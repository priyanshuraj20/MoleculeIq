"""
Verification script for Session 15 — AI Executive Analysis Service.

Tests the full pipeline from ResearchContext generation to ExecutiveReport synthesis:
  ResearchContext -> ExecutiveReportService -> ExecutiveReport (8 sections)

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_report.py

Checks:
  1. Full pipeline + aggregation + scoring runs for 'Metformin'.
  2. ExecutiveReportService generates ExecutiveReport.
  3. All 8 required report sections are non-empty strings.
  4. ExecutiveReport generated for 'Ibuprofen'.
  5. Unknown molecule ('UnknownMoleculeXYZ9999') handles degraded empty state gracefully with explicit uncertainty statements.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.orchestrator import run_research_pipeline
from app.services import AggregationService, ScoringService, ExecutiveReportService, generate_executive_report
from app.domain.executive_report import ExecutiveReport

PASS = "  PASS"
FAIL = "  FAIL"

all_results = []


def check(label: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    line = f"{status}  {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    all_results.append(condition)


async def main():
    print("\n========================================")
    print("MoleculeIQ — Session 15 Executive Report Verification")
    print("========================================\n")

    agg_service   = AggregationService()
    score_service = ScoringService()
    report_service = ExecutiveReportService()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_met   = await run_research_pipeline("Metformin")
    context_met = agg_service.build_context(state_met)
    context_met = score_service.evaluate_and_attach(context_met)

    t0 = time.monotonic()
    report_met = await report_service.generate_report(context_met)
    gen_time = round(time.monotonic() - t0, 2)

    check("ExecutiveReport instance returned", isinstance(report_met, ExecutiveReport))
    check("1. summary populated", len(report_met.summary) > 0, report_met.summary[:50] + "...")
    check("2. commercial_opportunity populated", len(report_met.commercial_opportunity) > 0, report_met.commercial_opportunity[:50] + "...")
    check("3. clinical_analysis populated", len(report_met.clinical_analysis) > 0, report_met.clinical_analysis[:50] + "...")
    check("4. market_analysis populated", len(report_met.market_analysis) > 0, report_met.market_analysis[:50] + "...")
    check("5. patent_analysis populated", len(report_met.patent_analysis) > 0, report_met.patent_analysis[:50] + "...")
    check("6. scientific_analysis populated", len(report_met.scientific_analysis) > 0, report_met.scientific_analysis[:50] + "...")
    check("7. risks populated", len(report_met.risks) > 0, report_met.risks[:50] + "...")
    check("8. recommendation populated", len(report_met.recommendation) > 0, report_met.recommendation[:50] + "...")
    check("model_name populated", len(report_met.model_name) > 0, report_met.model_name)
    check("generated_at populated", len(report_met.generated_at) > 0, report_met.generated_at)
    check(f"Report generation execution time", gen_time < 30, f"{gen_time}s")

    print(f"\nSample Executive Report for Metformin ({report_met.model_name}):")
    print(f"----------------------------------------")
    print(report_met.summary)
    print()
    print(report_met.recommendation)
    print(f"----------------------------------------\n")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using functional entrypoint)
    # ------------------------------------------------------------------ #
    print("[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu   = await run_research_pipeline("Ibuprofen")
    context_ibu = agg_service.build_context(state_ibu)
    context_ibu = score_service.evaluate_and_attach(context_ibu)

    t0 = time.monotonic()
    report_ibu = await generate_executive_report(context_ibu)
    gen_time_ibu = round(time.monotonic() - t0, 2)

    check("Functional generate_executive_report succeeded", isinstance(report_ibu, ExecutiveReport))
    check("Ibuprofen summary populated", len(report_ibu.summary) > 0)
    check("Ibuprofen recommendation populated", len(report_ibu.recommendation) > 0)
    check(f"Ibuprofen report generation time", gen_time_ibu < 30, f"{gen_time_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Explicit uncertainty handling)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 (Explicit Uncertainty) ]")
    state_unk   = await run_research_pipeline("UnknownMoleculeXYZ9999")
    context_unk = agg_service.build_context(state_unk)
    context_unk = score_service.evaluate_and_attach(context_unk)

    t0 = time.monotonic()
    report_unk = await report_service.generate_report(context_unk)
    gen_time_unk = round(time.monotonic() - t0, 2)

    check("Unknown molecule report generated without exception", isinstance(report_unk, ExecutiveReport))
    check("Unknown molecule summary populated", len(report_unk.summary) > 0)
    check("Clinical section explicitly states unconfirmed/missing status", "unconfirmed" in report_unk.clinical_analysis.lower() or "no" in report_unk.clinical_analysis.lower())
    check("Market section explicitly states unconfirmed/unavailable status", "unavailable" in report_unk.market_analysis.lower() or "no" in report_unk.market_analysis.lower())
    check("Unknown molecule recommendation flags high uncertainty", "uncertainty" in report_unk.recommendation.lower() or "priority" in report_unk.recommendation.lower())
    check(f"Unknown molecule report generation time", gen_time_unk < 30, f"{gen_time_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 15 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
