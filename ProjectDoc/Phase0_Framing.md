# MoleculeIQ — Phase 0: Product & Architectural Framing (Frozen)

> **Document Status:** FROZEN & APPROVED  
> **Role:** Principal Software Architect & Product Architect  
> **Target Audience:** Engineering Internship Reviewers, Technical Interviewers, R&D Stakeholders

---

## 1. Executive Summary & Product Vision

### 1.1 Product Vision
**MoleculeIQ** is a production-grade, multi-agent AI SaaS designed to automate early-stage pharmaceutical innovation and drug repurposing research. By orchestrating specialized autonomous AI agents across clinical registries, scientific literature, trade databases, market size records, and patent landscapes, MoleculeIQ transforms weeks of manual multi-silo research into a **30-second structured intelligence report** complete with explainable source citations, quantitative scoring, and multi-perspective AI debate.

### 1.2 The Core Problem
Pharmaceutical manufacturers (especially generic and specialty pharma companies) seek to expand into **Value-Added Generics (VAG)**, new formulations, and secondary therapeutic indications to combat revenue cliffs and generic price erosion. 

Currently, evaluating a single molecule candidate requires cross-functional teams to manually audit:
1. **Clinical Trial Registries** (Is anyone else testing this indication?)
2. **Scientific & Biomedical Literature** (Is there mechanistically sound evidence?)
3. **Patent & IP Registries** (What is the Freedom-to-Operate timeline?)
4. **Market & Sales Data** (What is the target addressable market size and CAGR?)
5. **Trade & EXIM Data** (Are raw active pharmaceutical ingredients [APIs] accessible?)

**Pain Point:** Analysts evaluate 50–100 candidate molecules per quarter. Manual synthesis across these 5 disparate data silos takes 2 to 4 weeks per molecule, creating an enormous strategic bottleneck and inconsistent evaluation criteria.

### 1.3 Finalized Problem Statement
> *"Pharma BD and Strategy teams lack a unified, rapid pre-diligence system to screen candidate molecules across clinical, scientific, market, IP, and trade data silos. MoleculeIQ solves this by providing a unified multi-agent intelligence pipeline that automatically gathers multi-domain evidence, scores opportunity vs. risk, provides transparent source citations, and generates executive-ready decision reports in seconds."*

---

## 2. Precursor Project Review & Architectural Evolution
*(Review of initial Sanjaya AI prototype / baseline blueprint)*

| Category | Component / Approach | Critical Architect Evaluation & Decision |
|---|---|---|
| **REMAIN UNCHANGED** | **Parallel Multi-Agent Fan-Out** | Keep LangGraph DAG fan-out pattern for domain agents (Clinical, Web, EXIM, Market, Patent). Parallel execution is mandatory for acceptable response latency. |
| **REMAIN UNCHANGED** | **Real Public APIs for Open Data** | Retain ClinicalTrials.gov REST v2 API, UN Comtrade API, and Europe PMC REST API. Using real APIs demonstrates real-world software engineering data integration skills. |
| **REMAIN UNCHANGED** | **Async Backend + SSE Streaming** | FastAPI backend returning Server-Sent Events (SSE) to React frontend. Ensures UI shows live agent state progression (e.g., "Querying ClinicalTrials API...") rather than blocking on a 30s synchronous call. |
| **IMPROVE** | **Master Orchestrator Routing** | **Old:** LLM router deciding which agents to run per query.<br>**New:** Static parallel execution DAG with dynamic per-agent sub-query formulation. Reduces unnecessary router LLM calls by 100%, lowers latency by ~3s, and eliminates routing failure modes. |
| **IMPROVE** | **Data Grounding & Explainability** | Enforce strict Pydantic schemas on all agent outputs containing explicit `source_uri`, `entity_id` (e.g., `NCT04561234`, `PMID:312984`), and LLM self-assessed confidence scores to prevent hallucination. |
| **REMOVE** | **LLM-Based PDF Report Generator Node** | **Old:** Treating PDF generation as an LLM agent node.<br>**New:** Replace with deterministic Python backend rendering service (ReportLab). LLM formats JSON; backend compiles PDF deterministically. Reduces token waste and formatting bugs. |
| **REMOVE / DEFER** | **Arbitrary PDF RAG Agent (MVP)** | Defer user PDF RAG to post-MVP. Arbitrary document chunking adds implementation noise without proving core multi-agent pharma aggregation logic. |
| **NEW ADDITION** | **Response Caching Layer** | Add Supabase/PostgreSQL query caching keyed by `(molecule_name, normalized_query)` with a TTL. Prevents API rate-limit exhaustion and accelerates repeated demo queries. |
| **NEW ADDITION** | **Deterministic Opportunity Scoring Engine** | Combine qualitative LLM reasoning with a deterministic scoring formula rather than relying 100% on raw LLM number generation. |

---

## 3. Target User Personas & Realism Validation

### 3.1 Primary Target Persona (Refined)
* **Role:** **Pharma Business Development (BD) & Portfolio Strategy Manager**
* **Primary Need:** Rapid screening and comparative scoring of 20–50 candidate molecules per month. Needs a clean executive dashboard, a score card, transparent risk callouts, and downloadable PDF reports for leadership reviews.
* **Secondary Persona:** R&D Innovation Lead / Licensing Analyst.

### 3.2 Realism & Scope Validation

#### Problem Statement Realism: **HIGH**
* In industry, early-stage triage is a real $M+ bottleneck. However, we explicitly scope MoleculeIQ as a **Pre-Diligence & Screening Tool**, not a legal freedom-to-operate guarantee.

#### Technical Scope Realism for Solo Developer: **ACHIEVABLE (with strict discipline)**
* **Timeline:** 3–4 Weeks.
* **Core Architecture:** 4-5 domain agents, 1 orchestrator, 1 scoring engine, 1 debate module, FastAPI, React/Vite, Supabase.
* **Cost:** ₹0 / $0 (Free tiers: Supabase PostgreSQL, Groq/Gemini APIs, public APIs).

#### Architecture Scalability: **HIGH**
* Stateless agent nodes in LangGraph running inside async FastAPI routes allow horizontal scaling. Caching reduces backend load. Plugging in real enterprise APIs (e.g., IQVIA MIDAS, USPTO Bulk Data) in the future requires modifying only individual agent tool functions, keeping the core graph structure untouched.

---

## 4. Finalized Product Scope & Deliverables

### 4.1 In-Scope Features (MVP v1.0)
1. **Interactive Intelligence Dashboard:** Chat-style input with real-time agent execution status indicators.
2. **Domain Agent Suite (5 Agents):**
   - **Clinical Trials Agent:** Real-time queries to ClinicalTrials.gov REST v2 API.
   - **Web & Literature Intelligence Agent:** Real-time scientific literature query via Europe PMC API.
   - **EXIM Trade Agent:** Trade volume data via UN Comtrade API.
   - **Market Intelligence Agent:** Market size, regional split, and CAGR via Supabase `iqvia_sales` mock dataset.
   - **Patent Landscape Agent:** Expiry timelines and freedom-to-operate status via Supabase `patents` mock dataset.
3. **AI Opportunity Scoring Engine:**
   - Innovation Score (0–100)
   - Commercial Attractiveness Score (0–100)
   - Patent Risk Rating (Low / Medium / High)
   - Clinical Risk Rating (Low / Medium / High)
4. **Explainability & Citation Engine:**
   - Grounded claim extraction with explicit source badges (`NCT ID`, `PMID`, `Comtrade Trade Flow`) and confidence scores.
5. **AI Debate Module (Bull vs. Bear):**
   - Autonomous two-sided evaluation ("Invest" case vs. "Do Not Invest" case) with Master Agent final verdict.
6. **Deterministic Executive PDF Report Export:**
   - Single-click PDF export generated via ReportLab summarizing scores, domain breakdowns, debate synthesis, and citations.

### 4.2 Out-of-Scope Features (Explicitly Excluded from MVP)
- Real IQVIA Subscription Integration (Replaced by representative mock schema).
- Full Freedom-to-Operate Legal Opinion Generation (Requires human legal counsel).
- Arbitrary User Document RAG (Deferred to Post-MVP).
- Multi-User Workspaces & Role-Based Access Control (RBAC).
- Portfolio-wide batch comparison across 100 molecules simultaneously (High API rate limit risk).

---

## 5. Success Criteria

### Technical Success Criteria
- **Execution Speed:** Complete end-to-end multi-agent pipeline execution in **< 35 seconds** for uncached queries; **< 1 second** for cached queries.
- **Reliability:** 100% structured JSON contract compliance across all LLM nodes using Pydantic/Instructor schemas (zero JSON parsing exceptions).
- **Graceful Degradation:** If an external public API (e.g. UN Comtrade) times out or fails, the graph must return partial domain results with a warning badge rather than crashing the request.
- **Explainability:** 100% of claims in the synthesized report must contain a clickable source citation badge.

### Interview & Portfolio Success Criteria
- Ability to explain every architectural decision out loud in under 2 minutes.
- Demonstrable production patterns: state management in LangGraph, parallel API fetching, async streaming, fallback mechanisms, and clean separation of concerns.

---

## 6. Assumptions & Risk Matrix

| Risk ID | Risk Description | Severity | Impact | Mitigation Strategy |
|---|---|---|---|---|
| **R-01** | External Public APIs (ClinicalTrials.gov, UN Comtrade) experience rate-limiting or latency spikes during live demo. | High | Pipeline hang / UI timeout | Wrap all API calls in strict 5-second timeouts with fallback mock data injectors and cache responses in Supabase. |
| **R-02** | LLM outputs non-deterministic or invalid JSON during scoring/debate steps. | Medium | Backend parsing crash | Enforce Pydantic validation via Instructor / structured outputs. Implement retry loops (max 2 retries). |
| **R-03** | Parallel execution exhausts Groq/Gemini free-tier TPM/RPM rate limits. | Medium | API 429 error | Implement rate-limit throttling in backend worker pool and batch parallel requests if needed. |
| **R-04** | Broad scope causes delay in frontend polish. | Medium | Unfinished UI | Complete backend & agent graph by Week 2, leaving Weeks 3 & 4 strictly for UI, debate, and PDF rendering. |

---

## 7. Open Architectural Questions for Approval

1. **Scoring Formula:** Should Opportunity Scoring be computed via 100% LLM prompt evaluation or a hybrid model (e.g., `Score = (Market_CAGR * 0.4) + (Clinical_Phase_Weight * 0.3) + (LLM_Qualitative_Score * 0.3)`)?  
   *Architect Recommendation:* Hybrid model for interview defensibility.
2. **Streaming Protocol:** Should we use Server-Sent Events (SSE) via FastAPI's `EventSourceResponse` or WebSockets?  
   *Architect Recommendation:* SSE. Unidirectional streaming from server to client is simpler to implement and debug for an HTTP request-response pipeline.

---
*End of Phase 0 Framing Document — Ready to Freeze Phase 0.*
