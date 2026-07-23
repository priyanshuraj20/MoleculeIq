# ADR-001: Backend Framework Selection — FastAPI

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
MoleculeIQ requires a high-performance backend API gateway capable of managing asynchronous multi-agent LLM workflows, external HTTP REST requests, and long-lived Server-Sent Events (SSE) streaming connections to the React frontend.

---

## Decision Drivers
- Native async/await event loop support.
- Native SSE event streaming capability over standard HTTP.
- Direct integration with Python AI/ML and PDF generation ecosystem (LangGraph, Pydantic, ReportLab).
- Automatic OpenAPI documentation and strict request validation.

---

## Considered Options
1. **FastAPI (Python 3.11+)** — *SELECTED*
2. **Express.js / NestJS (Node.js)**
3. **Flask / Django (Python)**

---

## Evaluation & Decision

### Option 1: FastAPI (Python 3.11+) — ACCEPTED
* **Why:** FastAPI is built natively on Starlette and Pydantic, offering exceptional async concurrency for non-blocking API calls. Python is the primary language of the AI orchestration ecosystem (LangGraph). Using FastAPI allows backend controllers, agent workflows, and report generation to run in a single, high-performance Python environment.
* **Trade-offs:** CPU-bound heavy computations (like complex PDF rendering or large vector operations) must be carefully offloaded to thread pools to avoid blocking the main event loop.

### Option 2: Express.js / NestJS (Node.js) — REJECTED
* **Why Rejected:** Node.js handles async I/O well, but requires cross-process IPC (Inter-Process Communication) or microservice overhead to invoke Python-based AI orchestration (LangGraph) and Python PDF libraries (ReportLab). This adds unnecessary latency, complexity, and deployment overhead.

### Option 3: Flask / Django (Python) — REJECTED
* **Why Rejected:** Flask and traditional Django are historically synchronous frameworks. While Django now supports ASGI, its ORM and framework overhead are bloated for an asynchronous API gateway. Flask requires external extensions (gevent/gunicorn) for streaming responses, adding maintenance friction.

---

## Consequences
* **Positive:** Single unified codebase in Python, clean async SSE streaming, native Pydantic validation, seamless LangGraph execution.
* **Negative:** CPU-heavy tasks must be handled asynchronously via thread executor pools.
