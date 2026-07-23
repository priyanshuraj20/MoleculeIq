"""
Verification script for Session 5 — Infrastructure Clients.

Tests all three external API clients: ClinicalTrials, Europe PMC, Comtrade.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_clients.py

What this checks:
  1. Client instances initialize without error.
  2. search_molecule("Metformin") returns a non-empty dict.
  3. The response contains expected top-level keys.
  4. Record count is reported.
  5. search_molecule("UnknownMoleculeXYZ") returns gracefully (empty dict or
     valid response with zero results — both are acceptable).
  6. Execution time is printed for each call.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.infrastructure.clients.clinicaltrials_client import ClinicalTrialsClient
from app.infrastructure.clients.europepmc_client import EuropePMCClient
from app.infrastructure.clients.comtrade_client import ComtradeClient

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


# ------------------------------------------------------------------ #
# Async test runner
# ------------------------------------------------------------------ #

async def run_all():

    print("\n========================================")
    print("MoleculeIQ — Session 5 Client Verification")
    print("========================================\n")

    # ------------------------------------------------------------------ #
    # 1. ClinicalTrials.gov
    # ------------------------------------------------------------------ #
    print("[ ClinicalTrialsClient — Metformin ]")
    ct_client = ClinicalTrialsClient()
    t0 = time.monotonic()
    ct_result = await ct_client.search_molecule("Metformin")
    elapsed = round(time.monotonic() - t0, 2)

    check("Request completed",            ct_result is not None)
    check("Response is dict",             isinstance(ct_result, dict))
    check("Non-empty response received",  len(ct_result) > 0,          f"{len(ct_result)} keys")
    check("Has 'studies' key",            "studies" in ct_result)
    studies_count = len(ct_result.get("studies", []))
    total_count   = ct_result.get("totalCount", studies_count)
    check("At least 1 study returned",    studies_count > 0,           f"{studies_count} studies returned")
    check("Total count is positive",      total_count > 0,             f"{total_count} total trials found")
    check(f"Execution time",              elapsed < 30,                f"{elapsed}s")

    print(f"\n[ ClinicalTrialsClient — Unknown molecule ]")
    t0 = time.monotonic()
    ct_empty = await ct_client.search_molecule("UnknownMoleculeXYZ9999")
    elapsed_empty = round(time.monotonic() - t0, 2)
    # Acceptable: empty dict {} OR valid dict with totalCount=0
    is_graceful = (ct_empty == {} or ct_empty.get("totalCount", 0) == 0)
    check("Graceful response (no crash)",  True)
    check("Zero or empty result",          is_graceful,                f"totalCount={ct_empty.get('totalCount', 'N/A')}")
    check(f"Execution time",               elapsed_empty < 30,         f"{elapsed_empty}s")
    await ct_client.close()

    # ------------------------------------------------------------------ #
    # 2. Europe PMC
    # ------------------------------------------------------------------ #
    print(f"\n[ EuropePMCClient — Metformin ]")
    pmc_client = EuropePMCClient()
    t0 = time.monotonic()
    pmc_result = await pmc_client.search_molecule("Metformin")
    elapsed = round(time.monotonic() - t0, 2)

    check("Request completed",            pmc_result is not None)
    check("Response is dict",             isinstance(pmc_result, dict))
    check("Non-empty response received",  len(pmc_result) > 0,          f"{len(pmc_result)} keys")
    check("Has 'hitCount' key",           "hitCount" in pmc_result)
    check("Has 'resultList' key",         "resultList" in pmc_result)
    hit_count  = pmc_result.get("hitCount", 0)
    papers     = pmc_result.get("resultList", {}).get("result", [])
    check("hitCount is positive",         hit_count > 0,               f"{hit_count} total papers")
    check("At least 1 paper returned",    len(papers) > 0,             f"{len(papers)} papers returned")
    check(f"Execution time",              elapsed < 30,                f"{elapsed}s")

    print(f"\n[ EuropePMCClient — Unknown molecule ]")
    t0 = time.monotonic()
    pmc_empty = await pmc_client.search_molecule("UnknownMoleculeXYZ9999")
    elapsed_empty = round(time.monotonic() - t0, 2)
    pmc_graceful = (pmc_empty == {} or pmc_empty.get("hitCount", 0) == 0)
    check("Graceful response (no crash)",  True)
    check("Zero or empty result",          pmc_graceful,               f"hitCount={pmc_empty.get('hitCount', 'N/A')}")
    check(f"Execution time",               elapsed_empty < 30,         f"{elapsed_empty}s")
    await pmc_client.close()

    # ------------------------------------------------------------------ #
    # 3. UN Comtrade
    # ------------------------------------------------------------------ #
    print(f"\n[ ComtradeClient — Metformin (HS 3004 proxy) ]")
    ct2_client = ComtradeClient()
    t0 = time.monotonic()
    comtrade_result = await ct2_client.search_molecule("Metformin")
    elapsed = round(time.monotonic() - t0, 2)

    check("Request completed",            comtrade_result is not None)
    check("Response is dict",             isinstance(comtrade_result, dict))
    check("Non-empty response received",  len(comtrade_result) > 0,    f"{len(comtrade_result)} keys")
    check("Has 'data' key",               "data" in comtrade_result)
    records = len(comtrade_result.get("data", []))
    check("At least 1 trade record",      records > 0,                 f"{records} records")
    check(f"Execution time",              elapsed < 30,                f"{elapsed}s")

    # Comtrade is HS-code based — same response for "unknown" molecule
    print(f"\n[ ComtradeClient — Unknown molecule (same HS code — expected same result) ]")
    t0 = time.monotonic()
    comtrade_empty = await ct2_client.search_molecule("UnknownMoleculeXYZ9999")
    elapsed_empty = round(time.monotonic() - t0, 2)
    check("Graceful response (no crash)", True)
    check("Returns dict",                 isinstance(comtrade_empty, dict))
    check(f"Execution time",              elapsed_empty < 30,          f"{elapsed_empty}s")
    await ct2_client.close()

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 5 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all())
    sys.exit(0 if success else 1)
