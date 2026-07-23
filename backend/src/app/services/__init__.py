"""
services/__init__.py

Exposes AggregationService, ScoringService, and functional entrypoints.
"""

from app.services.aggregation_service import AggregationService, build_research_context
from app.services.scoring_service import ScoringService, calculate_opportunity_score

__all__ = [
    "AggregationService",
    "build_research_context",
    "ScoringService",
    "calculate_opportunity_score",
]
