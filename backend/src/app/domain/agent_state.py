"""
domain/agent_state.py

Shared state object passed through the MoleculeIQ multi-agent workflow.
Uses Annotated list reducers on errors/warnings so parallel LangGraph nodes
can append safely without concurrent key conflicts.
"""

import operator
from dataclasses import dataclass, field
from typing import Annotated, Optional, List

from app.domain.clinical import ClinicalDomain
from app.domain.literature import LiteratureDomain
from app.domain.market import MarketInsightsDomain
from app.domain.patent import PatentLandscapeDomain
from app.domain.repurposing import RepurposingDomain


@dataclass
class AgentState:
    """
    Shared state container passed between orchestrator nodes and worker agents.
    """
    molecule_name:   str
    synonyms:        List[str] = field(default_factory=list)
    clinical_trials: Optional[ClinicalDomain] = None
    literature:      Optional[LiteratureDomain] = None
    market:          Optional[MarketInsightsDomain] = None
    patent:          Optional[PatentLandscapeDomain] = None
    repurposing:     Optional[RepurposingDomain] = None
    errors:          Annotated[List[str], operator.add] = field(default_factory=list)
    warnings:        Annotated[List[str], operator.add] = field(default_factory=list)
