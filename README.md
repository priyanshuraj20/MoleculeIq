# MoleculeIQ

### Pharmaceutical Research & Drug Repurposing Intelligence Platform

MoleculeIQ orchestrates specialized research agents across clinical trial registries, scientific literature, target-disease genetics, patent databases, and market intelligence to generate executive-grade research and drug repurposing dossiers.

## Project Overview

Traditional pharmaceutical research requires manually searching fragmented databases across clinical trials, scientific literature, target genetics, patent offices, and financial markets. MoleculeIQ unifies these workflows by deploying 5 specialized worker agents within a LangGraph execution graph to analyze pharmaceutical compounds, evaluate new repurposing indications, and synthesize multi-domain evidence into a deterministic Commercial Opportunity Score (0–100), executive summaries, PDF reports, and structured JSON exports.

## Key Features

### Multi-Agent Research Pipeline
- **Clinical Evidence Agent**: Queries ClinicalTrials.gov API v2 for study phases, recruitment status, and active trials.
- **Scientific Literature Agent**: Analyzes PubMed / Europe PMC publication volume and highly cited research papers.
- **Drug Repurposing Discovery Agent**: Discovers candidate new indications via Open Targets Platform GraphQL and ChEMBL. Filters out already-approved diseases using standardized disease ontology IDs (MONDO/EFO), ranks candidates by target-disease association scores, and cross-references real supporting evidence (ClinicalTrials.gov NCT IDs and PubMed PMIDs).
- **Patent Landscape Agent**: Reviews patent filings and status horizons (labeled with simulated provenance; legal conclusions such as "Free to Operate" are suppressed on simulated records).
- **Market Intelligence Agent**: Estimates commercial market size and 5-year CAGR (labeled with simulated provenance).

### Data Provenance & Honest Scoring
- **Transparent Provenance Labels**: Every domain carries an explicit provenance tag (`real`, `simulated`, or `unavailable`).
- **Normalized Opportunity Scoring**: Simulated components are excluded from the composite opportunity score; weights are renormalized across verified real sources (e.g., Clinical and Literature), with the UI explicitly indicating `"Based on 2 of 4 data sources"`.

### Workspace Navigation & Layout
- **Multi-Tab Workspace**: Information is organized into focused enterprise views:
  - **Executive Overview**: High-level Commercial Opportunity Score (0–100), 4 core domain metric cards, and synthesized executive preview.
  - **Agent Orchestration (DAG)**: Interactive LangGraph StateGraph execution graph, active agent node telemetry, endpoint inspection, latency metrics, and state mutation audit.
  - **Drug Repurposing Studio**: Candidate new indications discovered via target genetics (Open Targets + ChEMBL), mechanism hypothesis, association scoring, and cross-referenced citations.
  - **Clinical & Evidence Explorer**: Verified ClinicalTrials.gov studies table with direct registry links, scientific literature, data confidence breakdown, and chronological milestone timeline.
  - **Head-to-Head Compare**: Deterministic comparative benchmark studio evaluating differential clinical pipelines, literature citations, and market advantages between competing molecules.
  - **Medicine Suggestions**: Feasible manufactured drug formulations, delivery routes (oral, injectable, transdermal, nanoparticles), biological action mechanisms, and clinical/commercial advantages for the researched molecule.
  - **Session & Exports**: Session execution audit, one-click PDF dossier generation, and raw `AgentState` JSON download.
- **Smart Contextual Navigation**: Global, history-aware back navigation. Exiting comparison mode (`A vs B`) gracefully returns to primary compound `A` research state rather than resetting to the root home page, with tab states fully synchronized in the browser history.

### Medicine Formulation Discovery
- **Feasible Drug Formulations**: Analyzes chemical molecules to identify what real medications, modified-release forms (XR/ER), fixed-dose combinations (FDCs), and targeted delivery formulations can be manufactured.
- **Multi-Tiered Generation Engine**: Backed by curated benchmark pharmaceutical formulations, Google Gemini LLM formulation chemist prompts, and deterministic synthesis fallbacks.

### Performance & Security
- **Redis Caching**: Upstash Redis caching with 24-hour TTL (`moleculeiq:report:{compound}`) for instant cache hits.
- **Real-Time Progress Streaming**: Server-Sent Events (SSE) streaming live status updates during pipeline execution.
- **Drug & Brand Synonym Resolution**: Resolves brand names to generic entities (e.g., `Ozempic` to `Semaglutide`, `Keytruda` to `Pembrolizumab`).
- **Molecule Comparison Mode**: Side-by-side comparative analysis for competing drugs (e.g., `Metformin vs Semaglutide`).
- **Google OAuth 2.0 & Custom JWT**: Identity verification via Google OAuth and a backend-issued JWT set in an HttpOnly cookie.
- **Stateless Architecture**: No sensitive report data is persisted in the database; users download structured PDF or JSON exports on demand.

## System Architecture

```mermaid
graph TD
    A["React + Vite Frontend"] --> B["Google OAuth"]
    B --> C["FastAPI Backend"]
    C --> D["JWT Authentication"]
    D --> E["Supabase PostgreSQL"]
    D --> F["Research Orchestrator"]
    F --> G["Redis Cache"]
    G --> H{"Cache Hit?"}
    H -->|Yes| I["Return Cached Dossier"]
    H -->|No| J["LangGraph Pipeline"]
    J --> K["Clinical Trials Agent (ClinicalTrials.gov)"]
    J --> L["Scientific Literature Agent (Europe PMC)"]
    J --> M["Market Intelligence Agent"]
    J --> N["Patent Landscape Agent"]
    J --> O["Drug Repurposing Agent (Open Targets & ChEMBL)"]
    K --> P["Aggregation Service"]
    L --> P
    M --> P
    N --> P
    O --> P
    P --> Q["Honest Opportunity Scoring Engine"]
    Q --> R["Tabbed Frontend Workspace"]
    R --> S["PDF Report Export"]
    R --> T["JSON Data Export"]
```

### Research Pipeline Execution Flow

```mermaid
flowchart LR
    A["Research Query"] --> B["FastAPI Endpoint"]
    B --> C["Redis Cache"]
    C --> D{"Cache Hit?"}
    D -->|Yes| E["Return Cached Context"]
    D -->|No| F["LangGraph Workflow"]
    F --> G["1. Clinical Agent"]
    G --> H["2. Literature Agent"]
    H --> I["3. Market Agent"]
    I --> J["4. Patent Agent"]
    J --> K["5. Drug Repurposing Agent"]
    K --> L["Aggregation Service"]
    L --> M["Opportunity Scoring Engine"]
    M --> N["SSE Stream & JSON Payload"]
    N --> O["React Dashboard"]
```

## Authentication & Request Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant React as React Frontend
    participant Google as Google OAuth 2.0
    participant FastAPI as FastAPI Backend
    participant Supabase as Supabase PostgreSQL
    participant Redis as Upstash Redis
    User->>React: Click "Continue with Google"
    React->>Google: Open OAuth Popup
    Google-->>React: Return Google ID Token (Credential)
    React->>FastAPI: POST /api/auth/google
    FastAPI->>Google: Verify ID Token Signature
    FastAPI->>Supabase: Get or Insert User (Update last_login_at)
    Supabase-->>FastAPI: Return User Profile Record
    FastAPI-->>React: Set HttpOnly Cookie & Return Custom JWT
    User->>React: Submit Compound Query (e.g., "Pembrolizumab")
    React->>FastAPI: GET /api/v1/research/stream (Bearer JWT / Cookie)
    FastAPI->>Redis: Check Cache (moleculeiq:report:pembrolizumab)
    alt Cache Hit
        Redis-->>FastAPI: Return Cached ResearchContext
        FastAPI-->>React: Stream Final Event
    else Cache Miss
        FastAPI->>FastAPI: Execute LangGraph 5-Agent Pipeline
        FastAPI->>Redis: Store Result (24h TTL)
        FastAPI-->>React: Stream SSE Events & Final ResearchContext
    end
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn, LangGraph, Pydantic, ReportLab |
| Frontend | React 18, Vite, JavaScript, Tailwind CSS, Lucide Icons |
| Authentication | Google OAuth 2.0, PyJWT, HttpOnly Cookies |
| Database | Supabase PostgreSQL (`users` table) |
| Caching | Upstash Redis (24h TTL, TLS) |
| External APIs | ClinicalTrials.gov API v2, Europe PMC REST API, Open Targets Platform GraphQL, ChEMBL REST API |
| Streaming | Server-Sent Events (SSE) |

## Project Structure

```
MoleculeIQ/
├── backend/
│   ├── scripts/
│   │   └── create_users_table.sql      # Supabase PostgreSQL schema script
│   ├── src/
│   │   └── app/
│   │       ├── agents/                 # Clinical, Literature, Market, Patent, Repurposing agents
│   │       ├── api/                    # REST routes (/research, /auth, /stream, /medical-suggestion)
│   │       ├── auth/                   # JWT, Google OAuth service & dependencies
│   │       ├── core/                   # System settings & configuration
│   │       ├── domain/                 # Domain entities (Clinical, Repurposing, Score, Context)
│   │       ├── infrastructure/         # API clients (Open Targets, Europe PMC, ClinicalTrials), Redis & DB
│   │       ├── orchestrator/           # LangGraph research graph DAG & node definitions
│   │       └── services/               # Aggregation, Scoring, PDF, JSON & Comparison services
│   └── main.py
└── frontend/
    ├── src/
    │   ├── auth/                       # AuthContext, GoogleLoginButton & ProtectedRoute
    │   ├── components/                 # UI cards (RepurposingCard, OverviewCard, BackButton, ComparisonView)
    │   │   └── dashboard/              # Tab components (MedicineSuggestionsTab, RepurposingCard)
    │   ├── pages/                      # LandingPage, ResearchPage, ReportPage, MedicalSuggestionPage
    │   └── services/                   # SSE stream, Axios client & API fetch services
    └── package.json
```

## Environment Variables

### Backend (`backend/.env`)
```env
APP_NAME=MoleculeIQ API
APP_ENV=development
DEBUG=True
PORT=8000
HOST=0.0.0.0
# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
# Authentication & Security
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
JWT_SECRET_KEY=your-production-super-secret-jwt-key
JWT_EXPIRE_MINUTES=10080
# Database & Cache
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
REDIS_URL=rediss://default:your-upstash-token@your-instance.upstash.io:6379
REDIS_TTL_SECONDS=86400
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

## Getting Started

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000 --app-dir src
```

### 2. Database Setup
Run the SQL script located in `backend/scripts/create_users_table.sql` in your Supabase SQL Editor:
```sql
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    picture TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations for anon" ON public.users FOR ALL TO public USING (true) WITH CHECK (true);
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Visit `http://localhost:5173` in your browser.

## API Overview

| Method | Endpoint | Protection | Description |
|---|---|---|---|
| `POST` | `/api/auth/google` | Public | Authenticates Google ID Token & returns app JWT + HttpOnly cookie |
| `GET` | `/api/auth/me` | JWT | Returns current authenticated user profile |
| `POST` | `/api/auth/logout` | Public | Clears access_token HttpOnly cookie |
| `POST` | `/api/research` | JWT | Executes full research pipeline for a compound |
| `GET` | `/api/v1/research/stream` | JWT | SSE stream endpoint for real-time pipeline events |
| `POST` | `/api/v1/research/compare` | JWT | Executes parallel research and synthesizes side-by-side comparison report |
| `GET` | `/api/v1/medical-suggestion/` | Public | Retrieves feasible manufactured drug formulations and clinical suggestions for a target molecule |
| `POST` | `/api/research/json` | JWT | Generates downloadable JSON research export |
| `GET` | `/api/research/pdf` | JWT | Synthesizes executive PDF report |
| `GET` | `/health` | Public | Health check endpoint |

## License

Distributed under the MIT License.