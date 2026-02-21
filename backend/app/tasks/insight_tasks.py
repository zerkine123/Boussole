# ============================================
# Boussole - Insight Tasks
# ============================================

import asyncio
from typing import List, Optional
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.insights_engine import InsightsEngineService
from app.models.sector import Sector
from sqlalchemy import select


async def _generate_insights_for_all_sectors():
    """Async helper to generate insights for all active sectors."""
    async with SessionLocal() as db:
        # Get all active sectors
        result = await db.execute(select(Sector).where(Sector.is_active == True))
        sectors = result.scalars().all()
        
        service = InsightsEngineService(db)
        
        # Determine period: e.g., current year or latest available
        current_year = str(datetime.now().year)
        
        for sector in sectors:
            try:
                # Generate insights for each sector
                await service.generate_insights_for_sector(
                    sector_slug=sector.slug,
                    period_end=current_year
                )
            except Exception as e:
                print(f"Error generating insights for sector {sector.slug}: {e}")


@celery_app.task(name="app.tasks.insight_tasks.generate_weekly_insights")
def generate_weekly_insights():
    """
    Celery task to generate insights for all sectors on a weekly basis.
    This runs the async logic synchronously in the Celery worker.
    """
    # Create a new event loop for the async execution
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        loop.run_until_complete(_generate_insights_for_all_sectors())
        return {"status": "success", "message": "Weekly insights generated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
