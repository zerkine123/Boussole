# ============================================
# Boussole - Database Initialization
# ============================================

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import async_session, engine
from app.core.security import get_password_hash


async def create_extensions():
    """
    Create required PostgreSQL extensions.
    """
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))


async def create_initial_superuser():
    """
    Create the initial superuser if it doesn't exist.
    """
    from app.models.user import User
    
    async with async_session() as session:
        # Check if superuser already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@boussole.dz'")
        )
        existing_user = result.fetchone()
        
        if not existing_user:
            # Create superuser
            superuser = User(
                email="admin@boussole.dz",
                full_name="Boussole Administrator",
                hashed_password=get_password_hash("admin123"),  # Change in production!
                is_active=True,
                is_superuser=True,
            )
            session.add(superuser)
            await session.commit()
            print("✓ Initial superuser created: admin@boussole.dz / admin123")
        else:
            print("✓ Superuser already exists")


async def create_initial_sectors():
    """
    Create initial sectors if they don't exist.
    """
    from app.models.sector import Sector
    
    sectors_data = [
        {
            "slug": "agriculture",
            "name_en": "Agriculture",
            "name_fr": "Agriculture",
            "name_ar": "الزراعة",
            "description_en": "Agricultural production and statistics",
            "description_fr": "Production agricole et statistiques",
            "description_ar": "الإنتاج الزراعي والإحصاءات",
            "icon": "leaf",
            "color": "#22c55e",
            "is_active": True,
        },
        {
            "slug": "energy",
            "name_en": "Energy",
            "name_fr": "Énergie",
            "name_ar": "الطاقة",
            "description_en": "Energy production and consumption",
            "description_fr": "Production et consommation d'énergie",
            "description_ar": "إنتاج واستهلاك الطاقة",
            "icon": "zap",
            "color": "#eab308",
            "is_active": True,
        },
        {
            "slug": "manufacturing",
            "name_en": "Manufacturing",
            "name_fr": "Industrie",
            "name_ar": "الصناعة",
            "description_en": "Industrial production and manufacturing",
            "description_fr": "Production industrielle et fabrication",
            "description_ar": "الإنتاج الصناعي والتصنيع",
            "icon": "factory",
            "color": "#3b82f6",
            "is_active": True,
        },
        {
            "slug": "services",
            "name_en": "Services",
            "name_fr": "Services",
            "name_ar": "الخدمات",
            "description_en": "Service sector statistics",
            "description_fr": "Statistiques du secteur des services",
            "description_ar": "إحصائيات قطاع الخدمات",
            "icon": "briefcase",
            "color": "#a855f7",
            "is_active": True,
        },
        {
            "slug": "tourism",
            "name_en": "Tourism",
            "name_fr": "Tourisme",
            "name_ar": "السياحة",
            "description_en": "Tourism statistics and data",
            "description_fr": "Statistiques et données touristiques",
            "description_ar": "الإحصاءات والبيانات السياحية",
            "icon": "plane",
            "color": "#f97316",
            "is_active": True,
        },
    ]
    
    async with async_session() as session:
        for sector_data in sectors_data:
            slug = sector_data["slug"]
            result = await session.execute(
                text("SELECT id FROM sectors WHERE slug = :slug"),
                {"slug": slug}
            )
            existing_sector = result.fetchone()
            
            if not existing_sector:
                sector = Sector(**sector_data)
                session.add(sector)
                await session.commit()
                print(f"✓ Initial sector created: {sector_data['name_en']}")
            else:
                print(f"✓ Sector already exists: {sector_data['name_en']}")


async def init_database():
    """
    Initialize the database with extensions and initial data.
    """
    print("Initializing database...")
    
    # Create PostgreSQL extensions
    print("Creating PostgreSQL extensions...")
    await create_extensions()
    
    # Create initial superuser
    print("Creating initial superuser...")
    await create_initial_superuser()
    
    # Create initial sectors
    print("Creating initial sectors...")
    await create_initial_sectors()
    
    print("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
