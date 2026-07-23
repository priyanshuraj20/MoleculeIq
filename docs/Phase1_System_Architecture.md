# MoleculeIQ — Phase 1A: High-Level System Architecture Specification

> **Document Status:** REVISED & APPROVED (Phase 1A High-Level Architecture)  
> **Role:** Principal Software Architect  
> **Target Audience:** Core Engineering Team, Technical Reviewers, System Architects

---

## 1. Executive System Overview

MoleculeIQ is architected as an **asynchronous, event-driven multi-agent research pipeline** utilizing a layered software architecture. The platform decouples web UI presentation, API gateway routing, multi-agent graph orchestration, domain worker agents, external data integrations, domain data models, and on-demand report generation.

```
[ React / Vite Single Page Application ]
                   │
                   ▼ (HTTP POST / SSE Stream)
[ FastAPI API Gateway ]
                   │
                   ▼ (Async In-Memory Execution)
[ Orchestrator (LangGraph Static Parallel DAG) ]
         ┌─────────┼─────────┬─────────┬─────────┐
         ▼         ▼         ▼         ▼         ▼
      [Clinical] [WebLit] [Trade]  [Market]  [Patent]  (Worker Agents)
         │         │         │         │         │
         ▼         ▼         ▼         ▼         ▼
      [CT.gov]   [PMC]   [Comtrade] [SupaDB]  [SupaDB] (Infrastructure Clients)
         └─────────┴─────────┼─────────┴─────────┘
                             ▼
                 [ Aggregation Node ]
                             │
                             ▼
               [ Opportunity Scoring Engine ]
                             │
                             ▼ (Streaming JSON Payload Completed)
[ Client Presentation (Render Interactive Dashboard) ]

========================= ON-DEMAND FLOW =========================
[ User Clicks "Download PDF" ] ──> (POST /api/v1/reports/pdf)
                                          │
                                          ▼
                             [ Report Generation Service ]
                                          │
                                          ▼
                                   [ PDF Download ]
```

---

## 2. Component Topology & Responsibilities

### 2.1 Major System Components

| Component | Architecture Role | Key Responsibilities |
|---|---|---|
| **Frontend UI** | Presentation Layer | Renders chat interface, establishes SSE connection, displays real-time agent status indicators, renders interactive scorecard, and issues on-demand PDF generation requests. |
| **API Gateway (FastAPI)** | Interface / Boundary Layer | Validates incoming payloads, manages SSE event streams, delegates requests to Orchestrator, and exposes on-demand PDF export endpoints. Zero business logic. |
| **Orchestrator (`orchestrator/`)** | Workflow Controller | Manages LangGraph state machine, graph topology, state transitions, parallel fan-out/fan-in, and streaming event hooks. |
| **Worker Agents (`agents/`)** | Domain Processing Layer | Formulates domain queries, invokes infrastructure clients, validates responses, extracts citations/confidence, and populates domain state. |
| **Domain Layer (`domain/`)** | Business Model Core | Defines internal domain models (`molecule`, `trial`, `patent`, `market`, `report`). Decouples internal app logic from raw external API formats. |
| **Scoring Engine** | Synthesis Layer | Receives aggregated multi-agent state, executes hybrid quantitative-qualitative scoring algorithm, and produces structured risk ratings. |
| **Report Service** | On-Demand Document Engine | Accepts synthesized domain models **on demand** when requested by user, compiling PDF report via ReportLab without blocking research streaming. |
| **Infrastructure Layer** | External Adapters | Isolated subdirectories for external API HTTP clients (`clients/`), Supabase DB adapter (`database/`), and caching (`cache/`). |

---

## 3. Architectural Layer Boundaries

To enforce strict separation of concerns, the backend is organized into 5 distinct architectural layers:

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│     (Routers, SSE Controllers, Request/Response DTOs)   │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                    Service Layer                        │
│   (Pipeline Runner Service, On-Demand PDF Service)      │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                Orchestrator & Agent Layer               │
│   (orchestrator/ -> Graph & State | agents/ -> Domain)  │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                     Domain Layer                        │
│   (Internal Models: molecule, trial, patent, report)    │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                 Infrastructure Layer                    │
│   (clients/ -> APIs | database/ -> Supabase | cache/)   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Communication Protocols & Data Flow

### 4.1 Request Lifecycle (Decoupled On-Demand PDF Flow)

1. **Submission Phase:**
   - User inputs molecule query on React UI.
   - Client issues HTTP POST request to `/api/v1/research`.

2. **Stream & Research Phase:**
   - Gateway opens SSE stream (`text/event-stream`).
   - Orchestrator executes 5 worker agents in parallel (`Clinical`, `Literature`, `Trade`, `Market`, `Patent`).
   - As each node completes, status events stream to client in real-time.

3. **Scoring & Response Phase:**
   - Aggregation node compiles domain results into clean domain models.
   - Opportunity Scoring Engine calculates scores and qualitative risk assessments.
   - Gateway streams final synthesized JSON payload to client and closes SSE stream. **Research is now 100% complete.**

4. **On-Demand PDF Generation Phase (Asynchronous / Decoupled):**
   - User reviews dashboard and clicks "Export PDF".
   - Client issues HTTP POST request to `/api/v1/reports/pdf` with report JSON payload.
   - Report Service deterministically compiles PDF using ReportLab in < 500ms and returns downloadable binary file.

---

## 5. Architectural Decision Records (ADRs) Summary

| Decision ID | Choice | Why? | Alternative Considered | Why Rejected? |
|---|---|---|---|---|
| **ADR-001** | **FastAPI (Python)** | Native async concurrency, direct integration with Python AI (LangGraph) & ReportLab PDF ecosystem. | Node.js (Express) | Cross-process IPC overhead between Node.js and Python worker agents adds latency and deployment friction. |
| **ADR-002** | **LangGraph Static DAG** | Parallel fan-out execution minimizes latency to `max(N1..N5)` seconds; explicit state machine and streaming hooks per node. | Dynamic LLM Router | Adds 3–5s latency, token costs, and non-deterministic routing failure modes when all 5 domains are mandatory. |
| **ADR-003** | **Server-Sent Events (SSE)** | Lightweight, unidirectional HTTP streaming natively supported by browsers (`EventSource`) and FastAPI (`EventSourceResponse`). | WebSockets | Unnecessary stateful connection management on server for strictly server-to-client progress updates. |
| **ADR-004** | **Hybrid Scoring Engine** | Deterministic mathematical baseline scores + LLM qualitative synthesis ensures auditable, repeatable numbers. | 100% LLM Scoring | Pure LLM scoring is non-deterministic, hard to audit, and vulnerable to temperature drift across runs. |
| **ADR-005** | **Decoupled On-Demand PDF Engine** | ReportLab PDF generated **on demand** via separate endpoint; prevents blocking initial research response. | In-Pipeline Synchronous PDF | Synchronous PDF generation blocks the SSE research stream, wastes CPU for unviewed reports, and degrades UX. |
| **ADR-006** | **Static Domain Workers vs. Tool Calling** | Static deterministic worker nodes with structured output schemas guarantee execution completeness and data isolation. | Dynamic ReAct Tool Calling | Tool-calling loops can skip tools, loop infinitely, or fail to adhere to structured JSON contracts. |

---

## 6. High-Level Folder Structure Specification

```
backend/
└── src/
    └── app/
        ├── api/                 # HTTP Gateway Controllers, SSE Routers, DTOs
        ├── services/            # Pipeline Execution Service, On-Demand PDF Service
        ├── orchestrator/        # LangGraph Workflow Definition, State Schema, Graph Builder
        ├── agents/              # Domain Worker Agents (clinical, market, patent, trade, literature)
        ├── domain/              # Business Domain Models (molecule, trial, patent, market, report)
        ├── infrastructure/
        │   ├── clients/         # External API REST Clients (CT.gov, PMC, Comtrade)
        │   ├── database/        # Supabase DB Client & Query Repositories
        │   └── cache/           # Response Caching Utilities
        └── core/                # System Config, Logging, Exception Handlers
```

---

*End of Phase 1A High-Level System Architecture Specification — Ready for Phase 1B (Low-Level Design).*
