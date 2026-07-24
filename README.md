# MoleculeIQ — Agentic AI Platform for Pharmaceutical Innovation Discovery

> **End-to-End AI System for Molecule Assessment, Market Research, Patent Landscape Analysis, and Drug Repurposing Reports.**

---

## 🚀 Project Overview

**MoleculeIQ** is an agentic AI platform engineered for pharmaceutical innovation discovery and drug repurposing. It automatically orchestrates specialized research agents across clinical trial registries, scientific literature, market intelligence databases, and patent landscapes to evaluate any pharmaceutical compound in seconds.

Rather than manually searching fragmented databases, MoleculeIQ synthesizes multi-domain evidence into a weighted **Commercial Opportunity Score (0–100)**, structured C-suite executive summaries, downloadable PDF reports, and standardized JSON exports.

---

## ✨ Features

- **Multi-Agent Orchestration**: LangGraph-powered orchestrator coordinating 4 specialized domain agents in parallel.
- **Upstash Redis Caching**: Configurable TTL cloud Redis caching layer over TLS with `moleculeiq:` key prefix (`moleculeiq:report:{canonical_molecule}`).
- **Dynamic Synonym & Brand Resolution**: Resolves brand names (e.g. `Ozempic` → `Semaglutide`, `Keytruda` → `Pembrolizumab`, `Mounjaro` → `Tirzepatide`) with PubChem PUG-REST dynamic fallback lookup.
- **Molecule Comparison Mode**: Parallel comparative evaluation for competing drug queries (e.g., `Metformin vs Semaglutide` or `Pembrolizumab vs Nivolumab`).
- **Four-Domain Intelligence**:
  - 🩺 **Clinical Evidence Agent**: ClinicalTrials.gov API v2 study phase, recruitment status, and sponsor tracking.
  - 📚 **Scientific Literature Agent**: Europe PMC publication volume and highly cited research paper analysis.
  - 📊 **Market Intelligence Agent**: Addressable market size (USD Mn), 5-year CAGR growth rate, and regional competitor footprints.
  - 🛡️ **Patent Landscape Agent**: Active patent filings, expiration horizons, and Freedom-To-Operate (FTO) indicators.
- **Hybrid Scoring Engine**: Multi-domain weighted scoring algorithm computing 0–100 commercial viability and data confidence ratings.
- **Real-Time Progress Streaming**: Server-Sent Events (SSE) streaming live agent checkmarks (`✓ Clinical Analysis Complete`, etc.) directly to the user interface.
- **C-Suite PDF & Structured JSON Export**: Production-grade C-suite PDF rendering and downstream API JSON exports.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18 (Vercel), Vite, JavaScript (ES6+), Vanilla CSS / Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI (Render), Uvicorn, LangGraph, Pydantic, HTTPX, ReportLab |
| **Caching & DB** | Upstash Redis (24h TTL, TLS), Supabase (PostgreSQL) + Local Repository Fallbacks |
| **Integrations** | ClinicalTrials.gov API v2, Europe PMC REST API, PubChem PUG-REST API |
| **Streaming** | Server-Sent Events (SSE) for real-time progress updates |

---

## 🏗️ System Architecture

```
                 React (Vercel)
                        │
                        ▼
              FastAPI (Render)
                        │
                 ResearchService
                        │
                  CacheService
                        │
                  Upstash Redis
                        │
             ┌──────────┴──────────┐
             │                     │
        Cache HIT            Cache MISS
             │                     │
      Return JSON          LangGraph Pipeline
                                  │
       ┌───────────────┬───────────────┼───────────────┐
       │               │               │               │
 Clinical Agent   Patent Agent   Literature Agent Market Agent
                                  │
                          Executive Summary
                                  │
                          Opportunity Score
                                  │
                          Final JSON Report
                                  │
                        Save to Redis (24h TTL)
                                  │
                          Return Response
```

---

## ⚙️ Installation & Running Locally

### 1. Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.11 or higher
- **pip**: v23.0+

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# (Linux/macOS)
# source venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables (`backend/.env`)
Copy `.env.example` to `.env` or set environment variables:
```env
REDIS_URL=rediss://default:your-upstash-token@your-instance.upstash.io:6379
REDIS_TTL_SECONDS=86400
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Run Backend Server
```bash
uvicorn app.main:app --reload --port 8000 --app-dir src
```
The API backend will start at `http://127.0.0.1:8000`.

### 5. Frontend Setup & Launch
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Build for production verification
npm run build

# Start Vite development server
npm run dev
```
Access the application UI in your browser at `http://localhost:5173`.

---

## 📁 Project Structure

```
MoleculeIQ/
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── agents/             # Worker agents (clinical, literature, market, patent)
│   │       ├── api/                # FastAPI endpoints & SSE stream handlers
│   │       ├── core/               # App configuration & settings
│   │       ├── domain/             # Typed Pydantic & dataclass domain models
│   │       ├── infrastructure/     # Upstash Redis client, API clients & Supabase repos
│   │       ├── orchestrator/       # LangGraph research graph & node definitions
│   │       └── services/           # CacheService, Scoring, Aggregation, Synonym & PDF services
│   └── scripts/                    # Verification & automated testing scripts
└── frontend/
    ├── src/
    │   ├── components/             # Minimal UI components & custom logos
    │   ├── hooks/                  # Custom React hooks (useResearch)
    │   ├── pages/                  # LandingPage & ResearchPage views
    │   └── services/               # API & SSE client integration
    └── package.json
```

---

## 🧪 Verification & Testing

To verify Upstash Redis caching, data quality, and multi-agent execution:
```bash
cd backend
# Test Upstash Redis caching & canonical key resolution
python scripts/verify_redis_cache.py

# Test Molecule Comparison Mode
python scripts/verify_comparison.py

# Test multi-molecule pipeline data quality
python scripts/verify_real_molecules.py
```

---

## 🔮 Future Improvements

- Expanded multi-language literature indexing.
- Direct chemical structure SMILES / MOL file parsing.
- Advanced target binding affinity scoring integrations.
