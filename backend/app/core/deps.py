# ============================================
# Boussole - Dependency Injection
# ============================================

from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from redis import asyncio as aioredis
from redis.asyncio import Redis

from app.db.session import async_session, redis_client
from app.core.security import get_current_user_id


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: An async database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency that provides a Redis client.
    
    Yields:
        Redis: An async Redis client
    """
    try:
        yield redis_client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service unavailable"
        ) from e


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency that provides the current authenticated user.
    
    Args:
        user_id: The user ID from the JWT token
        db: The database session
        
    Returns:
        The user object
        
    Raises:
        HTTPException: If the user is not found
    """
    from app.services.user_service import UserService
    from app.models.user import User
    
    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency that provides the current active user.
    
    Args:
        current_user: The current user from get_current_user
        
    Returns:
        The active user object
        
    Raises:
        HTTPException: If the user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_superuser(
    current_user = Depends(get_current_user)
):
    """
    Dependency that provides the current superuser.
    
    Args:
        current_user: The current user from get_current_user
        
    Returns:
        The superuser object
        
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have sufficient privileges"
        )
    return current_user
