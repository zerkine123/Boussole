# ============================================
# Boussole - Onboarding Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.onboarding import (
    OnboardingPreferences,
    OnboardingPreferencesCreate,
    OnboardingPreferencesUpdate,
    OnboardingCompleteRequest,
    OnboardingCompleteResponse,
    AvailableWilaya,
    AvailableSector,
    OnboardingData,
)
from app.services.onboarding_service import OnboardingService
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/preferences", response_model=OnboardingPreferences)
async def get_onboarding_preferences(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's onboarding preferences.
    """
    service = OnboardingService(db)
    preferences = await service.get_user_preferences(current_user.id)
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    
    return preferences


@router.post("/preferences", response_model=OnboardingPreferences)
async def update_onboarding_preferences(
    preferences: OnboardingPreferencesUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's onboarding preferences.
    """
    service = OnboardingService(db)
    updated = await service.update_user_preferences(current_user.id, preferences)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated


@router.get("/data", response_model=OnboardingData)
async def get_onboarding_data(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all onboarding data (Wilayas, sectors).
    """
    service = OnboardingService(db)
    
    wilayas = await service.get_available_wilayas()
    sectors = await service.get_available_sectors()
    
    # Get current preferences if available
    preferences = await service.get_user_preferences(current_user.id)
    
    return OnboardingData(
        available_wilayas=[
            AvailableWilaya(
                id=w["id"],
                code=w["code"],
                name_en=w["name_en"],
                name_fr=w["name_fr"],
                name_ar=w["name_ar"],
                name_arabic=w["name_arabic"],
                region=w["region"],
            )
            for w in wilayas
        ],
        available_sectors=[
            AvailableSector(
                id=s["id"],
                slug=s["slug"],
                name_en=s["name_en"],
                name_fr=s["name_fr"],
                name_ar=s["name_ar"],
                icon=s["icon"],
                color=s["color"],
            )
            for s in sectors
        ],
        current_preferences=preferences,
    )


@router.post("/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete user onboarding.
    """
    service = OnboardingService(db)
    
    if request.preferences.skip_onboarding:
        result = await service.skip_onboarding(current_user.id)
    else:
        result = await service.complete_onboarding(current_user.id, request.preferences)
    
    return result


@router.get("/recommended", response_model=dict)
async def get_recommended_content(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    language: str = "en"
):
    """
    Get recommended content based on user preferences.
    """
    service = OnboardingService(db)
    recommended = await service.get_recommended_content(current_user.id, language)
    
    return recommended
