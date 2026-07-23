"""
Verification script for Session 14 — Server-Sent Events (SSE) Research Streaming.

Tests GET /api/v1/research/stream?molecule_name=Metformin using FastAPI TestClient.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_stream.py

Checks:
  1. GET /api/v1/research/stream for 'Metformin' returns HTTP 200 with media_type='text/event-stream'.
  2. All 12 expected SSE events emitted in correct order.
  3. Final event 'research_completed' contains full ResearchContext payload.
  4. Stream closes cleanly.
  5. Stream runs successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') streams cleanly to completion with degraded empty state.
"""

import json
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


def parse_sse_stream(response_stream):
    """
    Parses raw SSE stream text lines into structured (event_name, data_dict) tuples.
    """
    events = []
    current_event = None
    current_data = None

    for line in response_stream.iter_lines():
        line = line.strip()
        if not line:
            if current_event and current_data is not None:
                try:
                    parsed_json = json.loads(current_data)
                except json.JSONDecodeError:
                    parsed_json = current_data
                events.append((current_event, parsed_json))
                current_event = None
                current_data = None
            continue

        if line.startswith("event:"):
            current_event = line[6:].strip()
        elif line.startswith("data:"):
            current_data = line[5:].strip()

    # Flush last event if stream ended without trailing double newline
    if current_event and current_data is not None:
        try:
            parsed_json = json.loads(current_data)
        except json.JSONDecodeError:
            parsed_json = current_data
        events.append((current_event, parsed_json))

    return events


def main():
    print("\n========================================")
    print("MoleculeIQ — Session 14 SSE Research Streaming Verification")
    print("========================================\n")

    client = TestClient(app)

    # ------------------------------------------------------------------ #
    # Test 1: GET /api/v1/research/stream?molecule_name=Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: GET /api/v1/research/stream — Metformin ]")
    url = "/api/v1/research/stream?molecule_name=Metformin"
    t0 = time.monotonic()

    with client.stream("GET", url) as response:
        elapsed = round(time.monotonic() - t0, 2)
        content_type = response.headers.get("content-type", "")

        check("HTTP Status Code is 200 OK", response.status_code == 200, f"Status: {response.status_code}")
        check("Content-Type is text/event-stream", "text/event-stream" in content_type, content_type)

        events = parse_sse_stream(response)

    print(f"\nReceived {len(events)} SSE Events:")
    event_names = [e[0] for e in events]
    for idx, (name, data) in enumerate(events, 1):
        summary = str(data)[:60] + "..." if len(str(data)) > 60 else str(data)
        print(f"  {idx:02d}. event: {name:<22} data: {summary}")
    print()

    expected_sequence = [
        "research_started",
        "clinical_started",
        "clinical_completed",
        "literature_started",
        "literature_completed",
        "market_started",
        "market_completed",
        "patent_started",
        "patent_completed",
        "aggregation_completed",
        "scoring_completed",
        "research_completed"
    ]

    check("Received 12 SSE events", len(events) == 12, f"{len(events)} events")
    check("Event sequence matches expected order", event_names == expected_sequence, f"Sequence: {event_names}")

    # Check final event payload
    if events and events[-1][0] == "research_completed":
        final_payload = events[-1][1]
        check("Final payload is ResearchContext dictionary", isinstance(final_payload, dict))
        check("Final payload molecule_name matches", final_payload.get("molecule_name") == "Metformin")
        check("Final payload has score", "score" in final_payload and final_payload["score"] is not None)
        check("Final payload has metadata", "metadata" in final_payload and final_payload["metadata"] is not None)
        check("Final payload has all 4 domains", all(k in final_payload for k in ["clinical", "literature", "market", "patent"]))

    check(f"Stream execution time", elapsed < 30, f"{elapsed}s")

    # ------------------------------------------------------------------ #
    # Test 2: GET /api/v1/research/stream?molecule_name=Ibuprofen
    # ------------------------------------------------------------------ #
    print("\n[ Test 2: GET /api/v1/research/stream — Ibuprofen ]")
    t0 = time.monotonic()
    with client.stream("GET", "/api/v1/research/stream?molecule_name=Ibuprofen") as response_ibu:
        elapsed_ibu = round(time.monotonic() - t0, 2)
        events_ibu = parse_sse_stream(response_ibu)

    check("Ibuprofen stream returned HTTP 200 OK", response_ibu.status_code == 200)
    check("Ibuprofen received 12 SSE events", len(events_ibu) == 12)
    if events_ibu:
        check("Ibuprofen final event is research_completed", events_ibu[-1][0] == "research_completed")

    check(f"Ibuprofen stream execution time", elapsed_ibu < 30, f"{elapsed_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: GET /api/v1/research/stream for Unknown Molecule
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: GET /api/v1/research/stream — UnknownMoleculeXYZ9999 ]")
    t0 = time.monotonic()
    with client.stream("GET", "/api/v1/research/stream?molecule_name=UnknownMoleculeXYZ9999") as response_unk:
        elapsed_unk = round(time.monotonic() - t0, 2)
        events_unk = parse_sse_stream(response_unk)

    check("Unknown molecule stream returned HTTP 200 OK", response_unk.status_code == 200)
    check("Unknown molecule received 12 SSE events", len(events_unk) == 12)
    if events_unk:
        check("Unknown molecule final event is research_completed", events_unk[-1][0] == "research_completed")

    check(f"Unknown molecule execution time", elapsed_unk < 30, f"{elapsed_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 14 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
