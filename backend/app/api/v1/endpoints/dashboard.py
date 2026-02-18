# ============================================
# Boussole - Dashboard Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.db.session import get_db
from app.schemas.metric import (
    Metric,
    MetricWithWilaya,
    DashboardKPI,
    WilayaHeatmapData,
)
from app.services.data_service import DataService
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/kpis", response_model=List[DashboardKPI])
async def get_dashboard_kpis(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(6, ge=1, le=20, description="Number of KPIs to return"),
):
    """
    Get dashboard KPI cards based on user preferences.
    
    Returns top metrics by value or change, grouped by sector if specified.
    """
    # Build query
    query = select(Metric).where(Metric.is_verified == True)
    
    if sector_slug:
        # Join with sector to filter
        query = query.join(Metric.sector).where(Sector.slug == sector_slug)
    
    query = query.order_by(Metric.value.desc()).limit(limit)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    # Format as KPI cards
    kpis = []
    for metric in metrics:
        # Determine trend icon and color
        trend_icon = "trending-up" if metric.trend == "up" else "trending-down" if metric.trend == "down" else "minus"
        trend_color = "#22c55e" if metric.trend == "up" else "#ef4444" if metric.trend == "down" else "#6b7280"
        
        kpis.append(DashboardKPI(
            title=metric.name_en,
            value=metric.value,
            unit=metric.unit,
            change_percent=metric.change_percent,
            trend=metric.trend,
            period=metric.period,
            icon="chart-line",
            color=trend_color,
        ))
    
    return kpis


@router.get("/wilaya-heatmap", response_model=List[WilayaHeatmapData])
async def get_wilaya_heatmap(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    metric_slug: Optional[str] = Query(None, description="Filter by metric"),
    period: Optional[str] = Query(None, description="Filter by period"),
):
    """
    Get Wilaya heatmap data for visualization.
    
    Returns metrics aggregated by Wilaya for map visualization.
    """
    # Build query
    query = select(Metric, Wilaya).join(Metric.wilaya)
    
    if sector_slug:
        query = query.join(Metric.sector).where(Sector.slug == sector_slug)
    
    if metric_slug:
        # This would require a separate relationship or join logic
        # For now, we'll just filter by sector and period
        pass
    
    if period:
        query = query.where(Metric.period == period)
    
    query = query.where(Metric.is_verified == True)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Format as heatmap data
    heatmap_data = []
    for metric, wilaya in rows:
        heatmap_data.append(WilayaHeatmapData(
            wilaya_code=wilaya.code,
            wilaya_name_en=wilaya.name_en,
            wilaya_name_fr=wilaya.name_fr,
            wilaya_name_ar=wilaya.name_ar,
            latitude=wilaya.latitude,
            longitude=wilaya.longitude,
            value=metric.value,
            unit=metric.unit,
        ))
    
    return heatmap_data


@router.get("/metrics", response_model=List[MetricWithWilaya])
async def get_dashboard_metrics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    wilaya_code: Optional[str] = Query(None, description="Filter by Wilaya code"),
    period_start: Optional[str] = Query(None, description="Start period"),
    period_end: Optional[str] = Query(None, description="End period"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get metrics for dashboard with filters.
    """
    service = DataService(db)
    
    # Get metrics with filters
    # This would require additional query logic
    # For now, we'll return a simplified list
    
    # Placeholder implementation
    # In production, implement proper filtering by sector, Wilaya, and period
    result = await db.execute(
        select(Metric)
        .where(Metric.is_verified == True)
        .order_by(Metric.period.desc())
        .offset(skip)
        .limit(limit)
    )
    metrics = result.scalars().all()
    
    # Format with Wilaya details
    formatted_metrics = []
    for metric in metrics:
        # Get Wilaya name (would require join in production)
        formatted_metrics.append(MetricWithWilaya(
            id=metric.id,
            wilaya_id=metric.wilaya_id,
            slug=metric.slug,
            name_en=metric.name_en,
            name_fr=metric.name_fr,
            name_ar=metric.name_ar,
            value=metric.value,
            unit=metric.unit,
            period=metric.period,
            year=metric.year,
            quarter=metric.quarter,
            change_percent=metric.change_percent,
            change_value=metric.change_value,
            trend=metric.trend,
            is_verified=metric.is_verified,
            is_featured=metric.is_featured,
            created_at=metric.created_at,
            updated_at=metric.updated_at,
            # Placeholder Wilaya details
            wilaya_code="",
            wilaya_name_en="",
            wilaya_name_fr="",
            wilaya_name_ar="",
        ))
    
    return formatted_metrics


@router.get("/summary")
async def get_dashboard_summary(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard summary statistics.
    """
    # Get total counts
    metrics_count = await db.execute(
        select(func.count(Metric.id)).where(Metric.is_verified == True)
    )
    total_metrics = metrics_count.scalar()
    
    sectors_count = await db.execute(
        select(func.count(Sector.id)).where(Sector.is_active == True)
    )
    total_sectors = sectors_count.scalar()
    
    wilayas_count = await db.execute(
        select(func.count(Wilaya.id)).where(Wilaya.is_active == True)
    )
    total_wilayas = wilayas_count.scalar()
    
    return {
        "total_metrics": total_metrics,
        "total_sectors": total_sectors,
        "total_wilayas": total_wilayas,
        "user_id": current_user.id,
        "user_email": current_user.email,
    }
