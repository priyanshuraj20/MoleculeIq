"""
domain/repurposing.py

Internal domain models for drug repurposing discovery intelligence.
Aggregates candidate new indications identified via Open Targets Platform GraphQL API,
filtered against known/approved indications, ranked by association score,
and enriched with real supporting clinical trials and literature publications.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class EvidenceItem:
    """
    Real external evidence validating a repurposing indication candidate.
    """
    evidence_type: str   # "clinical_trial" | "literature"
    id:            str   # NCT ID (e.g., "NCT01234567") or PMID (e.g., "34567890")
    title:         str   # Study or publication title
    url:           str   # Direct verified link to ClinicalTrials.gov or Europe PMC / PubMed

    @property
    def type(self) -> str:
        return "trial" if self.evidence_type == "clinical_trial" else "publication"


@dataclass
class RepurposingCandidate:
    """
    One candidate indication for drug repurposing with evidence metrics.
    """
    disease_name:             str
    disease_id:               str                  # EFO or MONDO ontology ID (e.g., "MONDO_0005233")
    association_score:        float                # Overall target-disease association score (0.0 to 1.0)
    target_symbols:           List[str]            # Associated gene symbols (e.g., ["PDCD1"], ["AMPK"])
    target_names:             List[str]            # Full protein/target names
    mechanisms_of_action:     List[str]            # Known drug MOAs on target(s)
    evidence:                 List[EvidenceItem]   = field(default_factory=list)
    evidence_counts:          Dict[str, int]       = field(default_factory=lambda: {"trials_count": 0, "publications_count": 0})
    explanation:              str                  = ""
    explanation_ai_generated: bool                 = True
    provenance:               str                  = "real"

    @property
    def targets(self) -> List[str]:
        return self.target_symbols

    @property
    def why_it_could_work(self) -> str:
        return self.explanation

    @property
    def evidence_trials_count(self) -> int:
        return self.evidence_counts.get("trials_count", 0)

    @property
    def evidence_papers_count(self) -> int:
        return self.evidence_counts.get("publications_count", 0)


@dataclass
class RepurposingDomain:
    """
    Aggregated drug repurposing intelligence container.
    Attached to AgentState.repurposing and ResearchContext.repurposing.
    """
    molecule_name:    str
    chembl_id:        Optional[str]                 = None
    candidates:       List[RepurposingCandidate]    = field(default_factory=list)
    total_candidates: int                           = 0
    source:           str                           = "Open Targets Platform"
    provenance:       str                           = "real"

    @property
    def is_empty(self) -> bool:
        """True when no candidate repurposing indications were found."""
        return len(self.candidates) == 0
