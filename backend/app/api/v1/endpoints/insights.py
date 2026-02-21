# ============================================
# Boussole - Insights Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.insight import InsightResponse, InsightWithDetailsResponse, InsightCreate
from app.services.insights_engine import InsightsEngineService
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[InsightWithDetailsResponse])
async def get_insights(
    sector_id: Optional[int] = Query(None, description="Filter insights by sector ID"),
    limit: int = Query(10, ge=1, le=100, description="Max number of insights to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the latest generated insights.
    """
    service = InsightsEngineService(db)
    insights = await service.get_latest_insights(limit=limit, sector_id=sector_id)
    return insights


@router.post("/generate", response_model=List[InsightResponse])
async def generate_insights(
    sector_slug: str = Query(..., description="Slug of the sector to analyze"),
    period_start: Optional[str] = Query(None, description="Start period (e.g. 2024-01)"),
    period_end: Optional[str] = Query(None, description="End period (e.g. 2024-12)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger the AI Engine to generate insights for a given sector and time period.
    Only accessible by authenticated users.
    """
    service = InsightsEngineService(db)
    try:
        insights = await service.generate_insights_for_sector(
            sector_slug=sector_slug,
            period_start=period_start,
            period_end=period_end
        )
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )
