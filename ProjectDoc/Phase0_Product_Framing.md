# MoleculeIQ — Phase 0: Product & Architectural Framing (Frozen)

> **Document Status:** FROZEN & APPROVED (Version 1.1)  
> **Role:** Principal Software Architect & Product Architect  
> **Target Audience:** Engineering Internship Reviewers, Technical Interviewers, R&D Strategy Stakeholders

---

## 1. Executive Summary & Product Vision

### 1.1 Product Vision
**MoleculeIQ** is a production-grade multi-agent AI SaaS designed to automate early-stage pharmaceutical innovation and drug repurposing research. By orchestrating specialized autonomous AI agents across clinical registries, scientific literature, trade databases, market size records, and patent landscapes, MoleculeIQ transforms weeks of manual multi-silo research into a **structured intelligence report**, typically completing within 1–2 minutes depending on external data source latencies. The platform features explainable source citations, quantitative opportunity/risk scoring, and an executive summary UI.

### 1.2 The Core Problem
Pharmaceutical manufacturers (specifically generic and specialty pharma companies) seek to expand into **Value-Added Generics (VAG)**, new formulations, and secondary therapeutic indications to combat revenue cliffs and generic price erosion.

Currently, evaluating a single molecule candidate requires cross-functional teams to manually audit:
1. **Clinical Trial Registries** (Is anyone else testing this indication?)
2. **Scientific & Biomedical Literature** (Is there mechanistically sound evidence?)
3. **Patent & IP Registries** (What is the Freedom-to-Operate timeline?)
4. **Market & Sales Data** (What is the target addressable market size and CAGR?)
5. **Trade & EXIM Data** (Are raw active pharmaceutical ingredients [APIs] accessible?)

**Pain Point:** Analysts evaluate 50–100 candidate molecules per quarter. Manual synthesis across these 5 disparate data silos takes 2 to 4 weeks per molecule, creating an enormous strategic bottleneck and inconsistent evaluation criteria.

### 1.3 Finalized Problem Statement
> *"Pharma BD and Strategy teams lack a unified, rapid pre-diligence system to screen candidate molecules across clinical, scientific, market, IP, and trade data silos. MoleculeIQ solves this by providing a unified multi-agent intelligence pipeline that automatically gathers multi-domain evidence, scores opportunity vs. risk, provides transparent source citations, and generates executive-ready decision reports."*

---

## 2. Precursor Project Review & Architectural Evolution
*(Review of baseline blueprint & architectural refinements)*

| Category | Component / Approach | Architectural Rationale & Decision |
|---|---|---|
| **REMAIN UNCHANGED** | **Parallel Multi-Agent Fan-Out** | Keep LangGraph DAG fan-out pattern for domain agents (Clinical, Web, EXIM, Market, Patent). Parallel execution is mandatory for acceptable throughput. |
| **REMAIN UNCHANGED** | **Real Public APIs for Open Data** | Retain ClinicalTrials.gov REST v2 API, UN Comtrade API, and Europe PMC REST API. Demonstrates authentic API integration and async data processing. |
| **REMAIN UNCHANGED** | **Async Backend + SSE Streaming** | FastAPI backend returning Server-Sent Events (SSE) to React frontend. Ensures UI shows live agent state progression without blocking on HTTP requests. |
| **IMPROVE** | **Orchestrator Routing** *(Renamed from Master Agent)* | **Old:** Dynamic LLM router deciding which agents to run per query.<br>**New:** Static parallel execution DAG with dynamic per-agent sub-query formulation. Reduces unnecessary router LLM calls by 100%, lowers latency, and eliminates routing failure modes. |
| **IMPROVE** | **Data Grounding & Explainability** | Enforce strict Pydantic schemas on all agent outputs containing explicit `source_uri`, `entity_id` (e.g., `NCT04561234`, `PMID:312984`), and confidence metrics to eliminate hallucinations. |
| **REMOVE** | **LLM-Based PDF Report Generator Node** | **Old:** Treating PDF generation as an LLM agent node.<br>**New:** Replace with deterministic Python backend rendering service (ReportLab). LLM formats structured JSON; backend compiles PDF deterministically. |
| **DEFER** | **AI Debate Module** | Move AI Debate (Bull vs. Bear agents) from MVP v1.0 to **v1.1**. Focus v1.0 100% on a bulletproof multi-domain research, scoring, and explainability pipeline first. |
| **DEFER** | **Arbitrary PDF RAG Agent & Caching** | Defer user PDF RAG and query caching to optimization phases (v1.1 / Phase 5). Core execution pipeline correctness comes first. |

---

## 3. Target User Personas & Realism Validation

### 3.1 Primary Target Persona (Refined)
* **Role:** **Pharma Business Development (BD) & Portfolio Strategy Manager**
* **Primary Need:** Rapid screening and comparative scoring of 20–50 candidate molecules per month. Needs a clean executive dashboard, a scorecard, transparent risk callouts, and downloadable PDF reports for leadership reviews.
* **Secondary Persona:** R&D Innovation Lead / Licensing Analyst.

### 3.2 Realism & Scope Validation

#### Problem Statement Realism: **HIGH**
* In industry, early-stage triage is a real $M+ bottleneck. However, we explicitly scope MoleculeIQ as a **Pre-Diligence & Screening Tool**, not a legal freedom-to-operate guarantee.

#### Technical Scope Realism for Solo Developer: **ACHIEVABLE (with strict discipline)**
* **Timeline:** 3–4 Weeks.
* **Core Architecture (v1.0):** 5 domain agents, 1 orchestrator, 1 scoring engine, FastAPI, React/Vite, Supabase.
* **Cost:** ₹0 / $0 (Free tiers: Supabase PostgreSQL, Groq/Gemini APIs, public APIs).

#### Architecture Scalability: **HIGH**
* Stateless agent nodes in LangGraph running inside async FastAPI routes allow horizontal scaling. Plugging in real enterprise APIs (e.g., IQVIA MIDAS, USPTO Bulk Data) in the future requires modifying only individual agent tool functions, keeping the core graph structure untouched.

---

## 4. Finalized Product Scope & Deliverables

### 4.1 In-Scope Features (MVP v1.0)
1. **Interactive Intelligence Dashboard:** Chat-style input with real-time agent execution status indicators via SSE.
2. **Domain Agent Suite (5 Agents):**
   - **Clinical Trials Agent:** Real-time queries to ClinicalTrials.gov REST v2 API.
   - **Web & Literature Intelligence Agent:** Real-time scientific literature query via Europe PMC API.
   - **EXIM Trade Agent:** Trade volume data via UN Comtrade API.
   - **Market Intelligence Agent:** Market size, regional split, and CAGR via Supabase `iqvia_sales` mock dataset.
   - **Patent Landscape Agent:** Expiry timelines and freedom-to-operate status via Supabase `patents` mock dataset.
3. **Opportunity Scoring Engine:**
   - Innovation Score (0–100)
   - Commercial Attractiveness Score (0–100)
   - Patent Risk Rating (Low / Medium / High)
   - Clinical Risk Rating (Low / Medium / High)
4. **Explainability & Citation Engine:**
   - Grounded claim extraction with explicit source badges (`NCT ID`, `PMID`, `Comtrade Trade Flow`) and confidence scores.
5. **Deterministic Executive PDF Report Export:**
   - Single-click PDF export generated via ReportLab summarizing scores, domain breakdowns, and citations.

### 4.2 Post-MVP Roadmap (v1.1 & Future)
- **v1.1:** AI Debate Module (Bull Agent vs. Bear Agent with Orchestrator verdict).
- **v1.1:** Query & Response Caching Layer in Supabase (optimization phase).
- **v1.2:** Arbitrary User Document RAG (Internal Knowledge Agent).
- **v1.2:** Real enterprise API plugins (IQVIA MIDAS, USPTO).

---

## 5. Success Criteria (Refined & Realistic)

### Core Functional Success Criteria
1. **Functional Correctness:** 100% of domain queries successfully query their respective APIs/data sources and produce valid, structured JSON output matching Pydantic schemas.
2. **Graceful Degradation:** If an external public API (e.g., UN Comtrade or ClinicalTrials.gov) experiences latency or times out, the orchestrator returns partial domain findings with a non-blocking UI warning badge.
3. **Grounding & Explainability:** 100% of claims rendered in the synthesis report contain verifiable source citation IDs (`NCT...`, `PMID...`, `Comtrade HS...`).
4. **Structured JSON Compliance:** Zero unhandled JSON parsing crashes between LLM output and backend API endpoints.

---

## 6. Assumptions & Risk Matrix

| Risk ID | Risk Description | Severity | Impact | Mitigation Strategy |
|---|---|---|---|---|
| **R-01** | External Public APIs (ClinicalTrials.gov, UN Comtrade) experience rate-limiting or latency spikes. | High | Latency / Timeout | Wrap all API calls in strict 5-second timeouts with fallback mock data injectors. |
| **R-02** | LLM outputs non-deterministic or invalid JSON during scoring steps. | Medium | Parsing crash | Enforce Pydantic validation via Instructor / structured outputs. Implement retry loops (max 2 retries). |
| **R-03** | Parallel execution exhausts Groq/Gemini free-tier rate limits. | Medium | API 429 error | Implement rate-limit throttling in backend worker pool. |
| **R-04** | Broad scope causes delay in frontend polish. | Medium | Unfinished UI | Focus v1.0 exclusively on 5 agents + scoring + PDF export. Defer AI Debate to v1.1. |

---

## 7. Next Steps: Architecture & ADR Roadmap

Phase 0 is frozen. We will structure the upcoming architecture and decision documentation under `docs/` as follows:

```
docs/
├── Phase0_Product_Framing.md       # (Frozen - This Document)
├── Phase1_System_Architecture.md   # (System Components, LangGraph DAG, Data Contracts)
└── ADR/
    ├── ADR-001-Why-LangGraph.md     # Orchestration Choice (LangGraph vs Autogen vs Sequential)
    ├── ADR-002-Why-SSE.md           # Streaming Protocol (SSE vs WebSockets vs Polling)
    ├── ADR-003-Why-FastAPI.md       # Async Backend Selection (FastAPI vs Express/Node)
    └── ADR-004-Hybrid-Scoring.md    # Scoring Model (Hybrid Deterministic + LLM vs Pure Prompt)
```

---
*Phase 0 Product Framing Document — 100% FROZEN & APPROVED.*
