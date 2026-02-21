# ============================================
# Boussole - Data Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.data_point import DataPoint, DataPointCreate, DataPointUpdate, DataPointBulkCreate, DataPointQuery
from app.services.data_service import DataService

router = APIRouter()


@router.get("/indicators", response_model=List[dict])
async def list_indicators(
    sector_id: Optional[int] = Query(None, description="Filter by sector ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all indicators with optional filtering.
    
    - **sector_id**: Filter by sector ID (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    service = DataService(db)
    return await service.list_indicators(sector_id=sector_id, skip=skip, limit=limit)


@router.get("/indicators/{indicator_id}", response_model=dict)
async def get_indicator(
    indicator_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific indicator by ID.
    """
    service = DataService(db)
    indicator = await service.get_indicator_by_id(indicator_id)
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicator not found"
        )
    return indicator


@router.get("/data-points", response_model=List[DataPoint])
async def list_data_points(
    indicator_id: Optional[int] = Query(None, description="Filter by indicator ID"),
    sector_id: Optional[int] = Query(None, description="Filter by sector ID"),
    region: Optional[str] = Query(None, description="Filter by region"),
    period_start: Optional[str] = Query(None, description="Filter by period start (e.g., '2024-01')"),
    period_end: Optional[str] = Query(None, description="Filter by period end (e.g., '2024-12')"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    List data points with optional filtering.
    """
    service = DataService(db)
    return await service.list_data_points(
        indicator_id=indicator_id,
        sector_id=sector_id,
        region=region,
        period_start=period_start,
        period_end=period_end,
        is_verified=is_verified,
        skip=skip,
        limit=limit
    )


@router.get("/data-points/{data_point_id}", response_model=DataPoint)
async def get_data_point(
    data_point_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific data point by ID.
    """
    service = DataService(db)
    data_point = await service.get_data_point_by_id(data_point_id)
    if not data_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found"
        )
    return data_point


@router.post("/data-points", response_model=DataPoint, status_code=status.HTTP_201_CREATED)
async def create_data_point(
    data_point: DataPointCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new data point.
    """
    service = DataService(db)
    return await service.create_data_point(data_point)


@router.post("/data-points/bulk", response_model=List[DataPoint], status_code=status.HTTP_201_CREATED)
async def bulk_create_data_points(
    bulk_data: DataPointBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk create multiple data points.
    """
    service = DataService(db)
    return await service.bulk_create_data_points(bulk_data.data_points)


@router.put("/data-points/{data_point_id}", response_model=DataPoint)
async def update_data_point(
    data_point_id: int,
    data_point_update: DataPointUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing data point.
    """
    service = DataService(db)
    updated_data_point = await service.update_data_point(data_point_id, data_point_update)
    if not updated_data_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found"
        )
    return updated_data_point


@router.delete("/data-points/{data_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_point(
    data_point_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a data point.
    """
    service = DataService(db)
    success = await service.delete_data_point(data_point_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found"
        )


from pydantic import BaseModel
from typing import Literal, Dict, Any

class DataQueryRequest(BaseModel):
    metric_slugs: List[str]
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

@router.post("/query")
async def execute_data_query(
    request: DataQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Universal data query endpoint for Dashboard widgets.
    Uses aggregated SQL queries for performance on large datasets.
    """
    from sqlalchemy import select, func, and_
    from app.models.metric import Metric
    from app.models.sector import Sector
    from app.models.wilaya import Wilaya

    # Normalize group_by
    VALID_GROUP_BY = {"year", "month", "sector", "wilaya"}
    group_by = request.group_by if request.group_by in VALID_GROUP_BY else None

    filters = request.filters or {}

    # ── Build aggregated query ─────────────────────────────────
    # Select: SUM(value), sector fields, wilaya fields, year, slug, unit, trend, change_percent
    query = (
        select(
            Metric.slug,
            Metric.unit,
            Metric.year,
            Metric.trend,
            Metric.change_percent,
            func.sum(Metric.value).label("value"),
            func.avg(Metric.change_percent).label("avg_change"),
            Sector.name_en.label("sector_name"),
            Sector.slug.label("sector_slug"),
            Wilaya.name_en.label("wilaya_name"),
            Wilaya.code.label("wilaya_code"),
        )
        .join(Sector, Metric.sector_id == Sector.id)
        .join(Wilaya, Metric.wilaya_id == Wilaya.id)
        .where(Metric.slug.in_(request.metric_slugs))
    )

    # ── Apply filters using WHERE (not extra joins) ────────────
    conditions = []

    if filters.get("sector_slug"):
        conditions.append(Sector.slug == str(filters["sector_slug"]))

    if filters.get("wilaya_code"):
        # Wilaya codes are like "16", "31" etc - ensure string comparison
        conditions.append(Wilaya.code == str(filters["wilaya_code"]).zfill(2))

    if filters.get("start_year"):
        try:
            conditions.append(Metric.year >= int(filters["start_year"]))
        except (ValueError, TypeError):
            pass

    if filters.get("end_year"):
        try:
            conditions.append(Metric.year <= int(filters["end_year"]))
        except (ValueError, TypeError):
            pass

    # Only include latest year by default if no year filter - prevents overwhelming results
    if not filters.get("start_year") and not filters.get("end_year") and not group_by == "year":
        conditions.append(Metric.year == 2024)

    if conditions:
        query = query.where(and_(*conditions))

    # ── GROUP BY dimension ─────────────────────────────────────
    if group_by == "year":
        query = query.group_by(
            Metric.slug, Metric.unit, Metric.year, Metric.trend, Metric.change_percent,
            Sector.name_en, Sector.slug, Wilaya.name_en, Wilaya.code
        ).order_by(Metric.year)
    elif group_by == "sector":
        query = query.group_by(
            Metric.slug, Metric.unit, Sector.name_en, Sector.slug, Wilaya.name_en, Wilaya.code,
            Metric.year, Metric.trend, Metric.change_percent
        ).order_by(Sector.name_en)
    elif group_by == "wilaya":
        query = query.group_by(
            Metric.slug, Metric.unit, Wilaya.name_en, Wilaya.code, Sector.name_en, Sector.slug,
            Metric.year, Metric.trend, Metric.change_percent
        ).order_by(Wilaya.name_en)
    else:
        # No specific grouping - just aggregate all matching rows per slug
        query = query.group_by(
            Metric.slug, Metric.unit, Sector.name_en, Sector.slug, Wilaya.name_en, Wilaya.code,
            Metric.year, Metric.trend, Metric.change_percent
        )

    # Limit results to prevent huge payloads
    query = query.limit(500)

    result = await db.execute(query)
    rows = result.mappings().all()

    data = []
    for row in rows:
        data.append({
            "metric_slug": row["slug"],
            "value": float(row["value"] or 0),
            "unit": row["unit"],
            "year": row["year"],
            "trend": row["trend"],
            "change_percent": float(row["avg_change"] or 0),
            "sector_name": row["sector_name"] or "Unknown",
            "sector_slug": row["sector_slug"] or "unknown",
            "wilaya_name": row["wilaya_name"] or "Unknown",
            "wilaya_code": row["wilaya_code"] or "Unknown",
        })

    return {"data": data}
