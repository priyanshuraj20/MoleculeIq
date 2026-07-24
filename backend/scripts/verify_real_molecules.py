"""
scripts/verify_real_molecules.py

Verifies data quality, synonym resolution, repository fallbacks,
and research reliability across target real pharmaceutical compounds.
"""

import sys
import os
import asyncio

# Ensure src/ directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.orchestrator.graph import run_research_pipeline
from app.services.aggregation_service import AggregationService
from app.services.scoring_service import ScoringService

TARGET_MOLECULES = [
    "Semaglutide",
    "Ozempic",
    "Wegovy",
    "Tirzepatide",
    "Mounjaro",
    "Pembrolizumab",
    "Keytruda",
    "Nivolumab",
    "Osimertinib",
    "Atorvastatin",
    "Empagliflozin",
    "Dapagliflozin",
    "Metformin",
    "Ibuprofen",
    "Aspirin",
    "Paracetamol",
    "helloworld"  # Invalid query test
]


async def run_verification():
    print("=" * 80, flush=True)
    print("MOLECULEIQ — MULTI-MOLECULE RESEARCH DATA QUALITY & RELIABILITY VERIFICATION", flush=True)
    print("=" * 80, flush=True)

    agg_service = AggregationService()
    scoring_service = ScoringService()

    success_count = 0
    total_count = len(TARGET_MOLECULES)

    for query in TARGET_MOLECULES:
        print(f"\n---> Testing Query: '{query}'", flush=True)
        try:
            state = await run_research_pipeline(query)
            context = agg_service.build_context(state)

            meta = context.metadata
            trials_n = len(context.clinical.trials) if context.clinical else 0
            pubs_n = len(context.literature.publications) if context.literature else 0
            market_sz = meta.global_market_size_usd_mn
            patents_n = meta.patent_count
            meaningful = meta.has_meaningful_evidence

            print(f"     Canonical Name: '{context.molecule_name}'", flush=True)
            print(f"     Domains Found: {meta.domains_available}", flush=True)
            print(f"     Clinical Trials: {trials_n}", flush=True)
            print(f"     Literature Papers: {pubs_n}", flush=True)
            print(f"     Market Size USD Mn: {market_sz}", flush=True)
            print(f"     Patents Count: {patents_n}", flush=True)
            print(f"     Meaningful Evidence: {meaningful}", flush=True)

            if meaningful:
                score = scoring_service.calculate(context)
                print(f"     Opportunity Score: {score.overall_score:.1f} / 100 (Confidence: {score.confidence_score:.0f}%)", flush=True)
                if query.lower() != "helloworld":
                    success_count += 1
            else:
                print("     Result: Pipeline correctly returned 'No Results Found'", flush=True)
                if query.lower() == "helloworld":
                    success_count += 1

        except Exception as exc:
            print(f"     FAILED with exception: {exc}", flush=True)

    print("\n" + "=" * 80, flush=True)
    print(f"VERIFICATION SUMMARY: {success_count}/{total_count} Passed Successfully", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    asyncio.run(run_verification())
