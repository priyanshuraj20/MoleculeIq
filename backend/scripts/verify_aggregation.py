"""
Verification script for Session 11 — Research Aggregation Layer.

Tests the complete research workflow:
  AgentState (from LangGraph) -> AggregationService -> ResearchContext & ResearchMetadata

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_aggregation.py

Checks:
  1. LangGraph pipeline executes and returns AgentState.
  2. AggregationService constructs ResearchContext cleanly.
  3. All 4 domain models (clinical, literature, market, patent) attached to ResearchContext.
  4. Deterministic ResearchMetadata computed correctly (trials count, publications count, market regions, patent count).
  5. Pipeline & aggregation execute successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') handled gracefully, producing valid ResearchContext with empty domains and warnings.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.orchestrator import run_research_pipeline
from app.services.aggregation_service import AggregationService, build_research_context
from app.domain.research_context import ResearchContext, ResearchMetadata

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
    print("MoleculeIQ — Session 11 Aggregation Verification")
    print("========================================\n")

    service = AggregationService()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    t0 = time.monotonic()
    state = await run_research_pipeline("Metformin")
    pipeline_time = round(time.monotonic() - t0, 2)
    print(f"AgentState retrieved from LangGraph in {pipeline_time}s\n")

    t1 = time.monotonic()
    context = service.build_context(state)
    agg_time = round(time.monotonic() - t1, 2)

    print(f"Sample ResearchContext OUTPUT:\n"
          f"  molecule_name    = '{context.molecule_name}'\n"
          f"  created_at       = '{context.created_at}'\n"
          f"  pipeline_version = '{context.pipeline_version}'\n"
          f"  domains_attached = [clinical={context.clinical is not None}, literature={context.literature is not None}, market={context.market is not None}, patent={context.patent is not None}]\n"
          f"  metadata         = {context.metadata}\n"
          f"  errors_count     = {len(context.errors)}\n"
          f"  warnings_count   = {len(context.warnings)}\n")

    check("Aggregation executed without throwing exception", True)
    check("Output is ResearchContext instance", isinstance(context, ResearchContext))
    check("Context molecule_name matches", context.molecule_name == "Metformin")
    check("Clinical domain attached", context.clinical is not None and not context.clinical.is_empty)
    check("Literature domain attached", context.literature is not None and not context.literature.is_empty)
    check("Market domain attached", context.market is not None and not context.market.is_empty)
    check("Patent domain attached", context.patent is not None and not context.patent.is_empty)

    # Check Metadata
    meta = context.metadata
    check("Metadata is ResearchMetadata instance", isinstance(meta, ResearchMetadata))
    check("Metadata domains_available contains all 4 domains", len(meta.domains_available) == 4, f"{meta.domains_available}")
    check("Metadata total_trials > 0", meta.total_trials > 0, f"{meta.total_trials} total trials")
    check("Metadata active_trials_count > 0", meta.active_trials_count > 0, f"{meta.active_trials_count} active")
    check("Metadata total_publications > 0", meta.total_publications > 0, f"{meta.total_publications} total publications")
    check("Metadata highly_cited_papers_count > 0", meta.highly_cited_papers_count > 0, f"{meta.highly_cited_papers_count} highly cited")
    check("Metadata market_regions populated", len(meta.market_regions) > 0, f"{meta.market_regions}")
    check("Metadata global_market_size_usd_mn set", meta.global_market_size_usd_mn is not None, f"${meta.global_market_size_usd_mn}M")
    check("Metadata patent_count > 0", meta.patent_count > 0, f"{meta.patent_count} patents")
    check("Metadata fto_summary set", len(meta.fto_summary) > 0, meta.fto_summary)
    check(f"Aggregation execution time", agg_time < 2, f"{agg_time}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using functional entrypoint)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu = await run_research_pipeline("Ibuprofen")
    t1 = time.monotonic()
    context_ibu = build_research_context(state_ibu)
    agg_time_ibu = round(time.monotonic() - t1, 2)

    check("Functional build_research_context succeeded", True)
    check("Ibuprofen ResearchContext created", context_ibu.molecule_name == "Ibuprofen")
    check("Ibuprofen metadata total_trials > 0", context_ibu.metadata.total_trials > 0, f"{context_ibu.metadata.total_trials} trials")
    check("Ibuprofen metadata total_publications > 0", context_ibu.metadata.total_publications > 0, f"{context_ibu.metadata.total_publications} papers")
    check("Ibuprofen metadata patent_count > 0", context_ibu.metadata.patent_count > 0, f"{context_ibu.metadata.patent_count} patents")
    check(f"Ibuprofen aggregation execution time", agg_time_ibu < 2, f"{agg_time_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Graceful empty domain handling)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 ]")
    state_unk = await run_research_pipeline("UnknownMoleculeXYZ9999")
    t1 = time.monotonic()
    context_unk = service.build_context(state_unk)
    agg_time_unk = round(time.monotonic() - t1, 2)

    check("Executed without exception for unknown molecule", True)
    check("ResearchContext returned cleanly", isinstance(context_unk, ResearchContext))
    check("Metadata domains_available is empty list", len(context_unk.metadata.domains_available) == 0)
    check("Metadata total_trials is 0", context_unk.metadata.total_trials == 0)
    check("Warnings from AgentState propagated cleanly", len(context_unk.warnings) >= 2, f"{len(context_unk.warnings)} warnings")
    check(f"Unknown molecule aggregation execution time", agg_time_unk < 2, f"{agg_time_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 11 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
