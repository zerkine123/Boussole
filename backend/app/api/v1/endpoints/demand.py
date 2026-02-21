# ============================================
# Boussole - Market Demand API
# ============================================

"""
API endpoints for market demand intelligence.

GET /api/v1/demand/score         — Demand score for sector + location
GET /api/v1/demand/opportunities — Ranked sector opportunities
GET /api/v1/demand/feasibility   — Full feasibility report
"""

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db, get_redis
from app.schemas.demand import DemandScore, FeasibilityReport, SectorOpportunity
from app.services.demand_intelligence_service import DemandIntelligenceService
from app.services.geo_cache_service import GeoCacheService
from app.services.geo_intelligence_service import GeoIntelligenceService

router = APIRouter()


def _build_service(db: AsyncSession, redis: Redis) -> DemandIntelligenceService:
    cache = GeoCacheService(redis)
    geo = GeoIntelligenceService(cache)
    return DemandIntelligenceService(db, geo_service=geo)


@router.get("/score", response_model=DemandScore)
async def get_demand_score(
    sector: str = Query(..., description="Sector slug (e.g. manufacturing, services)"),
    wilaya: Optional[str] = Query(None, description="Wilaya code (01-58)"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get the composite demand score (0-100) for a sector in a location."""
    service = _build_service(db, redis)
    return await service.compute_demand_score(sector, wilaya)


@router.get("/opportunities", response_model=list[SectorOpportunity])
async def get_sector_opportunities(
    wilaya: Optional[str] = Query(None, description="Wilaya code (01-58)"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get ranked sector opportunities for a location."""
    service = _build_service(db, redis)
    return await service.get_sector_opportunities(wilaya, limit)


@router.get("/feasibility", response_model=FeasibilityReport)
async def get_feasibility_report(
    sector: str = Query(..., description="Sector slug"),
    wilaya: Optional[str] = Query(None, description="Wilaya code (01-58)"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get a full market feasibility report for a sector in a location."""
    service = _build_service(db, redis)
    return await service.get_feasibility_report(sector, wilaya)
