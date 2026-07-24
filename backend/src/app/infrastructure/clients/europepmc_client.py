"""
infrastructure/clients/europepmc_client.py

Client for the Europe PubMed Central (Europe PMC) REST API.

API Documentation:
    https://europepmc.org/RestfulWebService

Endpoint:
    GET https://www.ebi.ac.uk/europepmc/webservices/rest/search

Request Parameters:
    query      : Search string — molecule name, MeSH term, or full query
    format     : Always 'json'
    pageSize   : Results per request (max 1000, we use 10)
    resultType : 'core' returns full metadata; 'lite' returns summary only
    sort       : 'RELEVANCE' or 'CITED desc' for popularity-sorted results

Response Structure:
    {
      "version": "6.9",
      "hitCount": 45231,
      "nextCursorMark": "AoE=...",
      "resultList": {
        "result": [
          {
            "id": "PMC1234567",
            "source": "PMC",
            "pmid": "12345678",
            "title": "Metformin reduces...",
            "abstractText": "...",
            "journalTitle": "Nature Medicine",
            "pubYear": "2022",
            "citedByCount": 142,
            "authorString": "Smith J, ...",
            "meshHeadings": { "meshHeading": [...] }
          },
          ...
        ]
      }
    }

Timeout Strategy:
    connect: 10s — EBI servers in Hinxton, UK, generally fast
    read:    30s — 'core' result type returns more data per record

Retry Strategy:
    3 attempts with exponential backoff (2s, 4s, 8s).
    Retries on timeout and 5xx. Does not retry on 4xx.

Rate Limit Notes:
    No hard rate limit for the public API.
    EBI recommends polite use: < 10 req/s.
    We run 1 request per user query so this is never a concern.

Known Limitations:
    - Search matches all fields (title, abstract, MeSH). A common drug name
      like "Aspirin" returns tens of thousands of results; we return top 10.
    - Literature coverage is strong for post-2000 papers. Pre-2000 coverage
      is inconsistent.
    - abstractText may be null for older papers or conference proceedings.
    - citedByCount is updated nightly, not real-time.
"""

import logging

from app.core.config import settings
from app.infrastructure.clients._base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class EuropePMCClient(BaseAPIClient):
    """
    Fetches scientific literature records from Europe PMC REST API.

    Returns raw API response dicts — no domain model conversion here.
    The Literature Agent is responsible for interpreting the data.
    """

    _client_name = "EuropePMC"

    async def search_molecule(self, molecule_name: str) -> dict:
        """
        Search Europe PMC for publications about a molecule.

        The query combines the molecule name with MeSH-style scope limiting
        to pharmaceutical/clinical literature. Without scoping, very common
        names return hundreds of thousands of results.

        Args:
            molecule_name: Drug or molecule name (e.g. "Metformin").

        Returns:
            Raw API response dict with keys: hitCount, resultList.
            Returns {} on any failure.
        """
        url = f"{settings.EUROPEPMC_BASE_URL}/search"

        # Scope the search to exact compound name + Medline/PMC sources for precision
        clean_name = molecule_name.strip().strip('"')
        query = f'"{clean_name}" AND (SRC:MED OR SRC:PMC)'

        params = {
            "query":      query,
            "format":     "json",
            "pageSize":   settings.EUROPEPMC_PAGE_SIZE,
            "resultType": "core",    # full metadata including abstract
            "sort":       "CITED desc",  # most-cited papers first
        }

        logger.info(
            "[EuropePMC] Searching for '%s' (pageSize=%d, sort=CITED desc)",
            molecule_name, settings.EUROPEPMC_PAGE_SIZE
        )

        result = await self._get(url, params=params)

        if result:
            hit_count = result.get("hitCount", 0)
            returned  = len(result.get("resultList", {}).get("result", []))
            logger.info(
                "[EuropePMC] '%s' → %d total papers, %d returned",
                molecule_name, hit_count, returned
            )
        else:
            logger.warning("[EuropePMC] Empty response for '%s'", molecule_name)

        return result
