"""
services/synonym_service.py

Pharmaceutical Synonym & Brand Name Resolution Service.

Responsibilities:
  1. Query normalization (stripping, casing, whitespace cleaning).
  2. Brand-to-Generic name resolution (e.g., Ozempic -> Semaglutide, Keytruda -> Pembrolizumab).
  3. Dynamic PubChem PUG-REST API fallback lookup for unknown chemical compound synonyms.
  4. Returns a SynonymResult containing canonical_name, query_name, and a set of lowercased search synonyms.
"""

import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Set, Optional
import httpx

logger = logging.getLogger(__name__)

# Known brand-to-generic dictionary for high-frequency pharmaceutical compounds
KNOWN_BRAND_MAPPINGS = {
    # GLP-1 / GIP
    "ozempic": "Semaglutide",
    "wegovy": "Semaglutide",
    "rybelsus": "Semaglutide",
    "mounjaro": "Tirzepatide",
    "zepbound": "Tirzepatide",
    "trulicity": "Dulaglutide",
    "victoza": "Liraglutide",
    "saxenda": "Liraglutide",

    # Oncology
    "keytruda": "Pembrolizumab",
    "opdivo": "Nivolumab",
    "tagrisso": "Osimertinib",
    "rituxan": "Rituximab",
    "mabthera": "Rituximab",
    "humira": "Adalimumab",
    "herceptin": "Trastuzumab",
    "avastin": "Bevacizumab",

    # SGLT2 & Metabolic
    "jardiance": "Empagliflozin",
    "farxiga": "Dapagliflozin",
    "forxiga": "Dapagliflozin",
    "invokana": "Canagliflozin",
    "januvia": "Sitagliptin",

    # Cardiovascular / Statins
    "lipitor": "Atorvastatin",
    "crestor": "Rosuvastatin",
    "zocor": "Simvastatin",

    # Analgesics & Common NSAIDs
    "glucophage": "Metformin",
    "advil": "Ibuprofen",
    "motrin": "Ibuprofen",
    "nurofen": "Ibuprofen",
    "tylenol": "Paracetamol",
    "panadol": "Paracetamol",
    "acetaminophen": "Paracetamol",
    "bayer": "Aspirin",
    "aspirine": "Aspirin",
    "acetylsalicylic acid": "Aspirin",
    "aricept": "Donepezil",
}


@dataclass
class SynonymResult:
    query_name: str
    canonical_name: str
    synonyms: Set[str] = field(default_factory=set)

    def get_search_terms(self) -> List[str]:
        """Returns ordered list of distinct search terms (canonical first, then synonyms)."""
        terms = [self.canonical_name]
        for syn in self.synonyms:
            if syn.lower() != self.canonical_name.lower() and syn not in terms:
                terms.append(syn)
        return terms


class SynonymResolver:
    """
    Resolves molecule names and brand aliases into canonical drug names
    and a rich list of search synonyms.
    """

    def __init__(self, timeout_seconds: float = 3.0):
        self._timeout = timeout_seconds

    def resolve(self, query_name: str) -> SynonymResult:
        """
        Resolves query_name to canonical molecule name and synonyms.
        """
        if not query_name or not query_name.strip():
            return SynonymResult(query_name="", canonical_name="")

        cleaned = query_name.strip()
        lower_q = cleaned.lower()

        # 1. Check known brand mappings
        if lower_q in KNOWN_BRAND_MAPPINGS:
            canonical = KNOWN_BRAND_MAPPINGS[lower_q]
            synonyms = {cleaned.lower(), canonical.lower()}
            # Add all other brand names for this canonical molecule
            for brand, gen in KNOWN_BRAND_MAPPINGS.items():
                if gen.lower() == canonical.lower():
                    synonyms.add(brand)
            logger.info("SynonymResolver: Mapped brand '%s' -> Canonical '%s'", cleaned, canonical)
            return SynonymResult(query_name=cleaned, canonical_name=canonical, synonyms=synonyms)

        # 2. Check if query is generic name of known compound
        canonical = cleaned.capitalize()
        synonyms = {lower_q}
        for brand, gen in KNOWN_BRAND_MAPPINGS.items():
            if gen.lower() == lower_q:
                synonyms.add(brand)
                canonical = gen

        # 3. Dynamic PubChem PUG-REST API lookup if synonyms are scarce
        pubchem_synonyms = self._fetch_pubchem_synonyms(cleaned)
        synonyms.update(pubchem_synonyms)

        return SynonymResult(
            query_name=cleaned,
            canonical_name=canonical,
            synonyms=synonyms
        )

    def _fetch_pubchem_synonyms(self, compound_name: str) -> Set[str]:
        """
        Lightweight fetch of synonyms from PubChem PUG-REST API.
        Fails silently and returns empty set if unreachable or non-existent.
        """
        syns: Set[str] = set()
        encoded = urllib.parse.quote(compound_name.strip())
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/synonyms/JSON"

        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_syns = (
                        data.get("InformationList", {})
                        .get("Information", [{}])[0]
                        .get("Synonym", [])
                    )
                    # Take top 10 concise synonyms (under 30 chars)
                    for item in raw_syns:
                        if isinstance(item, str) and len(item) <= 30:
                            syns.add(item.lower())
                            if len(syns) >= 10:
                                break
                    logger.debug("PubChem found %d synonyms for '%s'", len(syns), compound_name)
        except Exception as exc:
            logger.debug("PubChem synonym lookup skipped for '%s': %s", compound_name, exc)

        return syns
