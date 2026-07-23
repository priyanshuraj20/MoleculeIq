# ADR-002: Multi-Agent Orchestration — LangGraph Static Parallel DAG

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
MoleculeIQ gathers domain data across 5 distinct areas (clinical trials, scientific literature, trade data, market data, patent landscape). The orchestration system must trigger these domain queries in parallel, maintain state, aggregate results, and feed them into a scoring engine.

---

## Decision Drivers
- Support for parallel execution (fan-out / fan-in) to minimize latency.
- Explicit in-memory graph state persistence across node transitions.
- Per-node event streaming support for SSE progress updates.
- Deterministic execution flow (eliminating agent hallucinations during routing).

---

## Considered Options
1. **LangGraph with Static Parallel DAG** — *SELECTED*
2. **Dynamic LLM Orchestrator Router**
3. **Sequential LangChain Expression Language (LCEL)**
4. **Microsoft AutoGen / Conversational Framework**

---

## Evaluation & Decision

### Option 1: LangGraph with Static Parallel DAG — ACCEPTED
* **Why:** LangGraph provides cyclic and acyclic state machine graph capabilities. Defining a static parallel DAG guarantees that all 5 domain agents run concurrently for every query, reducing overall latency to the duration of the slowest API call. It provides clean node-level state isolation and progress event hooks.
* **Trade-offs:** Fixed graph topography; adding a new domain agent requires modifying the DAG definition.

### Option 2: Dynamic LLM Orchestrator Router — REJECTED
* **Why Rejected:** Calling an LLM router to decide *which* agents to run adds 3–5 seconds of latency and token cost per query. Because every molecule research report requires all 5 domain perspectives, dynamic routing adds unpredictability and routing failure modes without any domain benefit.

### Option 3: Sequential LangChain (LCEL) — REJECTED
* **Why Rejected:** Running 5 agents sequentially takes `N1 + N2 + N3 + N4 + N5` seconds (potentially 60–90s total). Parallel execution reduces latency to `max(N1..N5)` seconds (~15–30s total).

### Option 4: Microsoft AutoGen — REJECTED
* **Why Rejected:** AutoGen's conversational multi-agent paradigm relies on multi-turn text chat between agents. This pattern is non-deterministic, difficult to audit, prone to infinite loops, and unsuitable for structured data pipeline synthesis.

---

## Consequences
* **Positive:** Guaranteed 100% domain coverage per report, minimum execution latency through parallel fan-out, robust state management.
* **Negative:** Fixed graph structure requires code updates to add or remove worker nodes.
