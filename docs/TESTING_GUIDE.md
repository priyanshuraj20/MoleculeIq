# MoleculeIQ — Complete Testing Guide

## Current System Status

| Component | Status |
|---|---|
| Backend (FastAPI) | ✅ Running on http://127.0.0.1:8000 |
| Frontend (React) | ✅ Running on http://localhost:5173 |
| Database tables | ⚠️ Run `supabase_schema.sql` in Supabase dashboard first |

---

## Step 0 — Prerequisites (Do This Once)

### Create the Backend Virtual Environment

```powershell
# Navigate to backend folder
cd c:\Desktop_Local\MoleculeIQ\backend

# Create a Python 3.12 virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt

# Confirm packages are installed
pip list
```

You should see: `fastapi`, `uvicorn`, `supabase`, `python-dotenv`, `pydantic`.

### Create the Frontend Environment

```powershell
# Navigate to frontend folder
cd c:\Desktop_Local\MoleculeIQ\frontend

# Install all npm packages
npm install
```

---

## Step 1 — Run the SQL in Supabase

This is a one-time setup. Do it before running `verify_db.py`.

1. Open https://supabase.com → your project
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Open `c:\Desktop_Local\MoleculeIQ\docs\supabase_schema.sql`
5. Paste the entire contents
6. Click **Run**

You should see: `Success. No rows returned.`

The SQL creates:
- `iqvia_sales` table with indexes and RLS policy
- `patents` table with indexes and RLS policy
- Sample data for: Metformin, Ibuprofen, Aspirin, Atorvastatin

---

## Step 2 — Start the Backend Server

```powershell
cd c:\Desktop_Local\MoleculeIQ\backend

# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Start FastAPI server
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

The `--reload` flag auto-restarts on any file save.

---

## Step 3 — Test the Backend Health Endpoint

### Option A — Browser
Open: http://127.0.0.1:8000/health

Expected: `{"status":"ok"}`

### Option B — Swagger UI (recommended)
Open: http://127.0.0.1:8000/docs

You should see the FastAPI interactive docs with the `/health` endpoint listed.

### Option C — curl (PowerShell)
```powershell
curl.exe -s http://127.0.0.1:8000/health
```

Expected: `{"status":"ok"}`

---

## Step 4 — Run the Database Verification Script

After running the SQL in Supabase:

```powershell
cd c:\Desktop_Local\MoleculeIQ\backend

# Make sure venv is active
.\venv\Scripts\Activate.ps1

# Run the verification script
.\venv\Scripts\python.exe scripts\verify_db.py
```

**Expected output (after SQL is run):**
```
========================================
MoleculeIQ — Session 4 Verification
========================================

[ Supabase Client ]
  PASS  Client initializes  (Client)

[ MarketRepository — Metformin ]
  PASS  Returns MarketInsightsDomain
  PASS  Has at least 1 data point  (7 rows)
  PASS  is_empty is False
  PASS  global_market_size_usd_mn set  ($5120.8M)
  PASS  latest_cagr set  (6.2%)
  PASS  molecule_name preserved

[ MarketRepository — unknown molecule ]
  PASS  Returns domain model (not error)
  PASS  is_empty is True
  PASS  global_market_size returns None

[ PatentRepository — Metformin ]
  PASS  Returns PatentLandscapeDomain
  PASS  Has at least 1 patent record  (7 records)
  PASS  is_empty is False
  PASS  active_patents list works  (3 active)
  PASS  expired_patents list works  (2 expired)
  PASS  fto_summary string set  (At Risk — 3 active patent constraint(s))
  PASS  molecule_name preserved
  PASS  expiry_date parsed as date object  (2041-09-30)

[ PatentRepository — unknown molecule ]
  PASS  Returns domain model (not error)
  PASS  is_empty is True
  PASS  fto_summary still returns string

========================================
Result: 15/15 checks passed
All checks passed. Session 4 complete.
========================================
```

**Current output (before SQL):**
Supabase client initializes but all data checks fail with `PGRST205 — table not found`.
This is expected and correct. Run the SQL to fix it.

---

## Step 5 — Start the Frontend

```powershell
cd c:\Desktop_Local\MoleculeIQ\frontend

# Start Vite dev server
npm run dev
```

**Expected output:**
```
  VITE v8.1.5  ready in 350 ms

  ➜  Local:   http://localhost:5173/
```

---

## Step 6 — Verify the Frontend in Browser

Open: http://localhost:5173

You should see:
- `MOLECULEIQ` in small caps
- `Startup Check` heading
- 🟢 Green dot with **Backend is reachable**
- `Last checked at [time]`
- `GET http://127.0.0.1:8000/health`

If you see 🔴 red dot: the backend is not running. Start it with Step 2 first.

---

## Quick Reference — All Commands at Once

Open **two separate PowerShell terminals**:

**Terminal 1 (Backend):**
```powershell
cd c:\Desktop_Local\MoleculeIQ\backend
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```powershell
cd c:\Desktop_Local\MoleculeIQ\frontend
npm run dev
```

**Terminal 3 (Database Verification — run once after SQL):**
```powershell
cd c:\Desktop_Local\MoleculeIQ\backend
.\venv\Scripts\python.exe scripts\verify_db.py
```

---

## What Each Server Does

| Server | URL | Purpose |
|---|---|---|
| FastAPI (Uvicorn) | http://127.0.0.1:8000 | Python backend — handles API requests |
| FastAPI Docs | http://127.0.0.1:8000/docs | Swagger UI to test endpoints interactively |
| React (Vite) | http://localhost:5173 | Frontend — what you open in the browser |

> The React frontend talks to the FastAPI backend. Both must be running at the same time.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | You ran uvicorn from wrong directory. `cd backend` first. |
| `ENOSPC` / disk full on npm install | Run `npm cache clean --force` in the frontend folder. |
| Supabase returns 0 rows | RLS policy is missing. Re-run the full `supabase_schema.sql`. |
| `PGRST205 — table not found` | Tables not created yet. Run `supabase_schema.sql` in SQL Editor. |
| Frontend shows 🔴 Backend Offline | Backend server is not running. Start it in a separate terminal. |
| `venv\Scripts\Activate.ps1 cannot be loaded` | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
