"""
services/cache_service.py

Domain Caching Service for MoleculeIQ research reports.

Responsibility:
  1. Key Generation Strategy:
     - Single Molecule: report:{canonical_name.lower()}
       (e.g., 'Ozempic' and 'Semaglutide' both map to 'report:semaglutide')
     - Comparison: report:compare:{sorted_mol_1}:{sorted_mol_2}
       (e.g., 'Metformin vs Semaglutide' and 'Semaglutide vs Metformin' both map to 'report:compare:metformin:semaglutide')
  2. JSON Payload Serialization & Metadata Injection (cached: True, cached_at).
  3. TTL management (86,400s / 24 hours).
"""

import json
import logging
import time
from typing import Optional, Dict, Any, Tuple

from app.core.config import settings
from app.infrastructure.cache.redis_client import AsyncRedisClient
from app.services.synonym_service import SynonymResolver

logger = logging.getLogger(__name__)

# Single instance of AsyncRedisClient and SynonymResolver
_redis_client = AsyncRedisClient()
_synonym_resolver = SynonymResolver()


class CacheService:
    """
    Domain caching service handling canonical key formatting, JSON serialization,
    and metadata tagging.
    """

    def __init__(self, client: Optional[AsyncRedisClient] = None, resolver: Optional[SynonymResolver] = None):
        self._client = client or _redis_client
        self._resolver = resolver or _synonym_resolver

    def get_cache_key(self, query: str) -> Tuple[str, str]:
        """
        Generates canonical cache key with 'moleculeiq:' prefix and returns (cache_key, mode).

        Single Molecule: moleculeiq:report:semaglutide
        Comparison Mode: moleculeiq:report:compare:metformin:semaglutide
        """
        cleaned = query.strip()
        lower_q = cleaned.lower()

        # 1. Comparison Mode
        if " vs " in lower_q or " vs. " in lower_q:
            parts = lower_q.replace(" vs. ", " vs ").split(" vs ")
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                mol_a = self._resolver.resolve(parts[0].strip()).canonical_name.lower().strip()
                mol_b = self._resolver.resolve(parts[1].strip()).canonical_name.lower().strip()
                sorted_mols = sorted([mol_a, mol_b])
                key = f"moleculeiq:report:compare:{sorted_mols[0]}:{sorted_mols[1]}"
                return key, "comparison"

        # 2. Single Molecule Mode
        canonical = self._resolver.resolve(cleaned).canonical_name.lower().strip()
        key = f"moleculeiq:report:{canonical}"
        return key, "single"

    async def get_report(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Checks Redis for cached report JSON matching query.
        Returns parsed dictionary with metadata injected if HIT, None if MISS.
        """
        cache_key, mode = self.get_cache_key(query)
        json_str = await self._client.get(cache_key)

        if not json_str:
            return None

        try:
            data = json.loads(json_str)
            # Inject cache metadata
            data["cached"] = True
            data["processing_time_sec"] = 0.005
            logger.info("[CacheService] Served cached report for '%s' (key='%s')", query, cache_key)
            return data
        except Exception as exc:
            logger.warning("[CacheService] Failed to deserialize cached JSON for key='%s': %s", cache_key, str(exc))
            return None

    async def set_report(self, query: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        """
        Serializes and stores report dictionary in Redis with TTL configured via environment settings.
        """
        cache_key, mode = self.get_cache_key(query)
        ttl = ttl_seconds if ttl_seconds is not None else settings.REDIS_TTL_SECONDS

        try:
            # Tag metadata before storing
            data_to_store = dict(data)
            data_to_store["cached"] = True
            data_to_store["cached_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            json_str = json.dumps(data_to_store)
            success = await self._client.set(cache_key, json_str, ttl_seconds=ttl)
            if success:
                logger.info("[CacheService] Successfully cached report for '%s' (key='%s', TTL=%ds)", query, cache_key, ttl)
            return success
        except Exception as exc:
            logger.warning("[CacheService] Failed to serialize/store report for key='%s': %s", cache_key, str(exc))
            return False
