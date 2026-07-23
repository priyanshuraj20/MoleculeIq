# MoleculeIQ — Execution Tracker
### Session-wise Build Log (Framing → Design → Implementation → Test)

> Rule for every session: **Understand first, then build, then test, then check the box.**
> Don't move to the next session's task until the current one is tested and you can explain *why* it works.

---

## How to Use This File

Every time you sit down to work in Antigravity:
1. Open this file, find the next unchecked task.
2. Before touching code, **explain the task to yourself in one sentence** (write it in the "Notes" line — this is how you build interview-readiness as you go).
3. Build it.
4. Test it (manually run it, see real output).
5. Check the box `[x]` and add a one-line note of what you learned or what broke.

This file becomes your own build diary — extremely useful when someone asks "walk me through how you built this."

---

## PHASE 0 — Framing (Do This First, No Code)

- [ ] Re-read `MoleculeIQ_Blueprint.md` fully, one sitting, no skipping.
  - Notes:
- [ ] Write, in your own words (3–4 sentences), what problem this solves and for whom.
  - Notes:
- [ ] Write, in your own words, what each of the 7 agents does and what data source it uses.
  - Notes:
- [ ] Sketch (on paper or in Antigravity) the architecture diagram from memory, then compare with the blueprint's mermaid diagram.
  - Notes:

**Milestone 0 complete when:** you can explain the whole system out loud, without looking at the document, in under 2 minutes.

---

## PHASE 1 — Environment & Skeleton Setup

- [ ] Create project folder structure (`backend/`, `frontend/`, `docs/`)
  - Notes:
- [ ] Set up Python virtual environment, install FastAPI + Uvicorn
  - Notes:
- [ ] Create a single test route `/health` that returns `{"status": "ok"}`, run it, confirm in browser/Postman
  - Notes:
- [ ] Set up React + Vite + Tailwind frontend, confirm default page loads at localhost
  - Notes:
- [ ] Connect frontend to backend `/health` route — display "Backend Connected ✅" on the page
  - Notes:

**Milestone 1 complete when:** frontend and backend are running together and talking to each other.

---

## PHASE 2 — Data Layer Setup

- [ ] Create free Supabase project, note down URL + anon key (store in `.env`, never commit it)
  - Notes:
- [ ] Create `iqvia_sales` table (mock market data) — insert 5–10 sample rows manually
  - Notes:
- [ ] Create `patents` table (mock patent data) — insert 5–10 sample rows manually
  - Notes:
- [ ] From backend, write a simple query that fetches rows from `iqvia_sales` and returns as JSON — test with Postman
  - Notes:
- [ ] Repeat for `patents` table
  - Notes:

**Milestone 2 complete when:** you can query both mock tables from your backend and see real JSON output.

---

## PHASE 3 — First Real Agent (Clinical Trials — easiest, free, no key)

- [ ] Read ClinicalTrials.gov API docs, manually test one query in browser/Postman first (before writing code)
  - Notes:
- [ ] Write a Python function that calls the API for a given molecule name and returns raw JSON
  - Notes:
- [ ] Parse the response into a clean structure (trial phase, sponsor, status)
  - Notes:
- [ ] Wrap this as a LangGraph node ("Clinical Trials Agent")
  - Notes:
- [ ] Test standalone: run just this one node with a hardcoded molecule name, confirm output
  - Notes:

**Milestone 3 complete when:** you have one fully working agent, end-to-end, tested with real data — this is your proof of concept.

---

## PHASE 4 — Remaining Worker Agents

- [ ] Market Insights Agent (queries `iqvia_sales` table)
  - Notes:
- [ ] Patent Landscape Agent (queries `patents` table)
  - Notes:
- [ ] EXIM Trade Agent (UN Comtrade API)
  - Notes:
- [ ] Web Intelligence Agent (Europe PMC API)
  - Notes:
- [ ] Test each agent standalone before wiring into orchestrator (do NOT skip individual testing)
  - Notes:

**Milestone 4 complete when:** all 5 agents work independently and return clean structured data.

---

## PHASE 5 — Master Agent Orchestration

- [ ] Design the LangGraph graph: Master Agent → parallel branches → all 5 worker agents → aggregation node
  - Notes:
- [ ] Implement task decomposition (Master Agent decides which agents to call based on the query)
  - Notes:
- [ ] Implement parallel execution, confirm all agents run and results come back together
  - Notes:
- [ ] Test full flow with a real molecule query end-to-end via API call
  - Notes:

**Milestone 5 complete when:** one API call triggers all agents and returns one combined JSON response.

---

## PHASE 6 — Differentiator Features

- [ ] Build Opportunity Scoring Engine (synthesis prompt → JSON score output)
  - Notes:
- [ ] Test scoring with 2–3 different molecules, sanity-check the outputs make sense
  - Notes:
- [ ] Add `source` + `confidence` fields to each agent's output (Explainability foundation)
  - Notes:
- [ ] Build AI Debate: Bull Agent node + Bear Agent node + Master verdict node
  - Notes:
- [ ] Test debate output — read it, does it actually make sense given the data?
  - Notes:

**Milestone 6 complete when:** a single query produces a score, source citations, and a debate verdict.

---

## PHASE 7 — Report Generation

- [ ] Install ReportLab, build a basic PDF template (title, sections, table)
  - Notes:
- [ ] Wire real synthesized data into the PDF generator
  - Notes:
- [ ] Add charts (matplotlib or similar) embedded into PDF
  - Notes:
- [ ] Test: generate a full PDF report from a real query, open it, check it looks legit
  - Notes:

**Milestone 7 complete when:** you can download a real, readable PDF report from a live query.

---

## PHASE 8 — Frontend Build-Out

- [ ] Chat-style input for molecule queries
  - Notes:
- [ ] Live agent status display (which agent is running, done, etc.)
  - Notes:
- [ ] Results display: scorecard, tables, charts
  - Notes:
- [ ] Explainability UI (source badges + confidence %)
  - Notes:
- [ ] Debate section UI (bull vs bear side by side, verdict at bottom)
  - Notes:
- [ ] Download button for PDF/Excel report
  - Notes:

**Milestone 8 complete when:** the full UI works end-to-end without touching Postman/backend directly.

---

## PHASE 9 — Testing & Demo Prep

- [ ] Run 4–5 different molecule queries end-to-end, note any bugs
  - Notes:
- [ ] Fix any broken agent/edge cases (e.g., molecule with no clinical trials found)
  - Notes:
- [ ] Write a 2-minute demo script (what you'll say while clicking through)
  - Notes:
- [ ] Practice explaining the architecture out loud, no notes
  - Notes:
- [ ] (Optional) Deploy frontend to Vercel + backend to Render/Railway free tier
  - Notes:

**Milestone 9 complete when:** you can demo the whole thing live, confidently, in under 5 minutes.

---

## Running Issues Log

*(Use this to track bugs/blockers as you hit them — helps you see patterns and also gives you real "hardest part" interview stories.)*

| Date | Issue | How I Solved It |
|---|---|---|
| | | |
| | | |

---

## Quick Status Snapshot

| Phase | Status |
|---|---|
| 0 — Framing | ✅ Done (Frozen in `Phase0_Product_Framing.md`) |
| 1 — System Architecture & LLD | ✅ Done (Frozen in `Phase1_System_Architecture.md` & `Phase1B_Low_Level_Design.md`) |
| 1.1 — Skeleton Setup | ✅ Done (FastAPI + Uvicorn + Health Check) |
| 1.2 — Frontend Bootstrap | ✅ Done (React + Vite + Tailwind + Axios + Backend Connectivity) |
| 2 — Data Layer & Infra Clients | ✅ Done (Supabase DB + 3 API Clients: ClinicalTrials, EuropePMC, Comtrade) |
| 3 — Worker Agents (Clinical, Literature, Market, Patent) | ✅ Done (Clinical, Literature, Market, Patent Agents + 88/88 checks passed) |
| 4 — Remaining Agents | ⬜ Not started |
| 4 — Orchestration | ✅ Done (LangGraph StateGraph + 4-Node Sequential Execution + 18/18 checks passed) |
| 5 — Research Aggregation | ✅ Done (AggregationService + ResearchContext + ResearchMetadata + 24/24 checks passed) |
| 6 — Opportunity Scoring | ✅ Done (ScoringService + OpportunityScore + ScoreBreakdown + 22/22 checks passed) |
| 7 — FastAPI Research API | ✅ Done (POST /api/research endpoint + full pipeline orchestration + 18/18 checks passed) |
| 8 — SSE Research Streaming | ✅ Done (GET /api/v1/research/stream endpoint + 12-event SSE stream + 18/18 checks passed) |
| 9 — Executive Analysis Service | ✅ Done (ExecutiveReportService + ExecutiveReport 8-section synthesis + 22/22 checks passed) |
| 10 — PDF Report Generation | ✅ Done (PDFReportService + ReportLab 9-section PDF report + 12/12 checks passed) |
| 6 — Differentiators | ⬜ Not started |
| 7 — Reports | ⬜ Not started |
| 8 — Frontend | ⬜ Not started |
| 9 — Testing & Demo | ⬜ Not started |

*(Update this table as you complete each phase: ⬜ → 🟡 in progress → ✅ done)*