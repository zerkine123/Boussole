import asyncio
import sys
import os

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import async_session
from app.models.wilaya import Wilaya
from sqlalchemy import select

async def main():
    print("Checking Wilaya 16 in DB...")
    async with async_session() as db:
        try:
            stmt = select(Wilaya).where(Wilaya.code == "16")
            result = await db.execute(stmt)
            w = result.scalar_one_or_none()
            if w:
                print(f"Found Wilaya 16: {w.name}")
                print(f"Latitude: {w.latitude}")
                print(f"Longitude: {w.longitude}")
            else:
                print("Wilaya 16 NOT FOUND in DB.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
