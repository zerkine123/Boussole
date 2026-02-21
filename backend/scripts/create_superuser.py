import asyncio
import sys
import os

# Add the parent directory to sys.path to allow importing from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import async_session
from app.models.user import User
from app.core.security import get_password_hash

async def create_superuser(email: str, password: str, full_name: str):
    """
    Create a new superuser or update an existing user to be a superuser.
    """
    async with async_session() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User with email {email} already exists. Updating to superuser...")
            user.is_superuser = True
            user.is_active = True
            user.hashed_password = get_password_hash(password)
            user.full_name = full_name
        else:
            print(f"Creating new superuser with email {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                is_superuser=True,
                is_active=True
            )
            db.add(user)
        
        await db.commit()
        print(f"Successfully created/updated superuser: {email}")

if __name__ == "__main__":
    # You can change these default values or pass them as arguments
    admin_email = os.getenv("ADMIN_EMAIL", "admin@boussole.dz")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_name = os.getenv("ADMIN_NAME", "Boussole Admin")
    
    if len(sys.argv) > 1:
        admin_email = sys.argv[1]
    if len(sys.argv) > 2:
        admin_password = sys.argv[2]
    if len(sys.argv) > 3:
        admin_name = sys.argv[3]
        
    asyncio.run(create_superuser(admin_email, admin_password, admin_name))
