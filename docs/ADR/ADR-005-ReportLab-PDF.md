# ADR-005: Executive Document Generation — Decoupled On-Demand ReportLab Engine

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
MoleculeIQ allows users to download an executive summary PDF report. We must decide *when* and *how* PDF generation is triggered in the application lifecycle.

---

## Decision Drivers
- Fast initial research response time (minimizing SSE stream duration).
- Resource efficiency (avoid generating PDFs for users who only view the screen).
- Deterministic page formatting, table layout, and typography control.

---

## Considered Options
1. **Decoupled On-Demand ReportLab PDF Engine** (Triggered via POST `/api/v1/reports/pdf`) — *SELECTED*
2. **Synchronous In-Pipeline PDF Generation** (Generated during research graph execution)

---

## Evaluation & Decision

### Option 1: Decoupled On-Demand ReportLab PDF Engine — ACCEPTED
* **Why:** Research completion returns pure structured JSON over SSE directly to the UI for immediate rendering. PDF compilation occurs only when the user explicitly clicks "Download PDF". ReportLab compiles the document in < 500ms on demand, eliminating unnecessary backend work and providing an instant research UI loading experience.

### Option 2: Synchronous In-Pipeline PDF Generation — REJECTED
* **Why Rejected:** In-pipeline generation blocks the research SSE stream until PDF compilation finishes. If a user queries 10 molecules but downloads 0 PDFs, 100% of PDF generation work is wasted CPU cycles that degraded user response latency.

---

## Consequences
* **Positive:** Faster research pipeline response times, server resource efficiency, clean separation between data research APIs and document export APIs.
* **Negative:** Requires a dedicated HTTP POST route for PDF generation requests.
