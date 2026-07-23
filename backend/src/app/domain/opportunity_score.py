"""
domain/opportunity_score.py

Internal domain models for commercial opportunity scoring.

Represents deterministic, explainable, and reproducible opportunity metrics.
Calculated strictly via transparent heuristics without AI or LLM reasoning.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScoreBreakdown:
    """
    Detailed explanation of sub-scores and factors contributing to the OpportunityScore.
    Ensures 100% transparency and auditability for pharmaceutical executives.
    """
    clinical_factors:   Dict[str, float] = field(default_factory=dict)
    market_factors:     Dict[str, float] = field(default_factory=dict)
    patent_factors:     Dict[str, float] = field(default_factory=dict)
    literature_factors: Dict[str, float] = field(default_factory=dict)
    confidence_factors: Dict[str, float] = field(default_factory=dict)
    explanation:        List[str]        = field(default_factory=list)


@dataclass
class OpportunityScore:
    """
    Aggregated commercial opportunity score container.
    Attached directly to ResearchContext.score.
    """
    overall_score:    float          # Overall score from 0.0 to 100.0
    clinical_score:   float          # Clinical trial momentum & validation (0.0 to 100.0)
    market_score:     float          # Market size & growth potential (0.0 to 100.0)
    patent_score:     float          # Freedom-To-Operate & patent landscape (0.0 to 100.0)
    research_score:   float          # Scientific literature impact & volume (0.0 to 100.0)
    confidence_score: float          # Data completeness & source availability signal (0.0 to 100.0)
    score_breakdown:  ScoreBreakdown = field(default_factory=ScoreBreakdown)
