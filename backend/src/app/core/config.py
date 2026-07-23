"""
Application Configuration Module for MoleculeIQ.

This file loads environment variables from .env using python-dotenv.
It centralizes system settings so other parts of the application don't need
to read process environment variables directly.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Settings:
    """Central configuration class for application settings."""

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = os.getenv("APP_NAME", "MoleculeIQ API")
    APP_ENV: str  = os.getenv("APP_ENV", "development")
    DEBUG: bool   = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str     = os.getenv("HOST", "0.0.0.0")
    PORT: int     = int(os.getenv("PORT", 8000))

    # CORS — allow React dev server to talk to FastAPI
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # ------------------------------------------------------------------ #
    # Supabase — PostgreSQL database (mock market + patent datasets)
    # ------------------------------------------------------------------ #
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ------------------------------------------------------------------ #
    # External API — Base URLs
    # Centralised here so no client ever hardcodes a URL.
    # ------------------------------------------------------------------ #
    CLINICALTRIALS_BASE_URL: str = os.getenv(
        "CLINICALTRIALS_BASE_URL",
        "https://clinicaltrials.gov/api/v2"
    )
    EUROPEPMC_BASE_URL: str = os.getenv(
        "EUROPEPMC_BASE_URL",
        "https://www.ebi.ac.uk/europepmc/webservices/rest"
    )
    COMTRADE_BASE_URL: str = os.getenv(
        "COMTRADE_BASE_URL",
        "https://comtradeapi.un.org/data/v1"
    )

    # ------------------------------------------------------------------ #
    # External API — Secrets
    # ------------------------------------------------------------------ #
    # UN Comtrade requires a subscription key.
    # ClinicalTrials.gov and Europe PMC are open — no key needed.
    COMTRADE_API_KEY: str = os.getenv("COMTRADE_API_KEY", "")

    # ------------------------------------------------------------------ #
    # HTTP Client — Timeouts (seconds)
    # connect: time to establish a TCP connection
    # read:    time to receive the full response body
    # ------------------------------------------------------------------ #
    API_CONNECT_TIMEOUT: float = float(os.getenv("API_CONNECT_TIMEOUT", "10"))
    API_READ_TIMEOUT: float    = float(os.getenv("API_READ_TIMEOUT", "30"))

    # ------------------------------------------------------------------ #
    # HTTP Client — Retry (exponential backoff)
    # Max 3 attempts. Wait doubles each time: 2s → 4s → 8s.
    # ------------------------------------------------------------------ #
    API_MAX_RETRIES: int       = int(os.getenv("API_MAX_RETRIES", "3"))
    API_RETRY_WAIT_MIN: float  = float(os.getenv("API_RETRY_WAIT_MIN", "2"))

    # ------------------------------------------------------------------ #
    # External API — Result limits per request
    # Keeps latency predictable. Agents ask for exactly what they need.
    # ------------------------------------------------------------------ #
    CLINICALTRIALS_PAGE_SIZE: int = int(os.getenv("CLINICALTRIALS_PAGE_SIZE", "10"))
    EUROPEPMC_PAGE_SIZE: int      = int(os.getenv("EUROPEPMC_PAGE_SIZE", "10"))
    COMTRADE_PERIOD: str          = os.getenv("COMTRADE_PERIOD", "2022")


# Singleton — import this object everywhere, never instantiate Settings again
settings = Settings()
