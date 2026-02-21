# ============================================
# Boussole - Admin API Routes
# ============================================

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_superuser, get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, UserAdminResponse
from sqlalchemy.orm import selectinload
from sqlalchemy import select

router = APIRouter()

@router.get("/users", response_model=List[UserAdminResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Retrieve all users. Admin only.
    """
    query = select(User).options(selectinload(User.subscriptions)).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Format the users to include subscriptons as dictionaries to satisfy Pydantic
    formatted_users = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "organization": user.organization,
            "bio": user.bio,
            "preferred_language": user.preferred_language,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "subscriptions": []
        }
        for sub in user.subscriptions:
            user_dict["subscriptions"].append({
                "tier": sub.tier,
                "status": sub.status,
                "current_period_end": sub.current_period_end
            })
        formatted_users.append(user_dict)
        
    return formatted_users

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update a user. Admin only.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await user_service.update(user_id=user_id, user_data=user_in)
    return user

@router.delete("/users/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a user. Admin only.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent superuser from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete current active superuser")
        
    user = await user_service.delete(user_id=user_id)
    return user
