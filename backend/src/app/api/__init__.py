"""
api/__init__.py

Exposes research router.
"""

from app.api.research import router as research_router

__all__ = ["research_router"]
