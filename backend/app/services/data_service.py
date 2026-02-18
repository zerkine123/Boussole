# ============================================
# Boussole - Data Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from app.models.indicator import Indicator
from app.models.sector import Sector
from app.models.data_point import DataPoint
from app.schemas.data_point import DataPointCreate, DataPointUpdate


class DataService:
    """
    Service layer for data operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Indicator methods
    async def list_indicators(
        self,
        sector_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        List indicators with optional filtering.
        """
        query = select(Indicator)
        
        if sector_id:
            query = query.where(Indicator.sector_id == sector_id)
        
        query = query.where(Indicator.is_active == True)
        query = query.offset(skip).limit(limit)
        
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
    
    async def get_indicator_by_id(self, indicator_id: int) -> Optional[dict]:
        """
        Get an indicator by ID.
        """
        result = await self.db.execute(
            select(Indicator).where(Indicator.id == indicator_id)
        )
        indicator = result.scalar_one_or_none()
        
        if not indicator:
            return None
        
        return {
            "id": indicator.id,
            "sector_id": indicator.sector_id,
            "slug": indicator.slug,
            "code": indicator.code,
            "name_en": indicator.name_en,
            "name_fr": indicator.name_fr,
            "name_ar": indicator.name_ar,
            "description_en": indicator.description_en,
            "description_fr": indicator.description_fr,
            "description_ar": indicator.description_ar,
            "unit": indicator.unit,
            "frequency": indicator.frequency,
            "source": indicator.source,
            "is_active": indicator.is_active,
            "created_at": indicator.created_at,
            "updated_at": indicator.updated_at,
        }
    
    # Data Point methods
    async def list_data_points(
        self,
        indicator_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        region: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        is_verified: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DataPoint]:
        """
        List data points with optional filtering.
        """
        query = select(DataPoint)
        
        conditions = []
        
        if indicator_id:
            conditions.append(DataPoint.indicator_id == indicator_id)
        
        if sector_id:
            query = query.join(Indicator)
            conditions.append(Indicator.sector_id == sector_id)
        
        if region:
            conditions.append(DataPoint.region == region)
        
        if period_start:
            conditions.append(DataPoint.period >= period_start)
        
        if period_end:
            conditions.append(DataPoint.period <= period_end)
        
        if is_verified is not None:
            conditions.append(DataPoint.is_verified == is_verified)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        query = query.order_by(DataPoint.period.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_data_point_by_id(self, data_point_id: int) -> Optional[DataPoint]:
        """
        Get a data point by ID.
        """
        result = await self.db.execute(
            select(DataPoint).where(DataPoint.id == data_point_id)
        )
        return result.scalar_one_or_none()
    
    async def create_data_point(self, data_point_data: DataPointCreate) -> DataPoint:
        """
        Create a new data point.
        """
        db_data_point = DataPoint(**data_point_data.model_dump())
        self.db.add(db_data_point)
        await self.db.commit()
        await self.db.refresh(db_data_point)
        return db_data_point
    
    async def bulk_create_data_points(
        self,
        data_points_list: List[DataPointCreate]
    ) -> List[DataPoint]:
        """
        Bulk create multiple data points.
        """
        db_data_points = [
            DataPoint(**dp.model_dump()) for dp in data_points_list
        ]
        self.db.add_all(db_data_points)
        await self.db.commit()
        
        for dp in db_data_points:
            await self.db.refresh(dp)
        
        return db_data_points
    
    async def update_data_point(
        self,
        data_point_id: int,
        data_point_update: DataPointUpdate
    ) -> Optional[DataPoint]:
        """
        Update an existing data point.
        """
        db_data_point = await self.get_data_point_by_id(data_point_id)
        if not db_data_point:
            return None
        
        update_data = data_point_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_data_point, field, value)
        
        db_data_point.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(db_data_point)
        
        return db_data_point
    
    async def delete_data_point(self, data_point_id: int) -> bool:
        """
        Delete a data point.
        """
        db_data_point = await self.get_data_point_by_id(data_point_id)
        if not db_data_point:
            return False
        
        await self.db.delete(db_data_point)
        await self.db.commit()
        
        return True
