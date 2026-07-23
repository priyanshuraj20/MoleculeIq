"""
Verification script for Session 7 — Literature Worker Agent.

Tests LiteratureAgent execution end-to-end.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_literature_agent.py

Checks:
  1. Initial AgentState constructed cleanly.
  2. Agent executes successfully for 'Metformin'.
  3. Domain objects (LiteratureDomain, LiteratureRecord) properly populated.
  4. highly_cited_papers, recent_papers, and top_journals properties work.
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
from app.agents.literature_agent import LiteratureAgent, run_literature_agent

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
    print("MoleculeIQ — Session 7 Literature Agent Verification")
    print("========================================\n")

    agent = LiteratureAgent()

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
          f"literature={type(state_out.literature).__name__}, "
          f"errors_count={len(state_out.errors)}\n")

    check("Agent executed without throwing exception", True)
    check("state.literature is LiteratureDomain", state_out.literature is not None)

    if state_out.literature:
        domain = state_out.literature
        check("Domain molecule_name matches", domain.molecule_name == "Metformin")
        check("At least 1 publication mapped", len(domain.publications) > 0, f"{len(domain.publications)} papers")
        check("total_found is positive", domain.total_found > 0, f"{domain.total_found} papers found")
        check("is_empty is False", not domain.is_empty)
        check("highly_cited_papers property works", isinstance(domain.highly_cited_papers, list), f"{len(domain.highly_cited_papers)} highly cited")
        check("recent_papers property works", isinstance(domain.recent_papers, list), f"{len(domain.recent_papers)} recent")
        check("top_journals property works", isinstance(domain.top_journals, list), f"{len(domain.top_journals)} unique journals")

        # Check fields of first mapped publication
        first = domain.publications[0]
        check("Record has title", len(first.title) > 0, first.title[:40] + "...")
        check("Record has authors", len(first.authors) > 0, first.authors[:30] + "...")
        check("Record has journal", len(first.journal) > 0, first.journal)
        check("Record has citation_count", isinstance(first.citation_count, int), f"{first.citation_count} citations")

    check(f"Execution time", elapsed < 30, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using helper function entrypoint)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu = AgentState(molecule_name="Ibuprofen")
    t0 = time.monotonic()
    state_ibu_out = await run_literature_agent(state_ibu)
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("Functional run_literature_agent succeeded", True)
    check("state.literature is populated", state_ibu_out.literature is not None)
    if state_ibu_out.literature:
        check("Ibuprofen papers mapped", len(state_ibu_out.literature.publications) > 0, f"{len(state_ibu_out.literature.publications)} papers")

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
    check("state.literature is LiteratureDomain", state_unk_out.literature is not None)
    if state_unk_out.literature:
        check("is_empty is True", state_unk_out.literature.is_empty, "0 records")
        check("publications list is empty", len(state_unk_out.literature.publications) == 0)

    check(f"Execution time", elapsed_unk < 30, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 7 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    await agent._client.close()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
