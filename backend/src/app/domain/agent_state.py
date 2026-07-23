"""
domain/agent_state.py

Shared state object passed through the MoleculeIQ multi-agent workflow.

Minimal initial implementation: contains only fields required by
currently completed sessions (molecule_name, clinical_trials, errors, warnings).
Future fields will be added incrementally as new agents are implemented.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from app.domain.clinical import ClinicalDomain
from app.domain.literature import LiteratureDomain


@dataclass
class AgentState:
    """
    Shared state container passed between orchestrator nodes and worker agents.
    """
    molecule_name:   str
    clinical_trials: Optional[ClinicalDomain] = None
    literature:      Optional[LiteratureDomain] = None
    errors:          List[str] = field(default_factory=list)
    warnings:        List[str] = field(default_factory=list)
