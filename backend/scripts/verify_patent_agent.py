"""
Verification script for Session 9 — Patent Landscape Worker Agent.

Tests PatentAgent execution end-to-end against Supabase database.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_patent_agent.py

Checks:
  1. Initial AgentState constructed cleanly.
  2. Agent executes successfully for 'Metformin'.
  3. Domain objects (PatentLandscapeDomain, PatentRecord) properly populated.
  4. active_patents, expired_patents, at_risk_patents, and fto_summary properties work.
  5. Agent executes successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') handled gracefully with warning appended.
"""

import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.domain.agent_state import AgentState
from app.agents.patent_agent import PatentAgent, run_patent_agent

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


def main():
    print("\n========================================")
    print("MoleculeIQ — Session 9 Patent Agent Verification")
    print("========================================\n")

    agent = PatentAgent()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_in = AgentState(molecule_name="Metformin")
    print(f"Sample AgentState BEFORE: {state_in}\n")

    t0 = time.monotonic()
    state_out = agent.execute(state_in)
    elapsed = round(time.monotonic() - t0, 2)

    print(f"Sample AgentState AFTER: molecule_name='{state_out.molecule_name}', "
          f"patent={type(state_out.patent).__name__}, "
          f"warnings_count={len(state_out.warnings)}\n")

    check("Agent executed without throwing exception", True)
    check("state.patent is PatentLandscapeDomain", state_out.patent is not None)

    if state_out.patent:
        domain = state_out.patent
        check("Domain molecule_name matches", domain.molecule_name == "Metformin")
        check("At least 1 patent record mapped", len(domain.patents) > 0, f"{len(domain.patents)} records")
        check("is_empty is False", not domain.is_empty)
        check("active_patents property works", isinstance(domain.active_patents, list), f"{len(domain.active_patents)} active")
        check("expired_patents property works", isinstance(domain.expired_patents, list), f"{len(domain.expired_patents)} expired")
        check("at_risk_patents property works", isinstance(domain.at_risk_patents, list), f"{len(domain.at_risk_patents)} at risk")
        check("fto_summary property works", isinstance(domain.fto_summary, str), domain.fto_summary)

        # Check fields of first mapped patent record
        first = domain.patents[0]
        check("Record has jurisdiction", len(first.jurisdiction) > 0, first.jurisdiction)
        check("Record has status", len(first.status) > 0, first.status)
        check("Record has fto_status", len(first.fto_status) > 0, first.fto_status)

    check(f"Execution time", elapsed < 10, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using helper function entrypoint)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu = AgentState(molecule_name="Ibuprofen")
    t0 = time.monotonic()
    state_ibu_out = run_patent_agent(state_ibu)
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("Functional run_patent_agent succeeded", True)
    check("state.patent is populated", state_ibu_out.patent is not None)
    if state_ibu_out.patent:
        check("Ibuprofen patent records mapped", len(state_ibu_out.patent.patents) > 0, f"{len(state_ibu_out.patent.patents)} records")

    check(f"Execution time", elapsed_ibu < 10, f"{elapsed_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Graceful empty handling + Warning)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 ]")
    state_unk = AgentState(molecule_name="UnknownMoleculeXYZ9999")
    t0 = time.monotonic()
    state_unk_out = agent.execute(state_unk)
    elapsed_unk = round(time.monotonic() - t0, 2)

    check("Executed without throwing exception", True)
    check("state.patent is PatentLandscapeDomain", state_unk_out.patent is not None)
    if state_unk_out.patent:
        check("is_empty is True", state_unk_out.patent.is_empty, "0 records")
        check("patents list is empty", len(state_unk_out.patent.patents) == 0)

    check("Warning message appended to state.warnings", len(state_unk_out.warnings) > 0, state_unk_out.warnings[0])
    check(f"Execution time", elapsed_unk < 10, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 9 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
