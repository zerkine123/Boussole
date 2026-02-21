# ============================================
# Boussole - User Schemas
# ============================================

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    preferred_language: str = Field(default="en", pattern="^(en|fr|ar)$")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=50)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field(None, pattern="^(en|fr|ar)$")


class UserUpdatePassword(BaseModel):
    """Schema for updating user password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserInDB(UserBase):
    """Schema representing user in database."""
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """Schema for user response (without password)."""
    id: int
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserAdminResponse(User):
    """Schema for user response in Admin Panel, including relationships."""
    # We use 'Any' here temporarily to avoid circular imports, 
    # but the router will serialize it correctly due to from_attributes=True
    subscriptions: Optional[List[dict]] = []
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None
