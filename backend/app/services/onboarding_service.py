# ============================================
# Boussole - Onboarding Service
# ============================================

"""
Onboarding service for managing user preferences and first-time setup.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import logging

from app.models.user import User
from app.models.wilaya import Wilaya
from app.models.sector import Sector
from app.schemas.onboarding import (
    OnboardingPreferencesCreate,
    OnboardingPreferencesUpdate,
    OnboardingPreferences,
)

logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Service layer for onboarding operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_preferences(self, user_id: int) -> Optional[dict]:
        """
        Get user onboarding preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences as dictionary
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Parse preferences from user's metadata or dedicated fields
        # For now, return basic user info
        # In production, add dedicated onboarding preferences fields to User model
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "organization": user.organization,
            "preferred_language": user.preferred_language,
            "onboarding_completed": True,  # Placeholder - add dedicated field to model
        }
    
    async def update_user_preferences(
        self,
        user_id: int,
        preferences: OnboardingPreferencesUpdate
    ) -> Optional[dict]:
        """
        Update user onboarding preferences.
        
        Args:
            user_id: User ID
            preferences: Updated preferences
            
        Returns:
            Updated user preferences
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Update user preferences
        update_data = preferences.model_dump(exclude_unset=True)
        
        # Handle sectors of interest
        if "sectors_of_interest" in update_data:
            # In production, store this in a dedicated UserPreferences model
            # For now, we'll store it in the user's metadata or notes
            pass
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        # Refresh user
        await self.db.refresh(user)
        
        logger.info(f"Updated preferences for user {user_id}")
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "preferred_language": user.preferred_language,
        }
    
    async def get_available_wilayas(self) -> List[dict]:
        """
        Get all available Wilayas for user selection.
        
        Returns:
            List of Wilayas
        """
        result = await self.db.execute(
            select(Wilaya).where(Wilaya.is_active == True)
        )
        wilayas = result.scalars().all()
        
        return [
            {
                "id": w.id,
                "code": w.code,
                "name_en": w.name_en,
                "name_fr": w.name_fr,
                "name_ar": w.name_ar,
                "name_arabic": w.name_arabic,
                "region": w.region,
            }
            for w in wilayas
        ]
    
    async def get_available_sectors(self) -> List[dict]:
        """
        Get all available sectors for user selection.
        
        Returns:
            List of sectors
        """
        result = await self.db.execute(
            select(Sector).where(Sector.is_active == True)
        )
        sectors = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "slug": s.slug,
                "name_en": s.name_en,
                "name_fr": s.name_fr,
                "name_ar": s.name_ar,
                "icon": s.icon,
                "color": s.color,
            }
            for s in sectors
        ]
    
    async def complete_onboarding(
        self,
        user_id: int,
        preferences: OnboardingPreferencesCreate
    ) -> dict:
        """
        Complete user onboarding process.
        
        Args:
            user_id: User ID
            preferences: Onboarding preferences
            
        Returns:
            Onboarding completion status
        """
        # Update user with onboarding preferences
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Update user preferences
        update_data = {
            "preferred_language": preferences.preferred_language,
            "organization": preferences.organization,
        }
        
        # In production, add onboarding_completed flag and store sectors_of_interest
        # For now, we'll just update basic fields
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        logger.info(f"Onboarding completed for user {user_id}")
        
        return {
            "status": "success",
            "message": "Onboarding completed successfully",
            "user_id": user_id,
        }
    
    async def skip_onboarding(self, user_id: int) -> dict:
        """
        Skip onboarding for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Skip status
        """
        # In production, mark onboarding as skipped in user preferences
        # For now, just return success
        logger.info(f"User {user_id} skipped onboarding")
        
        return {
            "status": "success",
            "message": "Onboarding skipped",
            "user_id": user_id,
        }
    
    async def get_recommended_content(
        self,
        user_id: int,
        language: str = "en"
    ) -> dict:
        """
        Get recommended content based on user preferences.
        
        Args:
            user_id: User ID
            language: Content language
            
        Returns:
            Recommended sectors and metrics
        """
        # Get user preferences
        preferences = await self.get_user_preferences(user_id)
        
        if not preferences:
            # Return default recommendations
            return {
                "recommended_sectors": [],
                "recommended_metrics": [],
                "language": language,
            }
        
        # In production, use user's sectors_of_interest to recommend content
        # For now, return top sectors by metrics count
        # This is a placeholder - implement actual recommendation logic
        
        result = await self.db.execute(
            select(Sector)
            .where(Sector.is_active == True)
            .limit(5)
        )
        sectors = result.scalars().all()
        
        return {
            "recommended_sectors": [
                {
                    "id": s.id,
                    "slug": s.slug,
                    "name_en": s.name_en,
                    "name_fr": s.name_fr,
                    "name_ar": s.name_ar,
                    "icon": s.icon,
                    "color": s.color,
                }
                for s in sectors
            ],
            "recommended_metrics": [],  # Placeholder - implement actual metric recommendation
            "language": language,
        }
