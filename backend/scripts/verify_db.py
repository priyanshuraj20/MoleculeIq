"""
Verification script for Session 4 — Database Schema & Repository Layer.

Run AFTER you have executed supabase_schema.sql in the Supabase dashboard.

Usage:
    cd backend
    .\\venv\\Scripts\\python.exe scripts\\verify_db.py

What this checks:
  1. Supabase client initializes without error.
  2. MarketRepository returns data for a known molecule.
  3. MarketInsightsDomain properties work correctly.
  4. PatentRepository returns data for a known molecule.
  5. PatentLandscapeDomain properties work correctly.
  6. Graceful handling when a molecule has no data.
"""

import sys
import os

# Add src/ to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.infrastructure.database.supabase_client import get_supabase
from app.infrastructure.database.market_repository import MarketRepository
from app.infrastructure.database.patent_repository import PatentRepository

PASS = "  PASS"
FAIL = "  FAIL"

results = []


def check(label: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    line = f"{status}  {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    results.append(condition)


print("\n========================================")
print("MoleculeIQ — Session 4 Verification")
print("========================================\n")

# ------------------------------------------------------------------
# 1. Supabase client
# ------------------------------------------------------------------
print("[ Supabase Client ]")
try:
    client = get_supabase()
    check("Client initializes", True, type(client).__name__)
except Exception as e:
    check("Client initializes", False, str(e))
    print("\nCannot continue — fix Supabase credentials in .env first.")
    sys.exit(1)

# ------------------------------------------------------------------
# 2. Market Repository — Metformin (known data)
# ------------------------------------------------------------------
print("\n[ MarketRepository — Metformin ]")
market_repo = MarketRepository()
market = market_repo.get_by_molecule("Metformin")

check("Returns MarketInsightsDomain",    hasattr(market, "data_points"))
check("Has at least 1 data point",       len(market.data_points) > 0,
      f"{len(market.data_points)} rows")
check("is_empty is False",               not market.is_empty)
check("global_market_size_usd_mn set",   market.global_market_size_usd_mn is not None,
      f"${market.global_market_size_usd_mn}M")
check("latest_cagr set",                 market.latest_cagr is not None,
      f"{market.latest_cagr}%")
check("molecule_name preserved",         market.molecule_name == "Metformin")

# ------------------------------------------------------------------
# 3. Market Repository — unknown molecule (graceful empty response)
# ------------------------------------------------------------------
print("\n[ MarketRepository — unknown molecule ]")
market_empty = market_repo.get_by_molecule("NonExistentMoleculeXYZ")
check("Returns domain model (not error)", hasattr(market_empty, "data_points"))
check("is_empty is True",                market_empty.is_empty)
check("global_market_size returns None", market_empty.global_market_size_usd_mn is None)

# ------------------------------------------------------------------
# 4. Patent Repository — Metformin (known data)
# ------------------------------------------------------------------
print("\n[ PatentRepository — Metformin ]")
patent_repo = PatentRepository()
landscape = patent_repo.get_by_molecule("Metformin")

check("Returns PatentLandscapeDomain",   hasattr(landscape, "patents"))
check("Has at least 1 patent record",    len(landscape.patents) > 0,
      f"{len(landscape.patents)} records")
check("is_empty is False",               not landscape.is_empty)
check("active_patents list works",       isinstance(landscape.active_patents, list),
      f"{len(landscape.active_patents)} active")
check("expired_patents list works",      isinstance(landscape.expired_patents, list),
      f"{len(landscape.expired_patents)} expired")
check("fto_summary string set",          len(landscape.fto_summary) > 0,
      landscape.fto_summary)
check("molecule_name preserved",         landscape.molecule_name == "Metformin")

# Check date parsing only if we actually got records back
if landscape.patents:
    first_patent = landscape.patents[0]
    check("expiry_date parsed as date object",
          first_patent.expiry_date is None or hasattr(first_patent.expiry_date, "year"),
          str(first_patent.expiry_date))
else:
    check("expiry_date parsed as date object", True, "skipped — no records (run SQL first)")

# ------------------------------------------------------------------
# 5. Patent Repository — unknown molecule
# ------------------------------------------------------------------
print("\n[ PatentRepository — unknown molecule ]")
landscape_empty = patent_repo.get_by_molecule("NonExistentMoleculeXYZ")
check("Returns domain model (not error)", hasattr(landscape_empty, "patents"))
check("is_empty is True",               landscape_empty.is_empty)
check("fto_summary still returns string", isinstance(landscape_empty.fto_summary, str))

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
passed = sum(results)
total  = len(results)
print(f"\n========================================")
print(f"Result: {passed}/{total} checks passed")
if passed == total:
    print("All checks passed. Session 4 complete.")
else:
    print(f"{total - passed} check(s) failed. Review the output above.")
print("========================================\n")

sys.exit(0 if passed == total else 1)
