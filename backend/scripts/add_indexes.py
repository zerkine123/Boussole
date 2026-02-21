"""
Script to add performance indexes to the metrics table.
Run from the backend directory: python scripts/add_indexes.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine

async def create_indexes():
    print("Creating indexes on metrics table...")
    async with engine.begin() as conn:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_metric_slug ON metrics (slug)",
            "CREATE INDEX IF NOT EXISTS idx_metric_year ON metrics (year)",
            "CREATE INDEX IF NOT EXISTS idx_metric_sector_id ON metrics (sector_id)",
            "CREATE INDEX IF NOT EXISTS idx_metric_wilaya_id ON metrics (wilaya_id)",
            "CREATE INDEX IF NOT EXISTS idx_metric_slug_year ON metrics (slug, year)",
        ]
        for sql in indexes:
            await conn.execute(text(sql))
            print(f"  ✓ {sql.split('idx_')[1].split(' ON')[0]}")
    print("All indexes created successfully!")

if __name__ == "__main__":
    asyncio.run(create_indexes())
