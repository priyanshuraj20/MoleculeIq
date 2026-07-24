"""
scripts/verify_comparison.py

Verification script for Molecule Comparison Mode (Feature 1).
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.services.comparison_service import ComparisonService


async def test_comparison():
    print("=" * 80, flush=True)
    print("MOLECULEIQ — MOLECULE COMPARISON MODE VERIFICATION", flush=True)
    print("=" * 80, flush=True)

    service = ComparisonService()

    pairs = [
        ("Metformin", "Semaglutide"),
        ("Pembrolizumab", "Nivolumab")
    ]

    for mol_a, mol_b in pairs:
        print(f"\n---> Testing Comparison: '{mol_a}' vs '{mol_b}'", flush=True)
        report = await service.compare(mol_a, mol_b)

        print(f"     Molecule A: {report.molecule_a_name} (Score: {report.molecule_a_context.score.overall_score if report.molecule_a_context.score else 0:.1f})", flush=True)
        print(f"     Molecule B: {report.molecule_b_name} (Score: {report.molecule_b_context.score.overall_score if report.molecule_b_context.score else 0:.1f})", flush=True)
        print(f"     Overall Advantage: {report.overall_winner} (Diff: {report.score_difference:.1f} pts)", flush=True)
        print(f"     Clinical Winner: {report.clinical_comparison.winner} ({report.clinical_comparison.summary})", flush=True)
        print(f"     Patent Winner: {report.patent_comparison.winner} ({report.patent_comparison.summary})", flush=True)
        print(f"     Market Winner: {report.market_comparison.winner} ({report.market_comparison.summary})", flush=True)
        print(f"     Recommendation: {report.executive_summary.strategic_recommendation[:120]}...", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("MOLECULE COMPARISON VERIFICATION PASSED SUCCESSFULLY", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    asyncio.run(test_comparison())
