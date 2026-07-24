"""
Application Configuration Module for MoleculeIQ.

Loads environment variables from .env using python-dotenv.
Centralizes system settings across backend services.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration class for application settings."""

    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "MoleculeIQ API")
    APP_ENV: str  = os.getenv("APP_ENV", "development")
    DEBUG: bool   = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str     = os.getenv("HOST", "0.0.0.0")
    PORT: int     = int(os.getenv("PORT", 8000))

    # CORS Origins — includes all common Vite & React dev server ports
    DEFAULT_CORS = (
        "http://localhost:5173,http://localhost:5174,http://localhost:5175,"
        "http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175"
    )
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS).split(",")
        if origin.strip()
    ]

    # Supabase credentials (mock market + patent datasets)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # External API — Base URLs
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

    # External API — Secrets
    COMTRADE_API_KEY: str = os.getenv("COMTRADE_API_KEY", "")

    # Gemini LLM configuration
    GEMINI_API_KEY: str   = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str     = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # HTTP Client — Timeouts
    API_CONNECT_TIMEOUT: float = float(os.getenv("API_CONNECT_TIMEOUT", "10"))
    API_READ_TIMEOUT: float    = float(os.getenv("API_READ_TIMEOUT", "30"))

    # HTTP Client — Retry
    API_MAX_RETRIES: int       = int(os.getenv("API_MAX_RETRIES", "3"))
    API_RETRY_WAIT_MIN: float  = float(os.getenv("API_RETRY_WAIT_MIN", "2"))

    # External API — Limits
    CLINICALTRIALS_PAGE_SIZE: int = int(os.getenv("CLINICALTRIALS_PAGE_SIZE", "10"))
    EUROPEPMC_PAGE_SIZE: int      = int(os.getenv("EUROPEPMC_PAGE_SIZE", "10"))
    COMTRADE_PERIOD: str          = os.getenv("COMTRADE_PERIOD", "2022")


settings = Settings()
