# ============================================
# Boussole - Geographic Intelligence API
# ============================================

"""
API endpoints for geographic intelligence.

POST /api/v1/geo/intelligence       — Full area intelligence report
GET  /api/v1/geo/places             — Nearby places search
GET  /api/v1/geo/activity-score     — Composite activity score only
GET  /api/v1/geo/wilaya/{code}      — Intelligence for a specific wilaya
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db, get_redis
from app.models.wilaya import Wilaya
from app.schemas.geo import (
    AreaActivityScore,
    GeoIntelligenceResponse,
    LocationQuery,
    PlacePopularity,
)
from app.services.geo_cache_service import GeoCacheService
from app.services.geo_intelligence_service import GeoIntelligenceService

router = APIRouter()


def _build_service(redis: Redis) -> GeoIntelligenceService:
    cache = GeoCacheService(redis)
    return GeoIntelligenceService(cache)


@router.post("/intelligence", response_model=GeoIntelligenceResponse)
async def get_intelligence(
    query: LocationQuery,
    redis: Redis = Depends(get_redis),
):
    """
    Full geographic intelligence report for a location.
    Returns activity score, traffic density, and nearby places.
    """
    service = _build_service(redis)
    return await service.get_area_intelligence(
        lat=query.lat,
        lon=query.lon,
        radius=query.radius,
        place_type=query.place_type.value if query.place_type else None,
    )


@router.get("/places", response_model=list[PlacePopularity])
async def get_nearby_places(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: int = Query(1000, ge=100, le=50000),
    place_type: Optional[str] = Query(None),
    redis: Redis = Depends(get_redis),
):
    """Search for nearby places around a coordinate."""
    service = _build_service(redis)
    return await service.get_nearby_places(lat, lon, radius, place_type)


@router.get("/activity-score", response_model=AreaActivityScore)
async def get_activity_score(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: int = Query(1000, ge=100, le=50000),
    redis: Redis = Depends(get_redis),
):
    """Get the composite activity score (0-100) for a location."""
    service = _build_service(redis)
    return await service.compute_activity_score(lat, lon, radius)


@router.get("/wilaya/{code}", response_model=GeoIntelligenceResponse)
async def get_wilaya_intelligence(
    code: str,
    radius: int = Query(2000, ge=100, le=50000),
    place_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Get geographic intelligence for a specific wilaya.
    Uses the wilaya's stored latitude/longitude as the center point.
    """
    # Resolve wilaya
    result = await db.execute(
        select(Wilaya).where(Wilaya.code == code)
    )
    wilaya = result.scalar_one_or_none()

    if not wilaya:
        raise HTTPException(status_code=404, detail=f"Wilaya '{code}' not found")

    if not wilaya.latitude or not wilaya.longitude:
        raise HTTPException(
            status_code=422,
            detail=f"Wilaya '{code}' ({wilaya.name_en}) has no coordinates",
        )

    service = _build_service(redis)
    return await service.get_area_intelligence(
        lat=wilaya.latitude,
        lon=wilaya.longitude,
        radius=radius,
        place_type=place_type,
    )
