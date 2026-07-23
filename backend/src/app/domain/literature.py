"""
domain/literature.py

Internal domain models for scientific literature intelligence data.

Decoupled from Europe PMC REST API raw payload structure.
The Literature Agent maps raw API payloads into these strongly typed domain models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class LiteratureRecord:
    """
    Represents a single scientific publication record.
    """
    pmid:           Optional[str]  # PubMed ID e.g., "34567890"
    doi:            Optional[str]  # Digital Object Identifier e.g., "10.1038/s41591-..."
    title:          str            # Paper title
    authors:        str            # Comma-separated author string
    journal:        str            # Journal name e.g., "Nature Medicine"
    pub_year:       Optional[int]  # Publication year e.g., 2022
    citation_count: int            # Number of times cited
    abstract:       Optional[str]  # Full or truncated paper abstract
    data_source:    str = "Europe PMC"


@dataclass
class LiteratureDomain:
    """
    Aggregated scientific literature intelligence for a molecule.
    Written into AgentState.literature by the Literature Agent.
    """
    molecule_name: str
    publications:  List[LiteratureRecord] = field(default_factory=list)
    total_found:   int = 0
    source:        str = "Europe PMC REST API"
    confidence:    Optional[float] = None  # Scientifically computed during Hybrid Scoring (Phase 5)

    @property
    def highly_cited_papers(self) -> List[LiteratureRecord]:
        """Publications with 10 or more citations."""
        return [p for p in self.publications if p.citation_count >= 10]

    @property
    def recent_papers(self) -> List[LiteratureRecord]:
        """Publications from 2020 or later."""
        return [p for p in self.publications if p.pub_year is not None and p.pub_year >= 2020]

    @property
    def top_journals(self) -> List[str]:
        """List of unique journals represented in the result set."""
        journals = [p.journal for p in self.publications if p.journal and p.journal != "Unknown Journal"]
        return list(dict.fromkeys(journals))  # Order-preserving deduplication

    @property
    def is_empty(self) -> bool:
        """True when no publication records were found."""
        return len(self.publications) == 0
