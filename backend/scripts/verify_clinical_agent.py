"""
Verification script for Session 6 — Clinical Trials Worker Agent.

Tests ClinicalTrialsAgent execution end-to-end.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_clinical_agent.py

Checks:
  1. Initial AgentState constructed cleanly.
  2. Agent executes successfully for 'Metformin'.
  3. Domain objects (ClinicalDomain, ClinicalTrialRecord) properly populated.
  4. Active trials, completed trials, and phase distribution properties work.
  5. Agent executes successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') handled gracefully without crash.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.domain.agent_state import AgentState
from app.agents.clinical_agent import ClinicalTrialsAgent, run_clinical_agent

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
    print("MoleculeIQ — Session 6 Clinical Agent Verification")
    print("========================================\n")

    agent = ClinicalTrialsAgent()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_in = AgentState(molecule_name="Metformin")
    print(f"Sample AgentState BEFORE: {state_in}\n")

    t0 = time.monotonic()
    state_out = await agent.execute(state_in)
    elapsed = round(time.monotonic() - t0, 2)

    print(f"Sample AgentState AFTER: molecule_name='{state_out.molecule_name}', "
          f"clinical_trials={type(state_out.clinical_trials).__name__}, "
          f"errors_count={len(state_out.errors)}\n")

    check("Agent executed without throwing exception", True)
    check("state.clinical_trials is ClinicalDomain", state_out.clinical_trials is not None)

    if state_out.clinical_trials:
        domain = state_out.clinical_trials
        check("Domain molecule_name matches", domain.molecule_name == "Metformin")
        check("At least 1 trial record mapped", len(domain.trials) > 0, f"{len(domain.trials)} records")
        check("is_empty is False", not domain.is_empty)
        check("active_trials property works", isinstance(domain.active_trials, list), f"{len(domain.active_trials)} active")
        check("completed_trials property works", isinstance(domain.completed_trials, list), f"{len(domain.completed_trials)} completed")
        check("phase_distribution dict calculated", isinstance(domain.phase_distribution, dict), f"{domain.phase_distribution}")

        # Check fields of first mapped record
        first = domain.trials[0]
        check("Record has nct_id", first.nct_id.startswith("NCT"), first.nct_id)
        check("Record has title", len(first.title) > 0, first.title[:40] + "...")
        check("Record has status", len(first.status) > 0, first.status)

    check(f"Execution time", elapsed < 30, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using helper function entrypoint)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu = AgentState(molecule_name="Ibuprofen")
    t0 = time.monotonic()
    state_ibu_out = await run_clinical_agent(state_ibu)
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("Functional run_clinical_agent succeeded", True)
    check("state.clinical_trials is populated", state_ibu_out.clinical_trials is not None)
    if state_ibu_out.clinical_trials:
        check("Ibuprofen trials mapped", len(state_ibu_out.clinical_trials.trials) > 0, f"{len(state_ibu_out.clinical_trials.trials)} trials")

    check(f"Execution time", elapsed_ibu < 30, f"{elapsed_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Graceful empty handling)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 ]")
    state_unk = AgentState(molecule_name="UnknownMoleculeXYZ9999")
    t0 = time.monotonic()
    state_unk_out = await agent.execute(state_unk)
    elapsed_unk = round(time.monotonic() - t0, 2)

    check("Executed without throwing exception", True)
    check("state.clinical_trials is ClinicalDomain", state_unk_out.clinical_trials is not None)
    if state_unk_out.clinical_trials:
        check("is_empty is True", state_unk_out.clinical_trials.is_empty, "0 records")
        check("trials list is empty", len(state_unk_out.clinical_trials.trials) == 0)

    check(f"Execution time", elapsed_unk < 30, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 6 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    await agent._client.close()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
