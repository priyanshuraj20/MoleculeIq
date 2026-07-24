"""
infrastructure/database/user_repository.py

Repository for managing user accounts in Supabase PostgreSQL ('users' table).

Responsibilities:
  1. Lookup user by google_id or email.
  2. Insert new user record on first-time login.
  3. Update last_login_at timestamp on every login event.
  4. Handle DB exceptions gracefully with clear error messages.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.infrastructure.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def _handle_db_error(err: Exception, context: str):
    """Formats database errors into actionable developer-friendly messages."""
    err_str = str(err)
    if "PGRST205" in err_str or "public.users" in err_str or "schema cache" in err_str:
        msg = (
            "Supabase database table 'public.users' does not exist yet. "
            "Please copy and run the SQL script in backend/scripts/create_users_table.sql "
            "in your Supabase SQL Editor (https://supabase.com/dashboard/project/tlxyazbunhlnzjmwyqjw/sql)."
        )
        logger.critical(msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg
        )
    logger.error("Database query failed during %s: %s", context, err_str, exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error during {context}: {err_str}"
    )


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
        except HTTPException:
            raise
        except Exception as err:
            _handle_db_error(err, f"get_by_google_id({google_id})")

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
        except HTTPException:
            raise
        except Exception as err:
            _handle_db_error(err, f"get_by_email({email})")

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
        except HTTPException:
            raise
        except Exception as err:
            _handle_db_error(err, f"create_user({email})")

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
            return self.get_by_google_id(google_id)
        except HTTPException:
            raise
        except Exception as err:
            _handle_db_error(err, f"update_last_login({google_id})")
