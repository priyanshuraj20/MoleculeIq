"""
app/auth/schemas.py

Pydantic schemas for authentication requests, user profiles, and JWT tokens.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class GoogleAuthRequest(BaseModel):
    """Payload received from frontend containing Google OAuth ID token credential."""
    credential: str = Field(..., description="Google OAuth ID Token Credential string")


class UserResponse(BaseModel):
    """User profile data returned to client."""
    id: str
    google_id: str
    name: str
    email: str
    picture: Optional[str] = None
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None


class TokenResponse(BaseModel):
    """Authentication response payload containing custom JWT token and user profile."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
