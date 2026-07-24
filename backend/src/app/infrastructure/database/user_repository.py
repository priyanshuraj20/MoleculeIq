"""
infrastructure/database/user_repository.py

Repository for managing user accounts in Supabase PostgreSQL ('users' table).

Responsibilities:
  1. Lookup user by google_id or email.
  2. Insert new user record on first-time login.
  3. Update last_login_at timestamp on every login event.
  4. Handle DB exceptions gracefully.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.infrastructure.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository wrapping Supabase PostgreSQL queries for the 'users' table."""

    def __init__(self):
        self._db = get_supabase()

    def get_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Find a user by their Google OAuth unique ID."""
        try:
            res = (
                self._db.table("users")
                .select("*")
                .eq("google_id", google_id)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as err:
            logger.error("Failed to fetch user by google_id=%s: %s", google_id, err, exc_info=True)
            raise

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by their email address."""
        try:
            res = (
                self._db.table("users")
                .select("*")
                .eq("email", email)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as err:
            logger.error("Failed to fetch user by email=%s: %s", email, err, exc_info=True)
            raise

    def create_user(
        self,
        google_id: str,
        name: str,
        email: str,
        picture: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new user record in Supabase PostgreSQL.
        Initializes last_login_at, created_at, updated_at timestamps.
        """
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "google_id": google_id,
                "name": name,
                "email": email,
                "picture": picture,
                "created_at": now_iso,
                "updated_at": now_iso,
                "last_login_at": now_iso,
            }
            res = self._db.table("users").insert(payload).execute()
            if res.data and len(res.data) > 0:
                logger.info("Created new user: id=%s email=%s", res.data[0].get("id"), email)
                return res.data[0]
            raise RuntimeError("Supabase insert returned empty data")
        except Exception as err:
            logger.error("Failed to create user email=%s: %s", email, err, exc_info=True)
            raise

    def update_last_login(self, google_id: str) -> Dict[str, Any]:
        """
        Update last_login_at and updated_at timestamps for a user upon login.
        """
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "last_login_at": now_iso,
                "updated_at": now_iso,
            }
            res = (
                self._db.table("users")
                .update(payload)
                .eq("google_id", google_id)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
            # Fallback query if update doesn't return data
            return self.get_by_google_id(google_id)
        except Exception as err:
            logger.error("Failed to update last_login_at for google_id=%s: %s", google_id, err, exc_info=True)
            raise
