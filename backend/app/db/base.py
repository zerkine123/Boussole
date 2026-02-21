# ============================================
# Boussole - Database Base Configuration
# ============================================

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

# Database naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Create declarative base
Base = declarative_base(metadata=metadata)


def init_db():
    """
    Initialize the database with required extensions and initial data.
    This function is called during application startup.
    """
    from app.db.session import engine
    from app.models.user import User
    from app.models.sector import Sector
    from app.models.indicator import Indicator
    from app.models.intent import IntentLog, StaticIntent, SystemPrompt
    from app.models.ai_config import AIProviderConfig
    
    # Import all models to ensure they are registered with SQLAlchemy
    # This is important for Alembic to detect all models
    
    # Create initial data if needed
    # Example: Create default superuser
    # from app.core.security import get_password_hash
    # from sqlalchemy.ext.asyncio import AsyncSession
    # async with AsyncSession(engine) as session:
    #     # Check if superuser exists
    #     # Create if not exists
    #     pass
