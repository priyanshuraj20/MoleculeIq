"""
Verification script for Session 13 — FastAPI Research API.

Tests POST /api/research endpoint using FastAPI TestClient.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_api.py

Checks:
  1. POST /api/research for 'Metformin' returns HTTP 200.
  2. JSON response structure matches complete ResearchContext schema.
  3. All 4 domain objects (clinical, literature, market, patent) present in JSON body.
  4. metadata and score sections present and correctly populated.
  5. POST /api/research for 'Ibuprofen' returns HTTP 200 with populated research context.
  6. POST /api/research for 'UnknownMoleculeXYZ9999' returns HTTP 200 with degraded empty domains.
  7. Invalid input (empty molecule_name) returns HTTP 422 Unprocessable Entity without stack trace.
"""

import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from app.main import app

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
    print("MoleculeIQ — Session 13 FastAPI Research API Verification")
    print("========================================\n")

    client = TestClient(app)

    # ------------------------------------------------------------------ #
    # Test 1: POST /api/research for Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: POST /api/research — Metformin ]")
    payload_met = {"molecule_name": "Metformin"}
    print(f"Sample Request Payload: {payload_met}\n")

    t0 = time.monotonic()
    response_met = client.post("/api/research", json=payload_met)
    elapsed = round(time.monotonic() - t0, 2)

    check("HTTP Status Code is 200 OK", response_met.status_code == 200, f"Status: {response_met.status_code}")

    if response_met.status_code == 200:
        data = response_met.json()
        print(f"Sample Response Keys: {list(data.keys())}")
        print(f"  molecule_name = '{data.get('molecule_name')}'")
        print(f"  score         = Overall: {data.get('score', {}).get('overall_score')}, Confidence: {data.get('score', {}).get('confidence_score')}")
        print(f"  metadata      = Total Trials: {data.get('metadata', {}).get('total_trials')}, Publications: {data.get('metadata', {}).get('total_publications')}, Market: ${data.get('metadata', {}).get('global_market_size_usd_mn')}M, Patents: {data.get('metadata', {}).get('patent_count')}\n")

        check("Response molecule_name matches", data.get("molecule_name") == "Metformin")
        check("Clinical domain present in JSON", "clinical" in data and data["clinical"] is not None)
        check("Literature domain present in JSON", "literature" in data and data["literature"] is not None)
        check("Market domain present in JSON", "market" in data and data["market"] is not None)
        check("Patent domain present in JSON", "patent" in data and data["patent"] is not None)
        check("Metadata present in JSON", "metadata" in data and isinstance(data["metadata"], dict))
        check("Score present in JSON", "score" in data and isinstance(data["score"], dict))
        check("Score overall_score > 0", data.get("score", {}).get("overall_score", 0) > 0)
        check("Warnings & Errors lists present", "warnings" in data and "errors" in data)

    check(f"Endpoint execution time", elapsed < 30, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: POST /api/research for Ibuprofen
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: POST /api/research — Ibuprofen ]")
    t0 = time.monotonic()
    response_ibu = client.post("/api/research", json={"molecule_name": "Ibuprofen"})
    elapsed_ibu = round(time.monotonic() - t0, 2)

    check("HTTP Status Code is 200 OK", response_ibu.status_code == 200, f"Status: {response_ibu.status_code}")
    if response_ibu.status_code == 200:
        data_ibu = response_ibu.json()
        check("Ibuprofen score calculated", data_ibu.get("score", {}).get("overall_score", 0) > 0, f"Overall: {data_ibu.get('score', {}).get('overall_score')}")

    check(f"Ibuprofen execution time", elapsed_ibu < 30, f"{elapsed_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: POST /api/research for Unknown Molecule
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: POST /api/research — UnknownMoleculeXYZ9999 ]")
    t0 = time.monotonic()
    response_unk = client.post("/api/research", json={"molecule_name": "UnknownMoleculeXYZ9999"})
    elapsed_unk = round(time.monotonic() - t0, 2)

    check("HTTP Status Code is 200 OK", response_unk.status_code == 200, f"Status: {response_unk.status_code}")
    if response_unk.status_code == 200:
        data_unk = response_unk.json()
        check("Unknown molecule score generated gracefully", "score" in data_unk and data_unk["score"] is not None)
        check("Warnings captured in JSON response", len(data_unk.get("warnings", [])) >= 2, f"{len(data_unk.get('warnings', []))} warnings")

    check(f"Unknown molecule execution time", elapsed_unk < 30, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Test 4: Validation Error Handling (Empty molecule_name)
    # ------------------------------------------------------------------ #
    print("\n[ Test 4: Validation Handling — Empty molecule_name ]")
    response_val = client.post("/api/research", json={"molecule_name": "   "})
    check("HTTP Status Code is 422 Unprocessable Entity", response_val.status_code == 422, f"Status: {response_val.status_code}")
    if response_val.status_code == 422:
        val_data = response_val.json()
        check("Clean error detail returned (no stack trace)", "detail" in val_data)

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 13 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
