import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import async_session
from app.models.wilaya import Wilaya
from sqlalchemy import select

async def main():
    print("Seeding Wilaya 16 (Algiers)...")
    async with async_session() as db:
        try:
            stmt = select(Wilaya).where(Wilaya.code == "16")
            result = await db.execute(stmt)
            w = result.scalar_one_or_none()
            
            if w:
                print(f"Found Wilaya 16: {w.name_en}")
                print("Updating coordinates...")
                w.latitude = 36.752887
                w.longitude = 3.042048
                # Ensure region is set
                if not w.region:
                    w.region = "Central"
                await db.commit()
                print("Updated Algiers.")
            else:
                print("Creating Wilaya 16...")
                w = Wilaya(
                    code="16",
                    name_en="Algiers",
                    name_fr="Alger",
                    name_ar="الجزائر",
                    name_arabic="الجزائر",
                    latitude=36.752887,
                    longitude=3.042048,
                    region="Central",
                    area_km2=1190.0,
                    population=2988145
                )
                db.add(w)
                await db.commit()
                print("Created Algiers.")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
