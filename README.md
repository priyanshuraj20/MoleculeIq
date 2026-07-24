<div align="center">

# 🧬 MoleculeIQ

### AI-Powered Pharmaceutical Research Intelligence Platform

*Accelerating pharmaceutical innovation through autonomous AI research agents.*

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-FF6F00?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Upstash Redis](https://img.shields.io/badge/Upstash_Redis-Caching-00E676?style=flat-square&logo=redis&logoColor=white)](https://upstash.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![Google OAuth](https://img.shields.io/badge/Google_OAuth-2.0-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/identity)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

<p align="center">
  <b>MoleculeIQ</b> orchestrates specialized AI research agents across clinical trial registries, scientific literature, patent databases, and market intelligence to generate publication-grade executive drug repurposing reports in seconds.
</p>

<br />

<div align="center">

### 📸 Application Interface

| Google Authentication | Authenticated Workspace | Research Intelligence Dashboard |
| :---: | :---: | :---: |
| <img src="assets/landing-page.png" width="280" alt="Landing Page with Google Auth" /> | <img src="assets/profile-menu.png" width="280" alt="Profile Dropdown" /> | <img src="assets/research-report.png" width="280" alt="Research Results Dashboard" /> |

</div>

</div>

---

## 🎯 Project Overview

Traditional pharmaceutical research requires manually searching fragmented databases across clinical trials, scientific literature, patent offices, and financial markets. **MoleculeIQ** unifies these workflows by deploying 4 autonomous AI agents that analyze pharmaceutical compounds in parallel and synthesize multi-domain evidence into a deterministic **Commercial Opportunity Score (0–100)**, C-suite executive summaries, PDF exports, and structured JSON reports.

---

## ✨ Key Features

### 🤖 Autonomous Multi-Agent Intelligence
- **Clinical Evidence Agent**: Queries ClinicalTrials.gov API v2 for study phases, recruitment status, and active trials.
- **Scientific Literature Agent**: Analyzes PubMed / Europe PMC publication volume and highly cited research papers.
- **Patent Landscape Agent**: Reviews active patent filings, expiration horizons, and Freedom-To-Operate (FTO) indicators.
- **Market Intelligence Agent**: Calculates addressable market size (USD Mn), 5-year CAGR growth rate, and regional footprint.
- **Executive Synthesis & Scoring Agent**: Synthesizes cross-domain findings into a weighted 0–100 Commercial Opportunity Score and executive summary.

### ⚡ Production-Grade Performance
- **Upstash Redis Caching**: Cloud Redis caching with 24-hour TTL (`moleculeiq:report:{compound}`) for instant cache hits.
- **Real-Time Progress Streaming**: Server-Sent Events (SSE) streaming live status updates (`✓ Verified Clinical Analysis`, etc.).
- **Drug & Brand Synonym Resolution**: Auto-resolves brand names (e.g., `Ozempic` → `Semaglutide`, `Keytruda` → `Pembrolizumab`).
- **Molecule Comparison Mode**: Side-by-side comparative analysis for competing drugs (e.g., `Metformin vs Semaglutide`).

### 🔐 Enterprise Security & Export
- **Google OAuth 2.0 & Custom JWT**: Identity verification via Google OAuth and secure backend JWT issued in HttpOnly cookies.
- **Stateless Architecture**: Zero report data persistence in the database; user downloads structured PDF or JSON exports on demand.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User["React + Vite Frontend"] --> OAuth["Google OAuth 2.0"]
    OAuth --> Backend["FastAPI Backend"]
    Backend --> Auth["JWT Verification & HttpOnly Cookie"]
    Auth --> DB["Supabase PostgreSQL (Users Table Only)"]
    Auth --> Service["Research Service"]
    
    Service --> Cache["Upstash Redis Cache"]
    Cache -->|Cache Hit| ReturnCached["Return Cached Report Immediately"]
    Cache -->|Cache Miss| Graph["LangGraph Multi-Agent Pipeline"]
    
    Graph --> Agent1["🩺 Clinical Agent"]
    Graph --> Agent2["📚 Literature Agent"]
    Graph --> Agent3["🛡️ Patent Agent"]
    Graph --> Agent4["📊 Market Agent"]
    
    Agent1 --> Exec["Executive Summary Synthesizer"]
    Agent2 --> Exec
    Agent3 --> Exec
    Agent4 --> Exec
    
    Exec --> Score["Opportunity Score Engine (0-100)"]
    Score --> Output["Frontend Research Dashboard"]
    Output --> PDF["📄 C-Suite PDF Export"]
    Output --> JSON["📦 API JSON Export"]
```

### 🧠 AI Research Pipeline Workflow

```mermaid
flowchart LR
    Query["Research Query"] --> API["FastAPI"]
    API --> Redis{"Redis Cache"}
    
    Redis -->|Cache Hit| Return["Cached Report"]
    Redis -->|Cache Miss| LG["LangGraph Pipeline"]
    
    LG --> C["Clinical Agent"]
    LG --> L["Literature Agent"]
    LG --> P["Patent Agent"]
    LG --> M["Market Agent"]
    
    C --> Exec["Executive Summary"]
    L --> Exec
    P --> Exec
    M --> Exec
    
    Exec --> Score["Opportunity Score"]
    Score --> Report["Structured Research Report"]
    Report --> Exports["PDF & JSON Export"]
```

---

## 🔄 Authentication & Request Lifecycle

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

---

## ☁️ Deployment & Production Workflow

```mermaid
graph LR
    Dev["Developer"] --> GitHub["GitHub Repository"]
    GitHub --> Vercel["Vercel (Frontend Deployment)"]
    GitHub --> Render["Render (FastAPI Backend)"]
    
    Vercel --> Users["End Users"]
    Render --> Supabase["Supabase PostgreSQL"]
    Render --> Upstash["Upstash Redis Cache"]
    Render --> OAuth["Google OAuth 2.0"]
    Render --> LLM["Gemini AI Agents"]
```

---

## ⚙️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, JavaScript (ES6+), Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, LangGraph, Pydantic, ReportLab |
| **Authentication** | Google OAuth 2.0, PyJWT, HttpOnly Cookies |
| **Database** | Supabase PostgreSQL (`users` table only) |
| **Caching** | Upstash Redis (24h TTL, TLS) |
| **Data Sources** | ClinicalTrials.gov API v2, Europe PMC REST API, PubChem PUG-REST API |
| **Streaming** | Server-Sent Events (SSE) |

---

## 📂 Project Structure

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

---

## 🔑 Environment Variables

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

---

## 🚀 Getting Started

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
Run the SQL script located in `backend/scripts/create_users_table.sql` in your [Supabase SQL Editor](https://supabase.com/dashboard):

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

---

## 🌐 API Overview

| Method | Endpoint | Protection | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/google` | Public | Authenticates Google ID Token & returns app JWT + HttpOnly cookie |
| `GET` | `/api/auth/me` | JWT | Returns current authenticated user profile |
| `POST` | `/api/auth/logout` | Public | Clears access_token HttpOnly cookie |
| `POST` | `/api/research` | JWT | Executes full research pipeline for a compound |
| `GET` | `/api/v1/research/stream` | JWT | SSE stream endpoint for real-time pipeline events |
| `POST` | `/api/research/json` | JWT | Generates downloadable JSON research export |
| `GET` | `/api/research/pdf` | JWT | Synthesizes C-suite Executive PDF report |
| `GET` | `/health` | Public | Health check endpoint |

---

## 📄 License & Credits

This project is licensed under the **MIT License**.

Developed with ❤️ by **Priyanshu Raj** for Pharmaceutical Innovation Discovery.