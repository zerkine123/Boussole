# ============================================
# Boussole - Sectors Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.sector import SectorCreate, SectorUpdate, Sector
from app.services.sector_service import SectorService

router = APIRouter()


@router.get("/", response_model=List[Sector])
async def list_sectors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Only return active sectors"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all sectors with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **active_only**: Only return active sectors
    """
    service = SectorService(db)
    return await service.list_sectors(skip=skip, limit=limit, active_only=active_only)


@router.get("/{slug}", response_model=Sector)
async def get_sector(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific sector by slug.
    
    - **slug**: Sector identifier (e.g., 'agriculture', 'energy')
    """
    service = SectorService(db)
    sector = await service.get_by_slug(slug)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
    return sector


@router.get("/{slug}/indicators")
async def get_sector_indicators(
    slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all indicators for a specific sector.
    """
    service = SectorService(db)
    indicators = await service.get_sector_indicators(slug, skip=skip, limit=limit)
    if not indicators:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found or no indicators available"
        )
    return indicators


@router.post("/", response_model=Sector, status_code=status.HTTP_201_CREATED)
async def create_sector(
    sector: SectorCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new sector.
    
    - **slug**: Unique sector identifier (e.g., 'agriculture')
    - **name_en**: Sector name in English
    - **name_fr**: Sector name in French
    - **name_ar**: Sector name in Arabic
    - **description_en**: Description in English
    - **description_fr**: Description in French
    - **description_ar**: Description in Arabic
    - **icon**: Icon identifier (e.g., 'leaf', 'zap', 'factory')
    - **color**: Hex color code (e.g., '#22c55e')
    """
    service = SectorService(db)
    return await service.create(sector)


@router.put("/{slug}", response_model=Sector)
async def update_sector(
    slug: str,
    sector: SectorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing sector.
    """
    service = SectorService(db)
    updated_sector = await service.update(slug, sector)
    if not updated_sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
    return updated_sector


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sector(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a sector.
    
    ⚠️ This will also delete all associated indicators and data points.
    """
    service = SectorService(db)
    success = await service.delete(slug)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
