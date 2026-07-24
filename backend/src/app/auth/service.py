"""
app/auth/service.py

Service layer for Google OAuth verification and user authentication business logic.
"""

import logging
from typing import Dict, Any, Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status
from app.core.config import settings
from app.infrastructure.database.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Handles Google token verification and Supabase PostgreSQL user persistence."""

    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def verify_google_credential(self, credential: str) -> Dict[str, Any]:
        """
        Verify the raw Google OAuth ID Token credential using google-auth library.
        Validates token signature, expiration, and audience (GOOGLE_CLIENT_ID).
        Extracts google_id (sub), email, name, and picture.
        """
        try:
            # Construct Google request transport
            transport = google_requests.Request()
            
            # Verify ID token against Google's public keys
            # If GOOGLE_CLIENT_ID is set, enforce audience check
            audience = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
            
            payload = id_token.verify_oauth2_token(
                credential,
                transport,
                audience=audience
            )

            google_id = payload.get("sub")
            email     = payload.get("email")
            name      = payload.get("name") or email.split("@")[0]
            picture   = payload.get("picture")

            if not google_id or not email:
                raise ValueError("Google ID token missing sub or email claims")

            return {
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture": picture,
            }

        except ValueError as err:
            logger.warning("Google ID token verification failed: %s", err)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google authentication failed: {str(err)}"
            )
        except Exception as err:
            logger.error("Unexpected error verifying Google credential: %s", err, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify Google ID token with identity provider."
            )

    def authenticate_google_user(self, credential: str) -> Dict[str, Any]:
        """
        1. Verify Google credential.
        2. Query Supabase PostgreSQL for existing user by google_id or email.
        3. If existing: update last_login_at.
        4. If new: insert into users table.
        5. Return unified user dict.
        """
        google_data = self.verify_google_credential(credential)
        google_id   = google_data["google_id"]
        email       = google_data["email"]
        name        = google_data["name"]
        picture     = google_data["picture"]

        # Check existing user in Supabase PostgreSQL
        user = self.user_repo.get_by_google_id(google_id)
        if not user:
            # Check by email if google_id didn't match (prevents duplicate email conflicts)
            user = self.user_repo.get_by_email(email)

        if user:
            # Existing user — update last_login_at
            updated_user = self.user_repo.update_last_login(user["google_id"])
            return updated_user or user
        else:
            # First time user — insert new record into Supabase PostgreSQL
            new_user = self.user_repo.create_user(
                google_id=google_id,
                name=name,
                email=email,
                picture=picture,
            )
            return new_user
