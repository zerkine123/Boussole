# ============================================
# Boussole - Onboarding Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class OnboardingPreferencesBase(BaseModel):
    """Base OnboardingPreferences schema with common fields."""
    preferred_language: str = Field(default="en", pattern="^(en|fr|ar)$")
    sectors_of_interest: List[int] = Field(default=[], description="List of sector IDs")
    wilayas_of_interest: List[int] = Field(default=[], description="List of Wilaya IDs")
    organization: Optional[str] = Field(None, max_length=255)
    use_case: Optional[str] = Field(None, max_length=50, description="Use case: personal, business, academic, government")
    sub_sectors: List[str] = Field(default=[], description="List of sub-sectors or specific interests")
    intent_text: Optional[str] = Field(None, description="Free-text describing the user's ultimate goal or intent")


class OnboardingPreferencesCreate(OnboardingPreferencesBase):
    """Schema for creating onboarding preferences."""
    skip_onboarding: bool = Field(default=False, description="Skip onboarding process")


class OnboardingPreferencesUpdate(BaseModel):
    """Schema for updating onboarding preferences."""
    preferred_language: Optional[str] = Field(None, pattern="^(en|fr|ar)$")
    sectors_of_interest: Optional[List[int]] = None
    wilayas_of_interest: Optional[List[int]] = None
    organization: Optional[str] = Field(None, max_length=255)
    use_case: Optional[str] = Field(None, max_length=50)
    sub_sectors: Optional[List[str]] = None
    intent_text: Optional[str] = None


class OnboardingPreferences(OnboardingPreferencesBase):
    """Schema for OnboardingPreferences response."""
    user_id: int
    email: str
    full_name: str
    organization: Optional[str] = None
    preferred_language: str
    onboarding_completed: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class OnboardingStep(BaseModel):
    """Schema for onboarding step."""
    step_number: int
    title: str
    description: str
    is_completed: bool = False


class OnboardingSurvey(BaseModel):
    """Schema for onboarding survey questions."""
    question_1_use_case: Optional[str] = Field(None, max_length=50)
    question_2_sectors: List[int] = Field(default=[], description="Selected sector IDs")
    question_3_wilayas: List[int] = Field(default=[], description="Selected Wilaya IDs")
    question_4_language: str = Field(default="en", pattern="^(en|fr|ar)$")


class OnboardingCompleteRequest(BaseModel):
    """Schema for completing onboarding."""
    preferences: OnboardingPreferencesCreate


class OnboardingCompleteResponse(BaseModel):
    """Schema for onboarding completion response."""
    status: str
    message: str
    user_id: int
    recommended_content: Optional[dict] = None


class AvailableWilaya(BaseModel):
    """Schema for available Wilaya."""
    id: int
    code: str
    name_en: str
    name_fr: str
    name_ar: str
    name_arabic: str
    region: Optional[str] = None


class AvailableSector(BaseModel):
    """Schema for available sector."""
    id: int
    slug: str
    name_en: str
    name_fr: str
    name_ar: str
    icon: Optional[str] = None
    color: Optional[str] = None


class OnboardingData(BaseModel):
    """Schema for onboarding data."""
    available_wilayas: List[AvailableWilaya]
    available_sectors: List[AvailableSector]
    current_preferences: Optional[OnboardingPreferences] = None
    recommended_content: Optional[dict] = None
