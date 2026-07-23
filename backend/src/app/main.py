"""
MoleculeIQ — FastAPI Application Gateway Entry Point.

This is the main entry point of the backend application.
It initializes the FastAPI application, configures CORS middleware for frontend communication,
and registers global routes like the health check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Initialize FastAPI app instance with metadata for Swagger UI
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI SaaS API Gateway for Pharmaceutical Innovation Intelligence.",
    version="1.0.0",
    docs_url="/docs",      # Interactive Swagger UI documentation path
    redoc_url="/redoc",    # Alternative ReDoc documentation path
)

# Configure Cross-Origin Resource Sharing (CORS)
# This allows our React frontend (running on e.g. localhost:5173) to safely make API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System Health"])
async def health_check():
    """
    Health Check Endpoint.
    
    Returns standard JSON status indicating that the backend server is online and operational.
    Used by load balancers, monitoring tools, and frontend connection checks.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # Allow running main.py directly for local debugging
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
