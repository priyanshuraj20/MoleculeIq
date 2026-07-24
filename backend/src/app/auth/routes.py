"""
app/auth/routes.py

FastAPI router for Google OAuth authentication, JWT issuance, HttpOnly cookie management, and user session validation.
"""

import logging
from fastapi import APIRouter, Response, Depends, status
from app.auth.schemas import GoogleAuthRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
auth_service = AuthService()


@auth_router.post(
    "/google",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate with Google OAuth ID Token",
    description="Verifies Google ID token credential, creates or updates Supabase PostgreSQL user, issues custom JWT, and sets HttpOnly cookie."
)
async def login_with_google(payload: GoogleAuthRequest, response: Response):
    """
    Authenticate user using Google OAuth ID token.
    Sets HttpOnly cookie and returns access_token with user profile object.
    """
    # 1. Verify Google token & sync user with Supabase PostgreSQL
    user = auth_service.authenticate_google_user(payload.credential)

    # 2. Create custom FastAPI JWT access token
    token_data = {
        "sub": user["google_id"],
        "user_id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture"),
    }
    access_token = create_access_token(data=token_data)

    # 3. Set HttpOnly cookie for XSS protection
    # max_age = 7 days (604,800 seconds)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production HTTPS
        max_age=604800,
        path="/",
    )

    # 4. Construct response user model
    user_model = UserResponse(
        id=str(user["id"]),
        google_id=user["google_id"],
        name=user["name"],
        email=user["email"],
        picture=user.get("picture"),
        created_at=str(user.get("created_at")) if user.get("created_at") else None,
        last_login_at=str(user.get("last_login_at")) if user.get("last_login_at") else None,
    )

    logger.info("Successfully authenticated user email=%s via Google OAuth", user["email"])
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_model,
    )


@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current Logged-in User Profile",
    description="Validates app JWT (via HttpOnly cookie or Bearer header) and returns active user profile."
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the profile data of the currently authenticated user."""
    return UserResponse(
        id=current_user.get("user_id", ""),
        google_id=current_user.get("sub", ""),
        name=current_user.get("name", ""),
        email=current_user.get("email", ""),
        picture=current_user.get("picture"),
    )


@auth_router.post(
    "/logout",
    summary="Logout User",
    description="Clears the HttpOnly access_token cookie."
)
async def logout(response: Response):
    """Log out user by deleting the HttpOnly access_token cookie."""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}
