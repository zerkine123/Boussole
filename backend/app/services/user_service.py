# ============================================
# Boussole - User Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    """
    Service layer for user operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all users with pagination.
        """
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
        
    async def delete(self, user_id: int) -> Optional[User]:
        """
        Delete a user.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
            
        await self.db.delete(user)
        await self.db.commit()
        return user
