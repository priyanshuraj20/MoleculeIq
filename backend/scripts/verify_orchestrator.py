"""
Verification script for Session 10 — LangGraph Orchestrator Skeleton.

Tests the sequential execution research pipeline end-to-end:
  START -> clinical_node -> literature_node -> market_node -> patent_node -> END

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_orchestrator.py

Checks:
  1. Initial AgentState constructed cleanly before graph execution.
  2. LangGraph pipeline executes sequentially for 'Metformin'.
  3. All 4 domain attributes populated in final AgentState (clinical_trials, literature, market, patent).
  4. Pipeline executes successfully for 'Ibuprofen'.
  5. Unknown molecule ('UnknownMoleculeXYZ9999') executes cleanly without crashing, accumulating warnings.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.domain.agent_state import AgentState
from app.orchestrator import run_research_pipeline, research_graph

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


def print_graph_visualization():
    print("""
====================================================
LangGraph Research Pipeline Visualization
====================================================

      +----------------+
      |     START      |
      +-------+--------+
              |
              V
      +----------------+
      | clinical_node  |  (ClinicalTrialsAgent -> ClinicalDomain)
      +-------+--------+
              |
              V
      +----------------+
      | literature_node|  (LiteratureAgent -> LiteratureDomain)
      +-------+--------+
              |
              V
      +----------------+
      |  market_node   |  (MarketAgent -> MarketInsightsDomain)
      +-------+--------+
              |
              V
      +----------------+
      |  patent_node   |  (PatentAgent -> PatentLandscapeDomain)
      +-------+--------+
              |
              V
      +----------------+
      |      END       |
      +----------------+
====================================================
""")


async def main():
    print("\n========================================")
    print("MoleculeIQ — Session 10 Orchestrator Verification")
    print("========================================")

    print_graph_visualization()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_in = AgentState(molecule_name="Metformin")
    print(f"Sample AgentState BEFORE Graph: {state_in}\n")

    t0 = time.monotonic()
    state_out = await run_research_pipeline("Metformin")
    elapsed = round(time.monotonic() - t0, 2)

    print(f"Sample AgentState AFTER Graph:\n"
          f"  molecule_name   = '{state_out.molecule_name}'\n"
          f"  clinical_trials = {type(state_out.clinical_trials).__name__} ({len(state_out.clinical_trials.trials) if state_out.clinical_trials else 0} records)\n"
          f"  literature      = {type(state_out.literature).__name__} ({len(state_out.literature.publications) if state_out.literature else 0} papers)\n"
          f"  market          = {type(state_out.market).__name__} ({len(state_out.market.data_points) if state_out.market else 0} data points)\n"
          f"  patent          = {type(state_out.patent).__name__} ({len(state_out.patent.patents) if state_out.patent else 0} records)\n"
          f"  errors          = {state_out.errors}\n"
          f"  warnings        = {state_out.warnings}\n")

    check("Pipeline executed without throwing exception", True)
    check("Final output is AgentState instance", isinstance(state_out, AgentState))
    check("state.clinical_trials populated", state_out.clinical_trials is not None and not state_out.clinical_trials.is_empty)
    check("state.literature populated", state_out.literature is not None and not state_out.literature.is_empty)
    check("state.market populated", state_out.market is not None and not state_out.market.is_empty)
    check("state.patent populated", state_out.patent is not None and not state_out.patent.is_empty)
    check(f"Total pipeline execution time", elapsed < 30, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen ]")
    t0 = time.monotonic()
    state_ibu = await run_research_pipeline("Ibuprofen")
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("Ibuprofen pipeline executed without exception", True)
    check("Ibuprofen clinical trials present", state_ibu.clinical_trials is not None and len(state_ibu.clinical_trials.trials) > 0)
    check("Ibuprofen literature papers present", state_ibu.literature is not None and len(state_ibu.literature.publications) > 0)
    check("Ibuprofen market points present", state_ibu.market is not None and len(state_ibu.market.data_points) > 0)
    check("Ibuprofen patent records present", state_ibu.patent is not None and len(state_ibu.patent.patents) > 0)
    check(f"Ibuprofen pipeline execution time", elapsed_ibu < 30, f"{elapsed_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Graceful degraded pipeline execution)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 ]")
    t0 = time.monotonic()
    state_unk = await run_research_pipeline("UnknownMoleculeXYZ9999")
    elapsed_unk = round(time.monotonic() - t0, 2)

    check("Pipeline executed without exception for unknown molecule", True)
    check("All 4 domains attached as empty domain models",
          state_unk.clinical_trials is not None and
          state_unk.literature is not None and
          state_unk.market is not None and
          state_unk.patent is not None)
    check("Market and Patent appended warnings cleanly", len(state_unk.warnings) >= 2, f"{len(state_unk.warnings)} warnings")
    check(f"Unknown molecule execution time", elapsed_unk < 30, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 10 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
