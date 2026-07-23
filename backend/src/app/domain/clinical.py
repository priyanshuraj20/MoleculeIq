"""
domain/clinical.py

Internal domain models for clinical trials data.

Decoupled from ClinicalTrials.gov API raw structure.
The Clinical Trials Agent maps raw JSON payloads into these strongly typed domain models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class ClinicalTrialRecord:
    """
    Represents a single clinical trial study.
    """
    nct_id:           str            # e.g., "NCT01083212"
    title:            str            # Brief title of the study
    status:           str            # COMPLETED, RECRUITING, TERMINATED, etc.
    phases:           List[str]      # e.g., ["PHASE3"], ["PHASE1", "PHASE2"]
    conditions:       List[str]      # e.g., ["Type 2 Diabetes Mellitus"]
    lead_sponsor:     Optional[str]  # e.g., "AstraZeneca"
    start_date:       Optional[str]  # e.g., "2010-03"
    completion_date:  Optional[str]  # e.g., "2010-06"
    enrollment_count: Optional[int]  # e.g., 19
    data_source:      str = "ClinicalTrials.gov"


@dataclass
class ClinicalDomain:
    """
    Aggregated clinical trial intelligence for a molecule.
    Written into AgentState.clinical_trials by the Clinical Trials Agent.
    """
    molecule_name: str
    trials:        List[ClinicalTrialRecord] = field(default_factory=list)
    total_found:   int = 0
    source:        str = "ClinicalTrials.gov API v2"
    confidence:    float = 0.90  # API data is highly authoritative

    @property
    def active_trials(self) -> List[ClinicalTrialRecord]:
        """Trials currently active or recruiting."""
        active_statuses = {"RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION", "NOT_YET_RECRUITING"}
        return [t for t in self.trials if t.status in active_statuses]

    @property
    def completed_trials(self) -> List[ClinicalTrialRecord]:
        """Trials that have completed."""
        return [t for t in self.trials if t.status == "COMPLETED"]

    @property
    def phase_distribution(self) -> Dict[str, int]:
        """Distribution of trials across phases (e.g. {'PHASE3': 4, 'PHASE2': 2})."""
        dist: Dict[str, int] = {}
        for trial in self.trials:
            if not trial.phases:
                dist["NA"] = dist.get("NA", 0) + 1
            for phase in trial.phases:
                dist[phase] = dist.get(phase, 0) + 1
        return dist

    @property
    def is_empty(self) -> bool:
        """True when no clinical trial records were found."""
        return len(self.trials) == 0
