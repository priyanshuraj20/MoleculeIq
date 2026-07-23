"""
infrastructure/database/supabase_client.py

Creates and exports a single shared Supabase client instance.

Why a single instance?
  Creating a new client for every query is wasteful. One shared client
  reuses the same HTTP connection pool across all database calls.

Usage in repositories:
  from app.infrastructure.database.supabase_client import get_supabase
  client = get_supabase()
  data = client.table("iqvia_sales").select("*").execute()
"""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase() -> Client:
    """
    Returns an initialized Supabase client using credentials from .env.

    Raises a clear error if credentials are missing so the problem is
    obvious at startup rather than failing silently on the first query.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in your .env file. "
            "Copy .env.example to .env and fill in your Supabase project credentials."
        )

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
