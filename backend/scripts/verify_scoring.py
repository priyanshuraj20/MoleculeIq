"""
Verification script for Session 12 — Hybrid Opportunity Scoring Engine.

Tests the full research & scoring workflow:
  AgentState -> AggregationService -> ResearchContext -> ScoringService -> OpportunityScore

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_scoring.py

Checks:
  1. Full pipeline + aggregation runs for 'Metformin'.
  2. ScoringService calculates OpportunityScore and attaches to context.score.
  3. All category sub-scores (market, clinical, patent, research, confidence) generated in 0-100 range.
  4. Explanatory breakdown populated with human-readable factors.
  5. Reproducibility test: identical input produces identical float scores down to 6 decimal places.
  6. Pipeline & scoring run for 'Ibuprofen'.
  7. Unknown molecule ('UnknownMoleculeXYZ9999') handles empty context cleanly with zero exceptions.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.orchestrator import run_research_pipeline
from app.services import AggregationService, ScoringService
from app.domain.opportunity_score import OpportunityScore, ScoreBreakdown

PASS = "  PASS"
FAIL = "  FAIL"

all_results = []


def check(label: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    line = f"{status}  {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    all_results.append(condition)


async def main():
    print("\n========================================")
    print("MoleculeIQ — Session 12 Opportunity Scoring Verification")
    print("========================================\n")

    agg_service = AggregationService()
    score_service = ScoringService()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_met = await run_research_pipeline("Metformin")
    context_met = agg_service.build_context(state_met)

    check("Context built before scoring", context_met.score is None)

    t0 = time.monotonic()
    context_met = score_service.evaluate_and_attach(context_met)
    score_time = round(time.monotonic() - t0, 3)

    check("context.score attached", context_met.score is not None)
    score = context_met.score

    if score:
        print(f"\nOpportunityScore Output for Metformin:\n"
              f"  Overall Score    = {score.overall_score:.1f} / 100.0\n"
              f"  Market Score     = {score.market_score:.1f} / 100.0\n"
              f"  Clinical Score   = {score.clinical_score:.1f} / 100.0\n"
              f"  Patent Score     = {score.patent_score:.1f} / 100.0\n"
              f"  Research Score   = {score.research_score:.1f} / 100.0\n"
              f"  Confidence Score = {score.confidence_score:.1f} / 100.0\n")

        print("Score Breakdown Explanations:")
        for line in score.score_breakdown.explanation:
            print(f"  • {line}")
        print()

        check("Overall score in 0-100 range", 0.0 <= score.overall_score <= 100.0, f"{score.overall_score}")
        check("Market sub-score in 0-100 range", 0.0 <= score.market_score <= 100.0, f"{score.market_score}")
        check("Clinical sub-score in 0-100 range", 0.0 <= score.clinical_score <= 100.0, f"{score.clinical_score}")
        check("Patent sub-score in 0-100 range", 0.0 <= score.patent_score <= 100.0, f"{score.patent_score}")
        check("Research sub-score in 0-100 range", 0.0 <= score.research_score <= 100.0, f"{score.research_score}")
        check("Confidence score in 0-100 range", 0.0 <= score.confidence_score <= 100.0, f"{score.confidence_score}")
        check("Explanations list populated", len(score.score_breakdown.explanation) > 0, f"{len(score.score_breakdown.explanation)} items")

    check(f"Scoring execution time", score_time < 0.5, f"{score_time}s")

    # ------------------------------------------------------------------ #
    # Test 2: Reproducibility Check (Exact same input -> Exact same output)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Reproducibility Check ]")
    score_run_1 = score_service.calculate(context_met)
    score_run_2 = score_service.calculate(context_met)

    check("Overall score is 100% reproducible", score_run_1.overall_score == score_run_2.overall_score, f"{score_run_1.overall_score} == {score_run_2.overall_score}")
    check("Market sub-score reproducible", score_run_1.market_score == score_run_2.market_score)
    check("Clinical sub-score reproducible", score_run_1.clinical_score == score_run_2.clinical_score)
    check("Patent sub-score reproducible", score_run_1.patent_score == score_run_2.patent_score)
    check("Research sub-score reproducible", score_run_1.research_score == score_run_2.research_score)
    check("Confidence score reproducible", score_run_1.confidence_score == score_run_2.confidence_score)

    # ------------------------------------------------------------------ #
    # Test 3: Ibuprofen
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: Ibuprofen ]")
    state_ibu = await run_research_pipeline("Ibuprofen")
    context_ibu = agg_service.build_context(state_ibu)
    context_ibu = score_service.evaluate_and_attach(context_ibu)

    check("Ibuprofen context.score attached", context_ibu.score is not None)
    if context_ibu.score:
        check("Ibuprofen overall score positive", context_ibu.score.overall_score > 0, f"{context_ibu.score.overall_score:.1f}")
        check("Ibuprofen confidence score positive", context_ibu.score.confidence_score > 0, f"{context_ibu.score.confidence_score:.1f}")

    # ------------------------------------------------------------------ #
    # Test 4: Unknown Molecule (Empty context scoring)
    # ------------------------------------------------------------------ #
    print("\n[ Test 4: UnknownMoleculeXYZ9999 (Empty context) ]")
    state_unk = await run_research_pipeline("UnknownMoleculeXYZ9999")
    context_unk = agg_service.build_context(state_unk)
    context_unk = score_service.evaluate_and_attach(context_unk)

    check("Scored empty context without exception", context_unk.score is not None)
    if context_unk.score:
        check("Confidence score is 0.0 for empty domains", context_unk.score.confidence_score == 0.0, f"Confidence: {context_unk.score.confidence_score}")
        check("Overall score calculated gracefully", 0.0 <= context_unk.score.overall_score <= 100.0, f"Overall: {context_unk.score.overall_score}")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 12 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
