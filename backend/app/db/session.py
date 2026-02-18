# ============================================
# Boussole - Database Session Management
# ============================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from redis import asyncio as aioredis
from redis.asyncio import Redis
from typing import AsyncGenerator

from app.core.config import settings
from app.db.base import Base

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Global async session
async_session = async_session_maker

# Redis client
redis_client: Redis = None


async def init_redis() -> Redis:
    """
    Initialize the Redis client.
    
    Returns:
        Redis: An async Redis client
    """
    global redis_client
    redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10
    )
    return redis_client


async def close_redis():
    """
    Close the Redis connection.
    """
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Get a Redis client.
    
    Yields:
        Redis: An async Redis client
    """
    if redis_client is None:
        await init_redis()
    yield redis_client


async def init_db():
    """
    Initialize the database connection.
    """
    # Test the connection
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)


async def close_db():
    """
    Close the database connection.
    """
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.
    
    Yields:
        AsyncSession: An async database session
    """
    async with async_session_maker() as session:
        yield session
