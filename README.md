# MoleculeIQ

### AI-Powered Pharmaceutical Research Intelligence Platform

MoleculeIQ orchestrates specialized research agents across clinical trial registries, scientific literature, patent databases, and market intelligence to generate executive-grade drug repurposing reports in seconds.

## Project Overview

Traditional pharmaceutical research requires manually searching fragmented databases across clinical trials, scientific literature, patent offices, and financial markets. MoleculeIQ unifies these workflows by deploying 4 autonomous agents that analyze pharmaceutical compounds in parallel and synthesize multi-domain evidence into a deterministic Commercial Opportunity Score (0–100), executive summaries, PDF exports, and structured JSON reports.

## Key Features

### Autonomous Multi-Agent Intelligence
- **Clinical Evidence Agent**: Queries ClinicalTrials.gov API v2 for study phases, recruitment status, and active trials
- **Scientific Literature Agent**: Analyzes PubMed / Europe PMC publication volume and highly cited research papers
- **Patent Landscape Agent**: Reviews active patent filings
- **Market Intelligence Agent**: Calculates addressable market size, 5-year CAGR growth rate
- **Executive Synthesis & Scoring Agent**: Synthesizes cross-domain findings into a weighted 0–100 Commercial Opportunity Score and executive summary

### Performance
- **Redis Caching**: Upstash Redis caching with 24-hour TTL (`moleculeiq:report:{compound}`) for instant cache hits
- **Real-Time Progress Streaming**: Server-Sent Events (SSE) streaming live status updates during pipeline execution
- **Drug & Brand Synonym Resolution**: Auto-resolves brand names (e.g., `Ozempic` → `Semaglutide`, `Keytruda` → `Pembrolizumab`)
- **Molecule Comparison Mode**: Side-by-side comparative analysis for competing drugs (e.g., `Metformin vs Semaglutide`)

### Security & Export
- **Google OAuth 2.0 & Custom JWT**: Identity verification via Google OAuth and a backend-issued JWT set in an HttpOnly cookie
- **Stateless Architecture**: No report data is persisted in the database; users download structured PDF or JSON exports on demand

## System Architecture

```mermaid
graph TD
    A["React + Vite"] --> B["Google OAuth"]
    B --> C["FastAPI Backend"]
    C --> D["JWT Authentication"]
    D --> E["Supabase PostgreSQL"]
    D --> F["Research Service"]
    F --> G["Redis Cache"]
    G --> H{"Cache Hit?"}
    H -->|Yes| I["Return Cached Report"]
    H -->|No| J["LangGraph"]
    J --> K["Clinical Agent"]
    J --> L["Literature Agent"]
    J --> M["Patent Agent"]
    J --> N["Market Agent"]
    K --> O["Executive Summary"]
    L --> O
    M --> O
    N --> O
    O --> P["Opportunity Score"]
    P --> Q["Frontend"]
    Q --> R["PDF Export"]
    Q --> S["JSON Export"]
```

### AI Research Pipeline

```mermaid
flowchart LR
    A["Research Query"] --> B["FastAPI"]
    B --> C["Redis Cache"]
    C --> D{"Cache Hit?"}
    D -->|Yes| E["Return Cached Report"]
    D -->|No| F["LangGraph Workflow"]
    F --> G["Clinical Trial Agent"]
    F --> H["Literature Agent"]
    F --> I["Patent Agent"]
    F --> J["Market Intelligence Agent"]
    G --> K["Executive Summary"]
    H --> K
    I --> K
    J --> K
    K --> L["Opportunity Score"]
    L --> M["Structured Research Report"]
    M --> N["Frontend"]
    N --> O["PDF Export"]
    N --> P["JSON Export"]
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
    User->>React: Submit Compound Query (e.g., "Semaglutide")
    React->>FastAPI: GET /api/v1/research/stream (Bearer JWT / Cookie)
    FastAPI->>Redis: Check Cache (moleculeiq:report:semaglutide)
    alt Cache Hit
        Redis-->>FastAPI: Return Cached ResearchContext
        FastAPI-->>React: Stream Final Event
    else Cache Miss
        FastAPI->>FastAPI: Execute LangGraph 4-Agent Pipeline
        FastAPI->>Redis: Store Result (24h TTL)
        FastAPI-->>React: Stream SSE Events & Final ResearchContext
    end
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn, LangGraph, Pydantic, ReportLab |
| Authentication | Google OAuth 2.0, PyJWT, HttpOnly Cookies |
| Database | Supabase PostgreSQL (`users` table only) |
| Caching | Upstash Redis (24h TTL, TLS) |
| Data Sources | ClinicalTrials.gov API v2, Europe PMC REST API, PubChem PUG-REST API |
| Streaming | Server-Sent Events (SSE) |

## Project Structure

```
MoleculeIQ/
├── backend/
│   ├── scripts/
│   │   └── create_users_table.sql      # Supabase PostgreSQL schema script
│   ├── src/
│   │   └── app/
│   │       ├── agents/                 # Clinical, Literature, Market & Patent agents
│   │       ├── api/                    # REST routes (/research, /auth, /stream)
│   │       ├── auth/                   # JWT, Google OAuth service & dependencies
│   │       ├── core/                   # System settings & configuration
│   │       ├── domain/                 # Pydantic & Dataclass domain entities
│   │       ├── infrastructure/         # Supabase client, Redis cache & API clients
│   │       ├── orchestrator/           # LangGraph research graph definition
│   │       └── services/               # Aggregation, Scoring, PDF & JSON services
│   └── main.py
└── frontend/
    ├── src/
    │   ├── auth/                       # AuthContext, GoogleLoginButton & ProtectedRoute
    │   ├── components/                 # UI cards, logo & navigation components
    │   ├── pages/                      # LandingPage, ResearchPage & ReportPage
    │   └── services/                   # SSE stream & API fetch services
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
| `POST` | `/api/research/json` | JWT | Generates downloadable JSON research export |
| `GET` | `/api/research/pdf` | JWT | Synthesizes executive PDF report |
| `GET` | `/health` | Public | Health check endpoint |

## License

Distributed under the MIT License.
