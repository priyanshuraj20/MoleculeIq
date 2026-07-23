"""
Verification script for Session 8 — Market Insights Worker Agent.

Tests MarketAgent execution end-to-end against Supabase database.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_market_agent.py

Checks:
  1. Initial AgentState constructed cleanly.
  2. Agent executes successfully for 'Metformin'.
  3. Domain objects (MarketInsightsDomain, MarketDataPoint) properly populated.
  4. global_market_size_usd_mn and latest_cagr properties work.
  5. Agent executes successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') handled gracefully with warning appended.
"""

import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.domain.agent_state import AgentState
from app.agents.market_agent import MarketAgent, run_market_agent

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
    print("MoleculeIQ — Session 8 Market Agent Verification")
    print("========================================\n")

    agent = MarketAgent()

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
          f"market={type(state_out.market).__name__}, "
          f"warnings_count={len(state_out.warnings)}\n")

    check("Agent executed without throwing exception", True)
    check("state.market is MarketInsightsDomain", state_out.market is not None)

    if state_out.market:
        domain = state_out.market
        check("Domain molecule_name matches", domain.molecule_name == "Metformin")
        check("At least 1 market data point mapped", len(domain.data_points) > 0, f"{len(domain.data_points)} points")
        check("is_empty is False", not domain.is_empty)
        check("global_market_size_usd_mn is set", domain.global_market_size_usd_mn is not None, f"${domain.global_market_size_usd_mn}M")
        check("latest_cagr is set", domain.latest_cagr is not None, f"{domain.latest_cagr}%")

        # Check fields of first mapped data point
        first = domain.data_points[0]
        check("Data point has region", len(first.region) > 0, first.region)
        check("Data point has therapeutic_area", len(first.therapeutic_area) > 0, first.therapeutic_area)
        check("Data point has market_size_usd_mn", first.market_size_usd_mn > 0, f"${first.market_size_usd_mn}M")

    check(f"Execution time", elapsed < 10, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using helper function entrypoint)
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu = AgentState(molecule_name="Ibuprofen")
    t0 = time.monotonic()
    state_ibu_out = run_market_agent(state_ibu)
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("Functional run_market_agent succeeded", True)
    check("state.market is populated", state_ibu_out.market is not None)
    if state_ibu_out.market:
        check("Ibuprofen market data mapped", len(state_ibu_out.market.data_points) > 0, f"{len(state_ibu_out.market.data_points)} data points")

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
    check("state.market is MarketInsightsDomain", state_unk_out.market is not None)
    if state_unk_out.market:
        check("is_empty is True", state_unk_out.market.is_empty, "0 data points")
        check("data_points list is empty", len(state_unk_out.market.data_points) == 0)

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
        print("All checks passed. Session 8 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
