"""
domain/research_context.py

Internal domain models for aggregated research context.

The Research Aggregation Layer combines data from all Worker Agents into a single
normalized, deterministic ResearchContext object ready for consumption by downstream
scoring, reporting, or API response layers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List

from app.domain.clinical import ClinicalDomain
from app.domain.literature import LiteratureDomain
from app.domain.market import MarketInsightsDomain
from app.domain.patent import PatentLandscapeDomain


@dataclass
class ResearchMetadata:
    """
    Deterministic analytical metrics computed from all research domains.
    Calculated strictly without AI or LLM reasoning.
    """
    total_trials:               int             = 0
    active_trials_count:        int             = 0
    completed_trials_count:     int             = 0
    total_publications:         int             = 0
    highly_cited_papers_count:  int             = 0
    market_regions:             List[str]       = field(default_factory=list)
    global_market_size_usd_mn:  Optional[float] = None
    latest_market_cagr:         Optional[float] = None
    patent_count:               int             = 0
    active_patents_count:       int             = 0
    at_risk_patents_count:      int             = 0
    fto_summary:                str             = "No patent data available"
    domains_available:          List[str]       = field(default_factory=list)


@dataclass
class ResearchContext:
    """
    Unified container aggregating all domain intelligence and computed metadata
    for a target molecule.
    """
    molecule_name:    str
    clinical:         Optional[ClinicalDomain]        = None
    literature:       Optional[LiteratureDomain]      = None
    market:           Optional[MarketInsightsDomain]  = None
    patent:           Optional[PatentLandscapeDomain]  = None
    metadata:         ResearchMetadata                = field(default_factory=ResearchMetadata)
    created_at:       str                             = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pipeline_version: str                             = "1.0.0"
    warnings:         List[str]                       = field(default_factory=list)
    errors:           List[str]                       = field(default_factory=list)
