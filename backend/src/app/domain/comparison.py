"""
domain/comparison.py

Typed domain models for side-by-side molecule comparison mode.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from app.domain.research_context import ResearchContext


@dataclass
class DomainComparisonItem:
    """
    Comparison item for a specific research domain (Clinical, Literature, Patent, Market).
    """
    domain_name: str
    molecule_a_val: str
    molecule_b_val: str
    winner: str  # "molecule_a", "molecule_b", or "tie"
    summary: str


@dataclass
class ExecutiveComparisonSummary:
    """
    Synthesized strategic executive summary comparing two molecules.
    """
    key_differentiators: List[str] = field(default_factory=list)
    clinical_winner_reason: str = ""
    patent_winner_reason: str = ""
    market_winner_reason: str = ""
    strategic_recommendation: str = ""


@dataclass
class ComparisonReport:
    """
    Complete side-by-side comparison report entity between Molecule A and Molecule B.
    """
    molecule_a_name: str
    molecule_b_name: str
    molecule_a_context: ResearchContext
    molecule_b_context: ResearchContext
    clinical_comparison: DomainComparisonItem
    literature_comparison: DomainComparisonItem
    patent_comparison: DomainComparisonItem
    market_comparison: DomainComparisonItem
    overall_winner: str  # "molecule_a", "molecule_b", or "tie"
    score_difference: float
    executive_summary: ExecutiveComparisonSummary
    timestamp: str = ""
    processing_time_sec: float = 0.0
