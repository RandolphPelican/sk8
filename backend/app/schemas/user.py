from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.user import StanceEnum


# Base schema
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    stance: StanceEnum


# Schema for user registration
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str


# Schema for user response (what we send back)
class UserResponse(UserBase):
    id: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    wins: int
    losses: int
    current_streak: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
