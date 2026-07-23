"""
Verification script for Session 16 — Professional PDF Report Generation.

Tests full pipeline from research -> aggregation -> scoring -> executive report -> PDF generation:
  ResearchContext + ExecutiveReport -> PDFReportService -> PDF bytes

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_pdf.py

Checks:
  1. Full pipeline + aggregation + scoring + executive report runs for 'Metformin'.
  2. PDFReportService generates PDF bytes starting with '%PDF-'.
  3. PDF byte size > 5,000 bytes.
  4. Saves sample Metformin PDF to 'backend/artifacts/Metformin_Executive_Report.pdf'.
  5. PDF generated successfully for 'Ibuprofen'.
  6. Unknown molecule ('UnknownMoleculeXYZ9999') generates valid PDF cleanly with degraded empty state tables.
"""

import asyncio
import sys
import os
import time

# Add src/ to path so app modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.orchestrator import run_research_pipeline
from app.services import (
    AggregationService,
    ScoringService,
    ExecutiveReportService,
    PDFReportService,
    generate_pdf_report
)

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
    print("MoleculeIQ — Session 16 PDF Generation Verification")
    print("========================================\n")

    agg_service    = AggregationService()
    score_service  = ScoringService()
    report_service = ExecutiveReportService()
    pdf_service    = PDFReportService()

    # ------------------------------------------------------------------ #
    # Test 1: Metformin
    # ------------------------------------------------------------------ #
    print("[ Test 1: Metformin ]")
    state_met   = await run_research_pipeline("Metformin")
    context_met = agg_service.build_context(state_met)
    context_met = score_service.evaluate_and_attach(context_met)
    report_met  = await report_service.generate_report(context_met)

    t0 = time.monotonic()
    pdf_bytes_met = pdf_service.generate_pdf(context_met, report_met)
    pdf_time = round(time.monotonic() - t0, 3)

    check("PDF bytes returned", isinstance(pdf_bytes_met, bytes))
    check("Starts with %PDF- magic header", pdf_bytes_met.startswith(b"%PDF-"))
    check("PDF size > 5,000 bytes", len(pdf_bytes_met) > 5000, f"{len(pdf_bytes_met):,} bytes")
    check(f"PDF generation execution time", pdf_time < 2.0, f"{pdf_time}s")

    # Save artifact for visual inspection
    artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    sample_path = os.path.join(artifacts_dir, "Metformin_Executive_Report.pdf")
    with open(sample_path, "wb") as f:
        f.write(pdf_bytes_met)
    print(f"  Saved sample PDF artifact to: {os.path.abspath(sample_path)}\n")

    # ------------------------------------------------------------------ #
    # Test 2: Ibuprofen (using functional entrypoint)
    # ------------------------------------------------------------------ #
    print("[ Test 2: Ibuprofen (functional entrypoint) ]")
    state_ibu   = await run_research_pipeline("Ibuprofen")
    context_ibu = agg_service.build_context(state_ibu)
    context_ibu = score_service.evaluate_and_attach(context_ibu)
    report_ibu  = await report_service.generate_report(context_ibu)

    t0 = time.monotonic()
    pdf_bytes_ibu = generate_pdf_report(context_ibu, report_ibu)
    pdf_time_ibu = round(time.monotonic() - t0, 3)

    check("Functional generate_pdf_report succeeded", isinstance(pdf_bytes_ibu, bytes))
    check("Ibuprofen PDF starts with %PDF-", pdf_bytes_ibu.startswith(b"%PDF-"))
    check("Ibuprofen PDF size > 5,000 bytes", len(pdf_bytes_ibu) > 5000, f"{len(pdf_bytes_ibu):,} bytes")
    check(f"Ibuprofen PDF generation time", pdf_time_ibu < 2.0, f"{pdf_time_ibu}s")

    # ------------------------------------------------------------------ #
    # Test 3: Unknown Molecule (Degraded empty tables PDF)
    # ------------------------------------------------------------------ #
    print("\n[ Test 3: UnknownMoleculeXYZ9999 (Degraded empty tables) ]")
    state_unk   = await run_research_pipeline("UnknownMoleculeXYZ9999")
    context_unk = agg_service.build_context(state_unk)
    context_unk = score_service.evaluate_and_attach(context_unk)
    report_unk  = await report_service.generate_report(context_unk)

    t0 = time.monotonic()
    pdf_bytes_unk = pdf_service.generate_pdf(context_unk, report_unk)
    pdf_time_unk = round(time.monotonic() - t0, 3)

    check("Unknown molecule PDF generated without exception", isinstance(pdf_bytes_unk, bytes))
    check("Unknown molecule PDF starts with %PDF-", pdf_bytes_unk.startswith(b"%PDF-"))
    check("Unknown molecule PDF size > 5,000 bytes", len(pdf_bytes_unk) > 5000, f"{len(pdf_bytes_unk):,} bytes")
    check(f"Unknown molecule PDF generation time", pdf_time_unk < 2.0, f"{pdf_time_unk}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n========================================")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed. Session 16 complete.")
    else:
        print(f"{total - passed} check(s) failed.")
    print("========================================\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
