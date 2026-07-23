"""
infrastructure/clients/clinicaltrials_client.py

Client for the ClinicalTrials.gov API v2.

API Documentation:
    https://clinicaltrials.gov/data-api/api

Endpoint:
    GET https://clinicaltrials.gov/api/v2/studies

Request Parameters:
    query.term  : Free-text molecule or drug name search
    pageSize    : Max results per request (default 10, max 1000)
    format      : Response format — always 'json'
    fields      : Optional comma-separated list of fields to return

Response Structure:
    {
      "studies": [
        {
          "protocolSection": {
            "identificationModule": { "nctId": "NCT...", "briefTitle": "..." },
            "statusModule": { "overallStatus": "Recruiting" },
            "designModule": { "phases": ["PHASE3"] },
            "conditionsModule": { "conditions": ["Type 2 Diabetes"] },
            "sponsorCollaboratorsModule": { "leadSponsor": { "name": "..." } }
          }
        },
        ...
      ],
      "totalCount": 1234,
      "nextPageToken": "..."
    }

Timeout Strategy:
    connect: 10s — ClinicalTrials.gov is a US government server, should be fast
    read:    30s — large JSON payloads can be slow on free tier

Retry Strategy:
    3 attempts with exponential backoff (2s, 4s, 8s).
    Retries on timeout and 5xx. Does not retry on 4xx.

Rate Limit Notes:
    No official rate limit published for v2.
    Empirically: ~10 req/s is safe. We run 1 request per user query.

Known Limitations:
    - Free-text search matches against title, condition, and intervention fields.
      A molecule name match is not always exact (e.g. "Metformin" matches
      both metformin trials AND combination therapy trials mentioning metformin).
    - totalCount can be very high (thousands). We cap at pageSize=10 for latency.
    - Older trials may lack structured data (phases, conditions).
"""

import logging

from app.core.config import settings
from app.infrastructure.clients._base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class ClinicalTrialsClient(BaseAPIClient):
    """
    Fetches active clinical trial records from ClinicalTrials.gov API v2.

    Returns raw API response dicts — no domain model conversion here.
    The Clinical Trials Agent is responsible for interpreting the data.
    """

    _client_name = "ClinicalTrials"

    async def search_molecule(self, molecule_name: str) -> dict:
        """
        Search ClinicalTrials.gov for trials involving a molecule.

        Args:
            molecule_name: Drug or molecule name (e.g. "Metformin").

        Returns:
            Raw API response dict with keys: studies, totalCount.
            Returns {} on any failure.
        """
        url = f"{settings.CLINICALTRIALS_BASE_URL}/studies"

        params = {
            "query.term":  molecule_name,    # free-text search across all fields
            "pageSize":    settings.CLINICALTRIALS_PAGE_SIZE,
            "format":      "json",
        }

        logger.info(
            "[ClinicalTrials] Searching for '%s' (pageSize=%d)",
            molecule_name, settings.CLINICALTRIALS_PAGE_SIZE
        )

        result = await self._get(url, params=params)

        if result:
            total = result.get("totalCount", 0)
            found = len(result.get("studies", []))
            logger.info(
                "[ClinicalTrials] '%s' → %d total trials, %d returned",
                molecule_name, total, found
            )
        else:
            logger.warning("[ClinicalTrials] Empty response for '%s'", molecule_name)

        return result
