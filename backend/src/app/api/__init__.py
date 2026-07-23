"""
api/__init__.py

Exposes research router.
"""

from app.api.research import router as research_router
from app.api.stream import router as stream_router

__all__ = ["research_router", "stream_router"]
