import asyncio
import os
import sys

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin_user():
    async with async_session_maker() as session:
        # Check if the user already exists
        result = await session.execute(select(User).where(User.email == "admin@boussole.dz"))
        existing_user = result.scalars().first()
        
        if existing_user:
            print("Admin user already exists. Updating password and permissions.")
            existing_user.hashed_password = get_password_hash("admin123")
            existing_user.is_superuser = True
            existing_user.is_active = True
        else:
            print("Creating new admin user: admin@boussole.dz / admin123")
            new_user = User(
                email="admin@boussole.dz",
                full_name="Boussole Admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            session.add(new_user)
            
        await session.commit()
        print("Admin user setup complete. You can login with admin@boussole.dz / admin123")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
