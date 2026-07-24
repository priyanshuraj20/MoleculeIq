"""
domain/patent.py

Internal domain models for patent landscape data.

Decoupled from Supabase. The patent repository maps raw DB rows into
these types. The Patent Agent reads from PatentLandscapeDomain only.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class PatentRecord:
    """
    One row from the patents table.
    Represents a single patent filing for a molecule.
    """
    molecule_name:  str
    patent_number:  Optional[str]   # e.g. "US8846100"
    jurisdiction:   str             # US, EU, IN, JP, CN, DE, GB, ...
    filing_date:    Optional[date]
    expiry_date:    Optional[date]
    status:         str             # Active | Expired | Pending
    patent_type:    Optional[str]   # Composition of Matter | Formulation | Method of Use
    assignee:       Optional[str]   # Company holding the patent
    fto_status:     str             # Free to Operate | At Risk | Blocked
    data_source:    str


@dataclass
class PatentLandscapeDomain:
    """
    Aggregated patent landscape for one molecule.
    This is what the Patent Agent writes into AgentState.

    Convenience properties surface the FTO summary and active patent
    count so agents don't re-compute from the raw list.
    """
    molecule_name: str
    patents:       list[PatentRecord] = field(default_factory=list)
    source:        str   = "Supabase / USPTO-EPO (mock)"
    confidence:    Optional[float] = None  # Scientifically computed during Hybrid Scoring (Phase 5)

    @property
    def active_patents(self) -> list[PatentRecord]:
        """Patents currently in force."""
        return [p for p in self.patents if p.status == "Active"]

    @property
    def expired_patents(self) -> list[PatentRecord]:
        """Patents no longer in force."""
        return [p for p in self.patents if p.status == "Expired"]

    @property
    def at_risk_patents(self) -> list[PatentRecord]:
        """Active patents that pose an FTO concern."""
        return [p for p in self.patents if p.fto_status == "At Risk"]

    @property
    def fto_summary(self) -> str:
        """
        High-level FTO assessment string for use in the report.
        Example: "At Risk — 3 active constraint(s)"
        """
        if self.is_empty:
            return "No patent data available"
        at_risk = self.at_risk_patents
        if not at_risk:
            return "Free to Operate — no active blocking patents found"
        return f"At Risk — {len(at_risk)} active patent constraint(s)"

    @property
    def is_empty(self) -> bool:
        """True when no patent records were found for this molecule."""
        return len(self.patents) == 0
