# ADR-003: Real-Time Client Communication — Server-Sent Events (SSE)

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
Multi-agent research pipelines execute asynchronously over 15 to 60 seconds. The frontend user experience requires real-time progress updates (e.g., "Clinical Trials Agent: Completed", "Scoring Engine: Running...") rather than a blank loading screen or HTTP request timeout.

---

## Decision Drivers
- Lightweight, browser-native streaming capability.
- Unidirectional server-to-client progress updates.
- Low backend resource consumption (no persistent bi-directional state machine required).
- Compatibility with standard HTTP infrastructure and reverse proxies.

---

## Considered Options
1. **Server-Sent Events (SSE)** — *SELECTED*
2. **WebSockets**
3. **Short / Long HTTP Polling**

---

## Evaluation & Decision

### Option 1: Server-Sent Events (SSE) — ACCEPTED
* **Why:** SSE operates over standard HTTP (`text/event-stream`), natively supported in all modern web browsers via `EventSource` and in FastAPI via `EventSourceResponse`. It provides clean, unidirectional event streaming for progress updates and automatic client reconnection without extra protocol overhead.
* **Trade-offs:** Unidirectional only (server to client). (Sufficient for our request-response lifecycle).

### Option 2: WebSockets — REJECTED
* **Why Rejected:** WebSockets provide full-duplex bi-directional communication. However, MoleculeIQ requires only server-to-client updates after initial HTTP request submission. WebSockets add unnecessary connection management, heartbeat ping/pong maintenance, and complex stateful scaling overhead on the server.

### Option 3: Short / Long HTTP Polling — REJECTED
* **Why Rejected:** HTTP polling forces the client to send repeated HTTP GET requests every 1–2 seconds to check status, generating high HTTP overhead, server log noise, and database query load.

---

## Consequences
* **Positive:** Standard HTTP compatibility, zero socket management friction, native browser event parsing.
* **Negative:** Cannot send data from client to server over the SSE stream (client sends initial POST, server streams back).
