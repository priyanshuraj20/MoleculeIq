"""
infrastructure/clients/comtrade_client.py

Client for the UN Comtrade API v1.

API Documentation:
    https://comtradeapi.un.org/

Endpoint:
    GET https://comtradeapi.un.org/data/v1/get/C/A/HS

Authentication:
    Subscription key passed as HTTP header:
        Ocp-Apim-Subscription-Key: <COMTRADE_API_KEY>
    Key is read from environment — never hardcoded.

Request Parameters:
    cmdCode      : HS commodity code. We use chapter 30 (pharmaceutical products).
                   Specifically HS 3004 = Medicaments for therapeutic use.
    period       : Year of data (e.g. "2022"). From config: COMTRADE_PERIOD.
    reporterCode : UN country code. "0" = World aggregate (all countries combined).
    flowCode     : Trade flow. "M" = Imports, "X" = Exports, "MX" = both.
    maxRecords   : Max rows returned. We cap at 20 to keep latency low.

Response Structure:
    {
      "data": [
        {
          "reporterCode": 0,
          "reporterDesc": "World",
          "flowCode": "M",
          "flowDesc": "Imports",
          "period": 2022,
          "cmdCode": "3004",
          "cmdDesc": "Medicaments",
          "primaryValue": 498000000000.0,   -- trade value in USD
          "netWgt": 1234567890.0,           -- net weight in kg
          "qty": null,
          "partnerCode": 0,
          "partnerDesc": "World"
        },
        ...
      ],
      "validation": { ... },
      "count": 20
    }

Design Note — Why HS codes instead of molecule names?
    UN Comtrade is a TRADE STATISTICS database. It organises data by
    commodity code (HS = Harmonized System), not by molecule name.

    A molecule name like "Metformin" has no direct Comtrade identifier.
    Instead, pharmaceutical active ingredients fall under:
        HS 2941  — Antibiotics
        HS 2942  — Other organic compounds (where most APIs fall)
        HS 3003  — Medicaments (unmixed products, bulk)
        HS 3004  — Medicaments (mixed, packaged for retail)

    For MVP: we fetch HS 3004 (packaged medicaments) as the representative
    pharmaceutical trade category. This gives import/export volume context
    for the therapeutic market the molecule competes in.

    In a production system, a molecule-to-HS-code mapping table would
    allow precise commodity-level queries. This is a Phase 5+ enhancement.

Timeout Strategy:
    connect: 10s
    read:    30s — Comtrade can be slow during peak hours

Retry Strategy:
    3 attempts with exponential backoff (2s, 4s, 8s).
    Retries on timeout, network error, and HTTP 5xx.

Rate Limit Notes:
    Free tier subscription: 500 requests/day.
    We run 1 request per user query — well within limits.
    Do NOT log the API key. Log only key presence (bool).

Known Limitations:
    - Data is annual, not monthly. Most recent year is typically 2022 or 2023.
    - HS codes group many drugs together. HS 3004 includes ALL packaged drugs,
      not just the molecule being researched.
    - Some countries report late or not at all. "World" aggregate fills gaps.
    - Free tier does not support sub-chapter HS codes (4-digit only).
"""

import logging

from app.core.config import settings
from app.infrastructure.clients._base_client import BaseAPIClient

logger = logging.getLogger(__name__)

# HS code for "Medicaments packaged for retail" — the broadest pharmaceutical category.
# Used as the default commodity when a molecule-level HS code is not available.
DEFAULT_PHARMA_HS_CODE = "3004"


class ComtradeClient(BaseAPIClient):
    """
    Fetches pharmaceutical trade statistics from UN Comtrade API v1.

    Returns raw API response dicts — no domain model conversion here.
    The Trade Analysis Agent is responsible for interpreting the data.
    """

    _client_name = "Comtrade"

    def __init__(self):
        super().__init__()

        # Validate at init time — fail fast rather than silently during queries
        if not settings.COMTRADE_API_KEY:
            logger.warning(
                "[Comtrade] COMTRADE_API_KEY is not set in .env. "
                "All requests will fail with 401 Unauthorized."
            )

    async def search_molecule(self, molecule_name: str) -> dict:
        """
        Fetch pharmaceutical trade data relevant to a molecule.

        Because Comtrade is HS-code based (not molecule-name based),
        this method fetches HS 3004 (packaged medicaments) trade data
        for the configured reporting period.

        The molecule_name parameter is accepted for interface consistency
        and included in logs, but does not change the HS code query.

        Args:
            molecule_name: Drug name (used for logging context only).

        Returns:
            Raw API response dict with key: data (list of trade records).
            Returns {} on any failure — including missing API key.
        """
        if not settings.COMTRADE_API_KEY:
            logger.error(
                "[Comtrade] Cannot search for '%s' — COMTRADE_API_KEY not configured",
                molecule_name
            )
            return {}

        # Endpoint: /get/{typeCode}/{freqCode}/{clCode}
        # C = commodities, A = annual, HS = Harmonized System
        url = f"{settings.COMTRADE_BASE_URL}/get/C/A/HS"

        params = {
            "cmdCode":      DEFAULT_PHARMA_HS_CODE,  # HS 3004 = packaged medicaments
            "period":       settings.COMTRADE_PERIOD, # e.g. "2022"
            "reporterCode": "842",                    # 842 = United States (major global pharma market)
            "maxRecords":   "20",
        }

        # API key goes in request header — NEVER logged
        headers = {
            "Ocp-Apim-Subscription-Key": settings.COMTRADE_API_KEY,
        }

        logger.info(
            "[Comtrade] Fetching HS %s trade data for period %s (context: '%s') "
            "[key present: %s]",
            DEFAULT_PHARMA_HS_CODE,
            settings.COMTRADE_PERIOD,
            molecule_name,
            bool(settings.COMTRADE_API_KEY),   # log presence, never the key itself
        )

        result = await self._get(url, params=params, headers=headers)

        if result:
            records = len(result.get("data", []))
            logger.info(
                "[Comtrade] HS %s period %s → %d trade records returned",
                DEFAULT_PHARMA_HS_CODE, settings.COMTRADE_PERIOD, records
            )
        else:
            logger.warning(
                "[Comtrade] Empty response for molecule '%s'", molecule_name
            )

        return result
