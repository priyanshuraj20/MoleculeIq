# ADR-006: Agent Paradigm — Static Domain Workers vs. Dynamic ReAct Tool Calling

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
In multi-agent systems, agents can either be implemented as **Dynamic ReAct Tool Callers** (an LLM equipped with tools deciding iteratively which tools to call in a loop) or **Static Domain Workers** (dedicated nodes running typed infrastructure calls with LLM context extraction).

---

## Decision Drivers
- Execution determinism and 100% data collection completeness.
- Response latency and token efficiency.
- Strict Pydantic data contract compliance.
- Interview defensibility against non-deterministic failure modes.

---

## Considered Options
1. **Static Domain Worker Nodes in Parallel DAG** — *SELECTED*
2. **Dynamic ReAct Tool-Calling Agent Loop**

---

## Evaluation & Decision

### Option 1: Static Domain Worker Nodes — ACCEPTED
* **Why:** In MoleculeIQ, every research query requires data from all 5 domains (clinical, literature, trade, market, patent). Implementing each domain worker as a static graph node executing typed infrastructure clients guarantees 100% execution coverage. It executes in parallel (`max(N1..N5)` time), eliminates tool-selection reasoning latency, and enforces exact Pydantic output contracts.

### Option 2: Dynamic ReAct Tool-Calling Agent Loop — REJECTED
* **Why Rejected:** Dynamic ReAct loops rely on an LLM to decide which tools to invoke sequentially. In practice, ReAct agents suffer from:
  1. **Skipped Tools:** The LLM may decide it has "enough information" after checking only 2 out of 5 sources.
  2. **Infinite Loops:** ReAct loops can get stuck calling the same search tool repeatedly.
  3. **High Latency:** Sequential tool calling takes `N1 + N2 + N3 + N4 + N5` seconds plus multi-turn LLM reasoning latency.

---

## Consequences
* **Positive:** Guaranteed 100% domain data collection, predictable latency, zero tool-skipping risk, robust technical interview defense.
* **Negative:** Adding a new tool requires adding a new graph node rather than exposing a function signature to a tool-calling LLM.
