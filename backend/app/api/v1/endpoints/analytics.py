# ============================================
# Boussole - Analytics Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/sectors/{sector_slug}/summary")
async def get_sector_summary(
    sector_slug: str,
    period_start: Optional[str] = Query(None, description="Start period (e.g., '2024-01')"),
    period_end: Optional[str] = Query(None, description="End period (e.g., '2024-12')"),
    region: Optional[str] = Query(None, description="Filter by region"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary of analytics for a specific sector.
    
    - **sector_slug**: Sector identifier (e.g., 'agriculture', 'energy')
    - **period_start**: Start period for filtering
    - **period_end**: End period for filtering
    - **region**: Geographic region filter
    """
    service = AnalyticsService(db)
    summary = await service.get_sector_summary(
        sector_slug=sector_slug,
        period_start=period_start,
        period_end=period_end,
        region=region
    )
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found or no data available"
        )
    return summary


@router.get("/sectors/{sector_slug}/trends")
async def get_sector_trends(
    sector_slug: str,
    indicator_slug: Optional[str] = Query(None, description="Filter by indicator"),
    period_start: Optional[str] = Query(None, description="Start period"),
    period_end: Optional[str] = Query(None, description="End period"),
    region: Optional[str] = Query(None, description="Filter by region"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend data for a specific sector.
    
    Returns time-series data for visualization.
    """
    service = AnalyticsService(db)
    trends = await service.get_sector_trends(
        sector_slug=sector_slug,
        indicator_slug=indicator_slug,
        period_start=period_start,
        period_end=period_end,
        region=region
    )
    return trends


@router.get("/sectors/{sector_slug}/comparison")
async def get_sector_comparison(
    sector_slug: str,
    compare_with: List[str] = Query(..., description="List of sector slugs to compare with"),
    indicator_slug: Optional[str] = Query(None, description="Filter by indicator"),
    period: Optional[str] = Query(None, description="Specific period to compare"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare a sector with other sectors.
    
    - **compare_with**: List of sector slugs to compare (e.g., ['energy', 'manufacturing'])
    - **indicator_slug**: Optional indicator to focus comparison
    - **period**: Specific period for comparison
    """
    service = AnalyticsService(db)
    comparison = await service.get_sector_comparison(
        sector_slug=sector_slug,
        compare_with=compare_with,
        indicator_slug=indicator_slug,
        period=period
    )
    return comparison


@router.get("/regions/{region_code}/summary")
async def get_region_summary(
    region_code: str,
    period: Optional[str] = Query(None, description="Specific period (e.g., '2024')"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary of analytics for a specific region.
    
    - **region_code**: Region code (e.g., '01' for Algiers, '16' for Oran)
    - **period**: Specific period for filtering
    """
    service = AnalyticsService(db)
    summary = await service.get_region_summary(
        region_code=region_code,
        period=period
    )
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found or no data available"
        )
    return summary


@router.get("/indicators/{indicator_id}/forecast")
async def get_indicator_forecast(
    indicator_id: int,
    periods: int = Query(12, ge=1, le=36, description="Number of periods to forecast"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get forecast data for an indicator.
    
    - **periods**: Number of future periods to forecast (1-36)
    """
    service = AnalyticsService(db)
    forecast = await service.get_indicator_forecast(
        indicator_id=indicator_id,
        periods=periods
    )
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicator not found or insufficient historical data"
        )
    return forecast


@router.post("/export")
async def export_analytics(
    export_config: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Export analytics data in various formats.
    
    - **format**: Export format (csv, excel, json, pdf)
    - **data_type**: Type of data to export (sector, indicator, region)
    - **filters**: Optional filters for the data
    """
    service = AnalyticsService(db)
    export_result = await service.export_analytics(export_config)
    return export_result
