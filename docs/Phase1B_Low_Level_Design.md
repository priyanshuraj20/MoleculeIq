# MoleculeIQ — Phase 1B: Low-Level Architecture & Design (LLD) Specification

> **Document Status:** PROPOSED (Phase 1B Low-Level Design)  
> **Role:** Principal Software Architect  
> **Target Audience:** Engineering Team, Backend Developers, System Reviewers

---

## 1. High-Level Design (HLD) Re-Cap & Phase 1B Scope

In Phase 1A, we locked down the high-level system architecture, layer boundaries, decoupled on-demand PDF generation, and ADR decisions. 

Phase 1B defines the **Low-Level Design (LLD)** specifications:
1. **Graph State Schema & Definitions**
2. **Agent Interfaces & Domain Contracts**
3. **API Data Transfer Objects (DTOs)**
4. **Module & Directory Responsibilities**
5. **Error Isolation & Graceful Degradation Strategy**
6. **Graph State Transition Lifecycle**

---

## 2. Graph State Schema (`AgentState`) Specification

The `AgentState` object is the single source of truth passed across all nodes in the LangGraph execution DAG.

### 2.1 State Keys & Field Definitions

| State Key | Data Type / Structure | Responsibility | Written By Node |
|---|---|---|---|
| `molecule_name` | String | Target molecule requested by user (e.g., "Metformin"). | API Gateway / Orchestrator |
| `target_indication` | Optional String | Specific medical indication or condition (if provided). | API Gateway / Orchestrator |
| `request_id` | UUID String | Unique identifier for trace logging and session tracking. | API Gateway |
| `clinical_trials` | Domain Object List (`TrialDomainModel`) | Aggregated clinical trial records from ClinicalTrials.gov. | `clinical_agent` node |
| `literature_articles` | Domain Object List (`LiteratureDomainModel`) | Aggregated journal & publication records from Europe PMC. | `literature_agent` node |
| `trade_data` | Domain Object (`TradeDomainModel`) | Import/export volume trends and API sourcing origins. | `trade_agent` node |
| `market_insights` | Domain Object (`MarketDomainModel`) | Market size, 5-year CAGR, and regional split. | `market_agent` node |
| `patent_landscape` | Domain Object (`PatentDomainModel`) | Patent expiry timeline and Freedom-to-Operate status. | `patent_agent` node |
| `scoring_results` | Domain Object (`ScorecardDomainModel`) | Innovation Score, Commercial Score, Risk Ratings, and reasoning. | `scoring_engine` node |
| `execution_logs` | List of State Log Objects | Array of step completion events streamed over SSE. | Orchestrator & All Nodes |
| `errors` | List of Error Warning Objects | Non-critical node warnings for UI degradation alerts. | Infrastructure Clients / Worker Nodes |

---

## 3. Agent Interfaces & Domain Specifications

Every worker agent in `app/agents/` implements a uniform execution contract:

```
Input: (shared AgentState, Infrastructure Client) ──> Agent Logic ──> Output: Partial AgentState Dictionary
```

### 3.1 Domain Worker Specifications

#### 1. Clinical Trials Agent (`agents/clinical.py`)
- **Infrastructure Client:** `infrastructure/clients/clinicaltrials_client.py`
- **Primary Method:** `fetch_trials_by_molecule(molecule_name)`
- **Output Key:** `AgentState.clinical_trials`
- **Fallback Rule:** If API times out or returns HTTP 5xx, return empty list `[]` and append warning to `AgentState.errors`.

#### 2. Literature Intelligence Agent (`agents/literature.py`)
- **Infrastructure Client:** `infrastructure/clients/europepmc_client.py`
- **Primary Method:** `search_literature(molecule_name, indication)`
- **Output Key:** `AgentState.literature_articles`
- **Fallback Rule:** If search fails, return fallback mock review articles with confidence score `0.50` and append warning.

#### 3. EXIM Trade Agent (`agents/trade.py`)
- **Infrastructure Client:** `infrastructure/clients/comtrade_client.py`
- **Primary Method:** `fetch_trade_flow(hs_code_or_molecule)`
- **Output Key:** `AgentState.trade_data`
- **Fallback Rule:** If UN Comtrade rate limit is hit (HTTP 429), return estimated trade dependency model marked with fallback badge.

#### 4. Market Insights Agent (`agents/market.py`)
- **Infrastructure Database:** `infrastructure/database/market_repository.py`
- **Primary Method:** `query_market_data(molecule_name)`
- **Output Key:** `AgentState.market_insights`
- **Data Source:** Supabase `iqvia_sales` mock table.

#### 5. Patent Landscape Agent (`agents/patent.py`)
- **Infrastructure Database:** `infrastructure/database/patent_repository.py`
- **Primary Method:** `query_patent_status(molecule_name)`
- **Output Key:** `AgentState.patent_landscape`
- **Data Source:** Supabase `patents` mock table.

---

## 4. API Data Transfer Objects (DTOs) Specification

Data Transfer Objects (DTOs) strictly isolate public API gateway contracts from internal domain models.

### 4.1 Request DTOs
1. **`ResearchRequestDTO`**
   - `molecule_name`: String (Required, 2–100 chars, sanitized)
   - `indication`: Optional String (Default: None)
   - `region`: Optional String (Default: "Global")

2. **`ReportExportDTO`**
   - `request_id`: UUID String
   - `synthesized_payload`: Complete JSON scorecard structure

### 4.2 Response & Streaming DTOs
1. **`SSEProgressEventDTO`**
   - `event`: String (`"node_start"` | `"node_complete"` | `"scoring_complete"` | `"research_complete"` | `"error"`)
   - `node`: String (e.g., `"clinical_agent"`)
   - `status`: String (`"PENDING"` | `"SUCCESS"` | `"WARNING"` | `"FAILED"`)
   - `timestamp`: ISO-8601 String

2. **`ResearchCompleteResponseDTO`**
   - `request_id`: UUID String
   - `molecule_name`: String
   - `scorecard`: Scorecard Object (Innovation Score, Commercial Score, Risks)
   - `domain_breakdown`: Object containing Clinical, Literature, Trade, Market, and Patent summaries
   - `citations`: Array of citation objects (`id`, `source`, `url`, `confidence`)

---

## 5. Error Isolation & Graceful Degradation Strategy

In a production multi-agent system, **one failing API must never crash the entire request**.

```
                   ┌─── [Clinical Agent] ──> SUCCESS
                   ├─── [Literature Agent] ──> SUCCESS
[ Orchestrator ] ──┼─── [Trade Agent] ───────> TIMEOUT / 429 ERROR
                   │                                │
                   │                                ▼
                   │                     (Inject Fallback + Warning)
                   ├─── [Market Agent] ─────> SUCCESS
                   └─── [Patent Agent] ─────> SUCCESS
                                │
                                ▼
         [ Aggregation Node Produces Partial Summary + Warning Badge ]
```

### Degradation Rules
1. **Timeout Threshold:** Every external API infrastructure client (`httpx`) enforces a strict **5-second request timeout**.
2. **Exception Containment:** Each agent node wraps client calls in a try-except block. Exceptions are logged to `AgentState.errors` rather than re-raised.
3. **Synthesis Flagging:** If an agent node degrades, the Aggregation Node flags that domain's UI component with a `"Data Source Unavailable — Estimated Metrics Displayed"` warning badge.

---

## 6. Graph State Transition Lifecycle

```
[State 0: INIT]
   │  (Molecule Query Injected)
   ▼
[State 1: FAN-OUT PARALLEL EXECUTION]
   ├── Node: clinical_agent     ──> Writes state.clinical_trials
   ├── Node: literature_agent   ──> Writes state.literature_articles
   ├── Node: trade_agent        ──> Writes state.trade_data
   ├── Node: market_agent       ──> Writes state.market_insights
   └── Node: patent_agent       ──> Writes state.patent_landscape
   │  (Wait for all 5 parallel nodes to join)
   ▼
[State 2: AGGREGATION & NORMALIZATION]
   │  (Cleans multi-agent state, validates citations)
   ▼
[State 3: HYBRID SCORING ENGINE]
   │  (Computes Scores & Writes state.scoring_results)
   ▼
[State 4: RESEARCH COMPLETE]
   │  (Emits Final JSON Payload to SSE Stream & Closes Connection)
   ▼
[State 5: ON-DEMAND PDF EXPORT] (Triggered asynchronously only if user requests PDF download)
```

---

*End of Phase 1B Low-Level Design (LLD) Specification — Ready for Architectural Freeze Review.*
