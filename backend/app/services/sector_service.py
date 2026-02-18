# ============================================
# Boussole - Sector Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.models.sector import Sector
from app.models.indicator import Indicator
from app.schemas.sector import SectorCreate, SectorUpdate


class SectorService:
    """
    Service layer for sector operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_sectors(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Sector]:
        """
        Get all sectors with optional filtering.
        """
        query = select(Sector)
        
        if active_only:
            query = query.where(Sector.is_active == True)
        
        query = query.offset(skip).limit(limit)
        query = query.order_by(Sector.name_en)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, sector_id: int) -> Optional[Sector]:
        """
        Get sector by ID.
        """
        result = await self.db.execute(
            select(Sector).where(Sector.id == sector_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Sector]:
        """
        Get sector by slug.
        """
        result = await self.db.execute(
            select(Sector).where(Sector.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def create(self, sector_data: SectorCreate) -> Sector:
        """
        Create a new sector.
        """
        db_sector = Sector(**sector_data.model_dump())
        self.db.add(db_sector)
        await self.db.commit()
        await self.db.refresh(db_sector)
        return db_sector
    
    async def update(self, slug: str, sector_data: SectorUpdate) -> Optional[Sector]:
        """
        Update an existing sector.
        """
        db_sector = await self.get_by_slug(slug)
        if not db_sector:
            return None
        
        update_data = sector_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sector, field, value)
        
        db_sector.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(db_sector)
        
        return db_sector
    
    async def delete(self, slug: str) -> bool:
        """
        Delete a sector.
        """
        db_sector = await self.get_by_slug(slug)
        if not db_sector:
            return False
        
        await self.db.delete(db_sector)
        await self.db.commit()
        
        return True
    
    async def get_sector_indicators(
        self,
        sector_slug: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Get all indicators for a specific sector.
        """
        sector = await self.get_by_slug(sector_slug)
        if not sector:
            return []
        
        query = select(Indicator).where(
            and_(
                Indicator.sector_id == sector.id,
                Indicator.is_active == True
            )
        )
        query = query.offset(skip).limit(limit)
        query = query.order_by(Indicator.name_en)
        
        result = await self.db.execute(query)
        indicators = result.scalars().all()
        
        return [
            {
                "id": ind.id,
                "sector_id": ind.sector_id,
                "slug": ind.slug,
                "code": ind.code,
                "name_en": ind.name_en,
                "name_fr": ind.name_fr,
                "name_ar": ind.name_ar,
                "description_en": ind.description_en,
                "description_fr": ind.description_fr,
                "description_ar": ind.description_ar,
                "unit": ind.unit,
                "frequency": ind.frequency,
                "source": ind.source,
            }
            for ind in indicators
        ]
