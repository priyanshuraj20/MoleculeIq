"""
infrastructure/database/market_repository.py

Repository for the iqvia_sales table.

Responsibilities:
  1. Issue the Supabase query.
  2. Handle any DB errors gracefully (never crash the agent pipeline).
  3. Map raw dicts → typed domain models.
  4. Log what happened so problems are easy to trace.

The agent layer ONLY imports from this file — it never touches
the Supabase client or raw query results directly.
"""

import logging
from app.infrastructure.database.supabase_client import get_supabase
from app.domain.market import MarketDataPoint, MarketInsightsDomain

# Module-level logger — named after the module for easy filtering in logs
logger = logging.getLogger(__name__)


class MarketRepository:
    """
    Wraps all database access for iqvia_sales.

    Why a class instead of plain functions?
      Easier to mock in unit tests — just swap the instance.
      Also keeps the Supabase client contained (no global state).
    """

    def __init__(self):
        # Shared Supabase client — one per repository instance
        self._db = get_supabase()

    # ------------------------------------------------------------------
    # Public API — what the agent calls
    # ------------------------------------------------------------------

    def get_by_molecule(self, molecule_name: str) -> MarketInsightsDomain:
        """
        Fetch all market data rows for a molecule name.

        Uses ILIKE for case-insensitive matching so the agent does not
        need to normalize the query string first.

        Returns a MarketInsightsDomain with an empty data_points list
        if the query fails or the molecule is not in the database —
        never raises to the caller.
        """
        domain = MarketInsightsDomain(molecule_name=molecule_name)

        try:
            response = (
                self._db
                .table("iqvia_sales")
                .select("*")
                .ilike("molecule_name", molecule_name)   # case-insensitive match
                .order("year", desc=True)                # most recent data first
                .execute()
            )

            for row in (response.data or []):
                domain.data_points.append(self._map_row(row))

            logger.info(
                "MarketRepository: found %d rows for '%s'",
                len(domain.data_points), molecule_name
            )

        except Exception as exc:
            # Log and continue — the pipeline degrades gracefully
            logger.warning(
                "MarketRepository: query failed for '%s'. Error: %s",
                molecule_name, str(exc)
            )

        return domain

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _map_row(self, row: dict) -> MarketDataPoint:
        """
        Convert one raw Supabase dict into a typed MarketDataPoint.

        All type coercions happen here, so the rest of the codebase
        works with proper Python types (float, int) not strings.
        """
        return MarketDataPoint(
            molecule_name      = row["molecule_name"],
            year               = int(row["year"]),
            region             = row["region"],
            therapeutic_area   = row["therapeutic_area"],
            market_size_usd_mn = float(row["market_size_usd_mn"]),
            cagr_percent       = float(row["cagr_percent"]) if row.get("cagr_percent") is not None else None,
            competitor_count   = int(row.get("competitor_count", 0)),
            data_source        = row.get("data_source", "IQVIA MIDAS (mock)"),
        )
