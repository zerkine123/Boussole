# ============================================
# Boussole - Geo Cache Service
# ============================================

"""
Redis-backed caching layer for Google Maps API responses.
Keys are structured as: geo:{api}:{lat_3dp}:{lon_3dp}:{radius}
Gracefully degrades if Redis is unavailable.
"""

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeoCacheService:
    """
    Thin wrapper around Redis for geographic data caching.
    Rounds lat/lon to 3 decimal places (~111 m precision)
    to maximise cache hits for nearby queries.
    """

    def __init__(self, redis: Optional[Redis] = None):
        self.redis = redis
        self.prefix = settings.GEO_CACHE_PREFIX
        self.ttl = settings.GEO_CACHE_TTL

    @staticmethod
    def _round_coord(val: float, decimals: int = 3) -> str:
        return f"{round(val, decimals):.{decimals}f}"

    def _build_key(self, api: str, lat: float, lon: float, extra: str = "") -> str:
        lat_r = self._round_coord(lat)
        lon_r = self._round_coord(lon)
        parts = [self.prefix + api, lat_r, lon_r]
        if extra:
            parts.append(extra)
        return ":".join(parts)

    async def get(self, api: str, lat: float, lon: float, extra: str = "") -> Optional[Any]:
        """Return cached JSON data or None."""
        if not self.redis:
            return None
        try:
            key = self._build_key(api, lat, lon, extra)
            raw = await self.redis.get(key)
            if raw:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(raw)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")
            return None

    async def set(self, api: str, lat: float, lon: float, data: Any, extra: str = "", ttl: Optional[int] = None) -> None:
        """Store JSON data with TTL."""
        if not self.redis:
            return
        try:
            key = self._build_key(api, lat, lon, extra)
            await self.redis.setex(
                key,
                ttl or self.ttl,
                json.dumps(data, default=str),
            )
            logger.debug(f"Cached: {key} (TTL={ttl or self.ttl}s)")
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")

    async def invalidate(self, api: str, lat: float, lon: float, extra: str = "") -> None:
        """Remove a specific cache entry."""
        if not self.redis:
            return
        try:
            key = self._build_key(api, lat, lon, extra)
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis cache invalidation failed: {e}")
