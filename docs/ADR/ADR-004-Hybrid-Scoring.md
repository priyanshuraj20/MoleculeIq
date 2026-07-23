# ADR-004: Opportunity Scoring Model — Hybrid Quantitative-Qualitative Engine

> **Status:** ACCEPTED  
> **Date:** 2026-07-23  
> **Deciders:** Principal Software Architect, Engineering Lead  

---

## Context and Problem Statement
MoleculeIQ evaluates candidate molecules to provide an Innovation Score, Commercial Score, and Risk Ratings. The scoring system must be auditable, repeatable, and interview-defensible.

---

## Decision Drivers
- High mathematical auditability and repeatability.
- Low vulnerability to LLM hallucinations or numeric drift.
- Qualitative context synthesis to explain *why* a score was given.

---

## Considered Options
1. **Hybrid Scoring Engine** (Deterministic Formula + LLM Qualitative Context) — *SELECTED*
2. **100% LLM Prompt-Based Scoring**

---

## Evaluation & Decision

### Option 1: Hybrid Scoring Engine — ACCEPTED
* **Why:** Baseline scores (e.g., Commercial Score) are calculated deterministically using a fixed formula based on market CAGR, market size, and clinical trial phase weights. The LLM is then used exclusively to analyze qualitative nuances (e.g., mechanistic fit, patent legal risks) and generate the textual explanation. This ensures numeric reproducibility while preserving qualitative AI synthesis.

### Option 2: 100% LLM Prompt-Based Scoring — REJECTED
* **Why Rejected:** Pure LLM scoring is non-deterministic and susceptible to temperature variations and prompt drift. The same molecule data could produce a score of 82 on one run and 65 on another. This fails technical interview defense and real-world pharma compliance standards.

---

## Consequences
* **Positive:** Mathematically auditable baseline scores, consistent numerical output across repeated runs, transparent qualitative AI reasoning.
* **Negative:** Requires defining and maintaining a deterministic mathematical scoring formula.
