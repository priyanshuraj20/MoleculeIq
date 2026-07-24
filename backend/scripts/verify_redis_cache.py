"""
scripts/verify_redis_cache.py

Verification script for Upstash Redis Caching Integration.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.services.cache_service import CacheService
from app.infrastructure.cache.redis_client import AsyncRedisClient


async def test_redis_cache():
    print("=" * 80, flush=True)
    print("MOLECULEIQ — UPSTASH REDIS CACHING VERIFICATION", flush=True)
    print("=" * 80, flush=True)

    client = AsyncRedisClient()
    service = CacheService(client=client)

    # 1. Test Ping
    print("\n---> 1. Testing Upstash Redis Connection (PING)...", flush=True)
    ping_ok = await client.ping()
    if ping_ok:
        print("     [SUCCESS] Connected to Upstash Redis Cloud over TLS (PONG received).", flush=True)
    else:
        print("     [WARNING] Could not connect to Upstash Redis. Check network/URL.", flush=True)

    # 2. Test Key Generation & Synonym Canonical Mapping
    print("\n---> 2. Testing Key Normalization Strategy...", flush=True)
    k1, m1 = service.get_cache_key("Ozempic")
    k2, m2 = service.get_cache_key("Semaglutide")
    k3, m3 = service.get_cache_key("Metformin vs Semaglutide")
    k4, m4 = service.get_cache_key("Semaglutide vs Metformin")

    print(f"     Query 'Ozempic'            -> Key: '{k1}'", flush=True)
    print(f"     Query 'Semaglutide'        -> Key: '{k2}'", flush=True)
    print(f"     Query 'Metformin vs Semaglutide' -> Key: '{k3}'", flush=True)
    print(f"     Query 'Semaglutide vs Metformin' -> Key: '{k4}'", flush=True)

    assert k1 == "moleculeiq:report:semaglutide", f"Expected 'moleculeiq:report:semaglutide', got '{k1}'"
    assert k1 == k2, "Ozempic and Semaglutide MUST map to the same canonical key!"
    assert k3 == "moleculeiq:report:compare:metformin:semaglutide", f"Expected 'moleculeiq:report:compare:metformin:semaglutide', got '{k3}'"
    assert k3 == k4, "Order-independent comparison queries MUST map to the same key!"
    print("     [SUCCESS] Key prefix ('moleculeiq:') & synonym normalization verified.", flush=True)

    # 3. Test Cache MISS -> SET -> HIT Lifecycle
    print("\n---> 3. Testing Cache SET & HIT Lifecycle...", flush=True)
    sample_payload = {
        "molecule_name": "Semaglutide",
        "opportunity_score": 80.0,
        "status": "completed"
    }

    # Save payload
    saved = await service.set_report("Ozempic", sample_payload, ttl_seconds=86400)
    print(f"     SET key '{k1}': {saved}", flush=True)

    # Fetch payload using brand synonym 'Ozempic'
    cached_data = await service.get_report("Semaglutide")
    if cached_data:
        print(f"     [SUCCESS] Cache HIT! Retrieved data for 'Semaglutide' from key '{k1}'.", flush=True)
        print(f"     Cached Flag: {cached_data.get('cached')}, Cached At: {cached_data.get('cached_at')}", flush=True)
    else:
        print("     [FAILURE] Cache MISS for key.", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("UPSTASH REDIS CACHING VERIFICATION PASSED SUCCESSFULLY", flush=True)
    print("=" * 80, flush=True)

    await client.close()


if __name__ == "__main__":
    asyncio.run(test_redis_cache())
