"""
services/__init__.py

Exposes AggregationService and build_research_context entrypoints.
"""

from app.services.aggregation_service import AggregationService, build_research_context

__all__ = ["AggregationService", "build_research_context"]
