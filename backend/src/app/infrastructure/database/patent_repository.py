"""
infrastructure/database/patent_repository.py

Repository for the patents table.

Responsibilities:
  1. Issue the Supabase query.
  2. Handle any DB errors gracefully.
  3. Map raw dicts → typed domain models (including date parsing).
  4. Log results for traceability.

Only the Patent Agent calls this — never directly from routes or
orchestrator.
"""

import logging
from datetime import date
from app.infrastructure.database.supabase_client import get_supabase
from app.domain.patent import PatentRecord, PatentLandscapeDomain

logger = logging.getLogger(__name__)


class PatentRepository:
    """
    Wraps all database access for the patents table.
    """

    def __init__(self):
        self._db = get_supabase()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_by_molecule(self, molecule_name: str) -> PatentLandscapeDomain:
        """
        Fetch all patent records for a molecule.

        Results are ordered by expiry_date descending — patents expiring
        furthest in the future (highest business risk) come first.

        Returns a PatentLandscapeDomain with an empty patents list if
        nothing is found or if the query fails.
        """
        domain = PatentLandscapeDomain(molecule_name=molecule_name)

        try:
            response = (
                self._db
                .table("patents")
                .select("*")
                .ilike("molecule_name", molecule_name)
                .order("expiry_date", desc=True)       # highest-risk (farthest expiry) first
                .execute()
            )

            for row in (response.data or []):
                domain.patents.append(self._map_row(row))

            logger.info(
                "PatentRepository: found %d records for '%s'",
                len(domain.patents), molecule_name
            )

        except Exception as exc:
            logger.warning(
                "PatentRepository: query failed for '%s'. Error: %s",
                molecule_name, str(exc)
            )

        return domain

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _map_row(self, row: dict) -> PatentRecord:
        """
        Convert one raw Supabase dict into a typed PatentRecord.

        Supabase returns dates as ISO 8601 strings ('2030-06-14').
        We parse them into Python date objects here so callers don't
        need to handle string-to-date conversion themselves.
        """
        return PatentRecord(
            molecule_name = row["molecule_name"],
            patent_number = row.get("patent_number"),
            jurisdiction  = row["jurisdiction"],
            filing_date   = self._parse_date(row.get("filing_date")),
            expiry_date   = self._parse_date(row.get("expiry_date")),
            status        = row["status"],
            patent_type   = row.get("patent_type"),
            assignee      = row.get("assignee"),
            fto_status    = row.get("fto_status", "Free to Operate"),
            data_source   = row.get("data_source", "USPTO / EPO (mock)"),
        )

    @staticmethod
    def _parse_date(value) -> date | None:
        """
        Parse an ISO date string from Supabase into a Python date.
        Returns None if the value is missing or unparseable.
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except (ValueError, TypeError):
            logger.debug("PatentRepository: could not parse date value: %r", value)
            return None
