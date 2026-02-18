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
