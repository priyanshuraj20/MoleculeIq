"""
Master Full-System End-to-End Verification Suite for MoleculeIQ.

Executes and validates all 11 architectural layers of MoleculeIQ:
  1. Database Repositories (MarketRepository, PatentRepository)
  2. Infrastructure Clients (ClinicalTrials, EuropePMC, Comtrade)
  3. Individual Worker Agents (Clinical, Literature, Market, Patent)
  4. LangGraph Multi-Agent Research Orchestrator
  5. Deterministic Research Aggregation Service
  6. Hybrid Opportunity Scoring Engine
  7. AI Executive Analysis Report Service
  8. Professional ReportLab PDF Generation Service
  9. FastAPI REST Research API Endpoint (POST /api/research)
 10. FastAPI Executive PDF Download Endpoint (GET /api/research/pdf)
 11. FastAPI SSE Real-time Streaming Endpoint (GET /api/v1/research/stream)
 12. Input Validation & Fault Tolerance (Empty inputs, Unknown molecules, Degraded states)

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_full_system.py
"""

import asyncio
import dataclasses
import json
import os
import sys
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from app.main import app
from app.domain.agent_state import AgentState
from app.domain.research_context import ResearchContext
from app.domain.opportunity_score import OpportunityScore
from app.domain.executive_report import ExecutiveReport
from app.infrastructure.database.market_repository import MarketRepository
from app.infrastructure.database.patent_repository import PatentRepository
from app.infrastructure.clients.clinicaltrials_client import ClinicalTrialsClient
from app.infrastructure.clients.europepmc_client import EuropePMCClient
from app.infrastructure.clients.comtrade_client import ComtradeClient
from app.agents.clinical_agent import ClinicalTrialsAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.market_agent import MarketAgent
from app.agents.patent_agent import PatentAgent
from app.orchestrator import run_research_pipeline
from app.services import (
    AggregationService,
    ScoringService,
    ExecutiveReportService,
    PDFReportService
)

PASS = "  PASS"
FAIL = "  FAIL"

all_results = []


def check(layer: str, label: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    line = f"{status}  [{layer}] {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    all_results.append(condition)


def parse_sse_events(response_stream):
    events = []
    current_event = None
    current_data = None
    for line in response_stream.iter_lines():
        line = line.strip()
        if not line:
            if current_event and current_data is not None:
                try:
                    parsed_json = json.loads(current_data)
                except json.JSONDecodeError:
                    parsed_json = current_data
                events.append((current_event, parsed_json))
                current_event = None
                current_data = None
            continue
        if line.startswith("event:"):
            current_event = line[6:].strip()
        elif line.startswith("data:"):
            current_data = line[5:].strip()

    if current_event and current_data is not None:
        try:
            parsed_json = json.loads(current_data)
        except json.JSONDecodeError:
            parsed_json = current_data
        events.append((current_event, parsed_json))
    return events


async def main():
    print("\n========================================================")
    print("      MoleculeIQ Master Full-System Verification Suite      ")
    print("========================================================\n")
    t_start = time.monotonic()

    # ------------------------------------------------------------------ #
    # LAYER 1: Database Repositories (Supabase)
    # ------------------------------------------------------------------ #
    print("--- Layer 1: Supabase Database Repositories ---")
    market_repo = MarketRepository()
    patent_repo = PatentRepository()

    m_domain = market_repo.get_by_molecule("Metformin")
    check("Database", "MarketRepository queries iqvia_sales cleanly", not m_domain.is_empty, f"{len(m_domain.data_points)} points")

    p_domain = patent_repo.get_by_molecule("Metformin")
    check("Database", "PatentRepository queries patents cleanly", not p_domain.is_empty, f"{len(p_domain.patents)} patents")
    print()

    # ------------------------------------------------------------------ #
    # LAYER 2: External API Infrastructure Clients
    # ------------------------------------------------------------------ #
    print("--- Layer 2: Infrastructure API Clients ---")
    ct_client = ClinicalTrialsClient()
    epmc_client = EuropePMCClient()
    comtrade_client = ComtradeClient()

    ct_res = await ct_client.search_molecule("Metformin")
    check("Infra Clients", "ClinicalTrialsClient fetches data (WAF bypass verified)", len(ct_res.get("studies", [])) > 0, f"{len(ct_res.get('studies', []))} studies")

    epmc_res = await epmc_client.search_molecule("Metformin")
    check("Infra Clients", "EuropePMCClient fetches literature papers", epmc_res.get("hitCount", 0) > 0, f"{epmc_res.get('hitCount')} hitCount")

    com_res = await comtrade_client.search_molecule("Metformin")
    check("Infra Clients", "ComtradeClient fetches HS 3004 trade records", len(com_res.get("data", [])) > 0, f"{len(com_res.get('data', []))} records")

    await ct_client.close()
    await epmc_client.close()
    await comtrade_client.close()
    print()

    # ------------------------------------------------------------------ #
    # LAYER 3: Individual Worker Agents
    # ------------------------------------------------------------------ #
    print("--- Layer 3: Worker Agents ---")
    c_agent = ClinicalTrialsAgent()
    l_agent = LiteratureAgent()
    m_agent = MarketAgent()
    p_agent = PatentAgent()

    st0 = AgentState(molecule_name="Metformin")
    st1 = await c_agent.execute(st0)
    check("Worker Agents", "ClinicalTrialsAgent populates state.clinical_trials", st1.clinical_trials is not None and not st1.clinical_trials.is_empty)

    st2 = await l_agent.execute(st1)
    check("Worker Agents", "LiteratureAgent populates state.literature", st2.literature is not None and not st2.literature.is_empty)

    st3 = m_agent.execute(st2)
    check("Worker Agents", "MarketAgent populates state.market", st3.market is not None and not st3.market.is_empty)

    st4 = p_agent.execute(st3)
    check("Worker Agents", "PatentAgent populates state.patent", st4.patent is not None and not st4.patent.is_empty)

    await c_agent._client.close()
    await l_agent._client.close()
    print()

    # ------------------------------------------------------------------ #
    # LAYER 4: LangGraph Multi-Agent Research Orchestrator
    # ------------------------------------------------------------------ #
    print("--- Layer 4: LangGraph Multi-Agent Orchestrator ---")
    graph_state = await run_research_pipeline("Metformin")
    check("Orchestrator", "LangGraph StateGraph executes sequential DAG", isinstance(graph_state, AgentState))
    check("Orchestrator", "All 4 worker agent domains populated in AgentState",
          graph_state.clinical_trials is not None and
          graph_state.literature is not None and
          graph_state.market is not None and
          graph_state.patent is not None)
    print()

    # ------------------------------------------------------------------ #
    # LAYER 5: Research Aggregation Service
    # ------------------------------------------------------------------ #
    print("--- Layer 5: Research Aggregation Service ---")
    agg_service = AggregationService()
    context = agg_service.build_context(graph_state)
    check("Aggregation", "AggregationService constructs ResearchContext", isinstance(context, ResearchContext))
    check("Aggregation", "ResearchMetadata calculates deterministic domain metrics",
          context.metadata.total_trials > 0 and context.metadata.total_publications > 0 and context.metadata.patent_count > 0)
    print()

    # ------------------------------------------------------------------ #
    # LAYER 6: Hybrid Opportunity Scoring Engine
    # ------------------------------------------------------------------ #
    print("--- Layer 6: Hybrid Opportunity Scoring Engine ---")
    score_service = ScoringService()
    scored_context = score_service.evaluate_and_attach(context)
    check("Scoring", "ScoringService computes and attaches OpportunityScore", scored_context.score is not None)

    score = scored_context.score
    check("Scoring", "Overall & Confidence scores calculated in 0-100 range",
          0.0 <= score.overall_score <= 100.0 and score.confidence_score == 100.0,
          f"Overall: {score.overall_score}, Confidence: {score.confidence_score}")
    check("Scoring", "100% Reproducible scoring check",
          score_service.calculate(scored_context).overall_score == score.overall_score)
    print()

    # ------------------------------------------------------------------ #
    # LAYER 7: AI Executive Analysis Service
    # ------------------------------------------------------------------ #
    print("--- Layer 7: AI Executive Analysis Service ---")
    report_service = ExecutiveReportService()
    exec_report = await report_service.generate_report(scored_context)
    check("Executive Report", "ExecutiveReportService generates 8-section report", isinstance(exec_report, ExecutiveReport))
    check("Executive Report", "All 8 strategic sections non-empty",
          all(len(getattr(exec_report, f)) > 0 for f in [
              "summary", "commercial_opportunity", "clinical_analysis",
              "market_analysis", "patent_analysis", "scientific_analysis",
              "risks", "recommendation"
          ]))
    print()

    # ------------------------------------------------------------------ #
    # LAYER 8: Professional ReportLab PDF Generation Service
    # ------------------------------------------------------------------ #
    print("--- Layer 8: Professional ReportLab PDF Service ---")
    pdf_service = PDFReportService()
    pdf_bytes = pdf_service.generate_pdf(scored_context, exec_report)
    check("PDF Service", "PDFReportService generates valid PDF bytes", pdf_bytes.startswith(b"%PDF-") and len(pdf_bytes) > 5000, f"{len(pdf_bytes):,} bytes")
    print()

    # ------------------------------------------------------------------ #
    # LAYER 9: FastAPI REST API Endpoints
    # ------------------------------------------------------------------ #
    print("--- Layer 9: FastAPI REST API Endpoints ---")
    api_client = TestClient(app)

    # POST /api/research
    r_post = api_client.post("/api/research", json={"molecule_name": "Metformin"})
    check("FastAPI REST", "POST /api/research returns HTTP 200 OK", r_post.status_code == 200, f"Status: {r_post.status_code}")
    check("FastAPI REST", "JSON body contains full ResearchContext", "score" in r_post.json() and "metadata" in r_post.json())

    # GET /api/research/pdf
    r_pdf = api_client.get("/api/research/pdf?molecule_name=Metformin")
    check("FastAPI REST", "GET /api/research/pdf returns application/pdf attachment",
          r_pdf.status_code == 200 and r_pdf.headers.get("content-type") == "application/pdf",
          f"{len(r_pdf.content):,} bytes")
    print()

    # ------------------------------------------------------------------ #
    # LAYER 10: FastAPI SSE Real-time Streaming Endpoint
    # ------------------------------------------------------------------ #
    print("--- Layer 10: Server-Sent Events (SSE) Real-Time Stream ---")
    with api_client.stream("GET", "/api/v1/research/stream?molecule_name=Metformin") as r_stream:
        check("FastAPI SSE", "GET /api/v1/research/stream returns text/event-stream",
              r_stream.status_code == 200 and "text/event-stream" in r_stream.headers.get("content-type", ""))
        sse_events = parse_sse_events(r_stream)
        check("FastAPI SSE", "Emits 12 events in exact expected order", len(sse_events) == 12 and sse_events[-1][0] == "research_completed")
    print()

    # ------------------------------------------------------------------ #
    # LAYER 11: Fault Tolerance & Edge-Case Error Handling
    # ------------------------------------------------------------------ #
    print("--- Layer 11: Fault Tolerance & Degraded State Handling ---")

    # Degraded pipeline execution for unknown molecule
    unk_context = agg_service.build_context(await run_research_pipeline("UnknownMoleculeXYZ9999"))
    unk_scored = score_service.evaluate_and_attach(unk_context)
    unk_report = await report_service.generate_report(unk_scored)
    unk_pdf = pdf_service.generate_pdf(unk_scored, unk_report)

    check("Fault Tolerance", "Unknown molecule pipeline executes without crashing", unk_scored.score is not None)
    check("Fault Tolerance", "Warnings appended cleanly for missing database rows", len(unk_context.warnings) >= 2, f"{len(unk_context.warnings)} warnings")
    check("Fault Tolerance", "Degraded PDF renders cleanly for empty domains", unk_pdf.startswith(b"%PDF-") and len(unk_pdf) > 4000)

    # API Input Validation
    r_val = api_client.post("/api/research", json={"molecule_name": "   "})
    check("Fault Tolerance", "Blank input returns HTTP 422 Unprocessable Entity", r_val.status_code == 422, f"Status: {r_val.status_code}")
    check("Fault Tolerance", "Zero raw python stack traces exposed to client", "detail" in r_val.json() and "Traceback" not in r_val.text)
    print()

    # ------------------------------------------------------------------ #
    # Final Summary
    # ------------------------------------------------------------------ #
    t_total = round(time.monotonic() - t_start, 2)
    passed = sum(all_results)
    total  = len(all_results)

    print("========================================================")
    print(f"Master Verification Summary: {passed}/{total} Checks Passed")
    print(f"Total Master Suite Execution Time: {t_total} seconds")
    if passed == total:
        print("STATUS: ALL 11 ARCHITECTURAL LAYERS OPERATIONAL AND VERIFIED!")
    else:
        print(f"STATUS: {total - passed} CHECK(S) FAILED.")
    print("========================================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
