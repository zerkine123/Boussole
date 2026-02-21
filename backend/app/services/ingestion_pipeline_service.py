# ============================================
# Boussole - Ingestion Pipeline Service
# ============================================

"""
Orchestrator that accepts NormalizedRecord instances from any connector
and upserts them into the database, creating or linking Indicators,
Sectors, and TimeSeriesData rows as needed.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.sector import Sector
from app.models.time_series_data import TimeSeriesData
from app.data_ingestion.connectors import NormalizedRecord

logger = logging.getLogger(__name__)


class IngestionPipelineService:
    """
    Takes a list of NormalizedRecord objects and persists them.

    Steps:
      1. Resolve sector (find or skip)
      2. Resolve indicator (find or create)
      3. Upsert TimeSeriesData row
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._sector_cache: Dict[str, int] = {}
        self._indicator_cache: Dict[str, int] = {}

    # ----- helpers -----

    async def _resolve_sector(self, slug: Optional[str]) -> Optional[int]:
        """Return sector id by slug, or None."""
        if not slug:
            return None
        if slug in self._sector_cache:
            return self._sector_cache[slug]

        result = await self.db.execute(
            select(Sector.id).where(Sector.slug == slug)
        )
        row = result.scalar_one_or_none()
        if row:
            self._sector_cache[slug] = row
        return row

    async def _resolve_indicator(
        self, name: str, sector_id: Optional[int]
    ) -> int:
        """Find indicator by slug or create a new one. Returns id."""
        slug = name.lower().replace(" ", "_").replace("-", "_")[:100]
        cache_key = f"{slug}_{sector_id}"

        if cache_key in self._indicator_cache:
            return self._indicator_cache[cache_key]

        result = await self.db.execute(
            select(Indicator).where(Indicator.slug == slug)
        )
        indicator = result.scalar_one_or_none()

        if not indicator:
            indicator = Indicator(
                slug=slug,
                name_en=name,
                name_fr=name,
                name_ar=name,
                sector_id=sector_id or 1,  # fallback to first sector
            )
            self.db.add(indicator)
            await self.db.flush()  # assign id
            logger.info(f"Created new indicator: {slug} (id={indicator.id})")

        self._indicator_cache[cache_key] = indicator.id
        return indicator.id

    # ----- main entry -----

    async def ingest(
        self, records: List[NormalizedRecord]
    ) -> Dict[str, Any]:
        """
        Persist a batch of normalised records.

        Returns summary dict:
          created, updated, skipped, errors
        """
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        for rec in records:
            try:
                sector_id = await self._resolve_sector(rec.sector)
                indicator_id = await self._resolve_indicator(
                    rec.indicator_name, sector_id
                )

                # Check for existing row (same indicator + year + period)
                existing = await self.db.execute(
                    select(TimeSeriesData).where(
                        TimeSeriesData.indicator_id == indicator_id,
                        TimeSeriesData.year == rec.year,
                        TimeSeriesData.period == rec.period,
                        TimeSeriesData.quarter == rec.quarter,
                        TimeSeriesData.month == rec.month,
                    )
                )
                row = existing.scalar_one_or_none()

                if row:
                    # Update existing
                    row.value = rec.value
                    row.unit = rec.unit or row.unit
                    row.source = rec.source or row.source
                    row.source_url = rec.source_url or row.source_url
                    row.updated_at = datetime.utcnow()
                    stats["updated"] += 1
                else:
                    # Insert new
                    ts = TimeSeriesData(
                        indicator_id=indicator_id,
                        sector_id=sector_id or 1,
                        wilaya_id=None,  # TODO: resolve from wilaya_code
                        period=rec.period,
                        year=rec.year,
                        quarter=rec.quarter,
                        month=rec.month,
                        value=rec.value,
                        unit=rec.unit,
                        source=rec.source,
                        source_url=rec.source_url,
                    )
                    self.db.add(ts)
                    stats["created"] += 1

            except Exception as e:
                logger.warning(f"Error ingesting record '{rec.indicator_name}': {e}")
                stats["errors"] += 1

        await self.db.commit()
        logger.info(f"Ingestion complete: {stats}")
        return stats
