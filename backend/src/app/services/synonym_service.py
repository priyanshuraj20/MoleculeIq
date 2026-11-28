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
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Set, Optional
import httpx
from app.core.config import settings

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
    "dolo": "Paracetamol",
    "dolo650": "Paracetamol",
    "crocin": "Paracetamol",
    "calpol": "Paracetamol",
    "acetaminophen": "Paracetamol",
    "brufen": "Ibuprofen",
    "combiflam": "Ibuprofen",
    "glycomet": "Metformin",
    "ecosprin": "Aspirin",
    "augmentin": "Amoxicillin",
    "pan": "Pantoprazole",
    "bayer": "Aspirin",
    "aspirine": "Aspirin",
    "acetylsalicylic acid": "Aspirin",
    "aricept": "Donepezil",
}

_DOSAGE_SUFFIX_RE = re.compile(
    r"(?:\b|(?<=[a-zA-Z]{3}))\d+(?:\.\d+)?\s*(?:mg|mcg|ug|g|ml|iu|%)\b"
    r"|(?:\b|(?<=[a-zA-Z]{4}))(?:xr|er|sr|cr|dr|dt|mr|ds|plus|forte)\b"
    r"|(?:\b|(?<=[a-zA-Z]{3}))\d{2,4}\b",
    re.IGNORECASE,
)


def _strip_dosage_tokens(text: str) -> str:
    """Removes strength/formulation suffixes like 'Dolo 650' -> 'Dolo', 'Metformin 500mg XR' -> 'Metformin'."""
    cleaned = _DOSAGE_SUFFIX_RE.sub(" ", text)
    return re.sub(r"\s+", " ", cleaned).strip(" -_/")

# Common non-pharmaceutical substances, solvents, placebos, excipients & non-drug entities
NON_PHARMACEUTICAL_SUBSTANCES = {
    # Water, simple solvents & hydration
    "water", "h2o", "h20", "drinking water", "tap water", "mineral water", "sterile water",
    "aqua", "dihydrogen monoxide", "distilled water", "saline", "normal saline",
    
    # Common atmospheric gases & elements
    "air", "oxygen", "nitrogen", "co2", "carbon dioxide", "hydrogen",
    
    # Common household food items, sugars & table condiments
    "sugar", "table salt", "salt", "sucrose", "fructose", "lactose",
    "food", "diet", "meal", "nutrition", "fasting", "fast",
    "tea", "coffee", "milk", "juice", "soda", "wine", "beer", "liquor",
    
    # Clinical trial controls, placebos & excipients
    "placebo", "vehicle", "control", "sham", "blank", "excipient",
    
    # Lifestyle & behavioral interventions
    "exercise", "walking", "running", "yoga", "meditation", "sleep", "sunlight",
    
    # Biological fluids & physical specimens
    "blood", "urine", "saliva", "stool", "feces", "semen", "sweat",
    "dirt", "soil", "dust", "smoke", "rock", "sand", "wood", "glass", "paper", "plastic"
}


def is_non_pharmaceutical(query_name: str) -> tuple[bool, Optional[str]]:
    """
    Checks if a query or any component of a comparison query represents a non-pharmaceutical substance.
    Returns (is_invalid, error_message).
    """
    if not query_name or not query_name.strip():
        return False, None

    cleaned_lower = query_name.strip().lower()
    tokens = [p.strip() for p in cleaned_lower.replace(" vs. ", " vs ").split(" vs ")]
    for token in tokens:
        if token in NON_PHARMACEUTICAL_SUBSTANCES:
            return True, (
                f"'{token.capitalize()}' is a common non-pharmaceutical substance/solvent, not an active pharmaceutical ingredient "
                "or therapeutic drug candidate. Please search for an active pharmaceutical molecule (e.g. Metformin, Semaglutide, Pembrolizumab)."
            )
    return False, None


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
        stripped = _strip_dosage_tokens(cleaned) or cleaned
        lower_q = stripped.lower()

        # 1. Check known brand mappings (after dosage stripping, e.g. "Dolo 650" -> "dolo" -> "Paracetamol")
        if lower_q in KNOWN_BRAND_MAPPINGS:
            canonical = KNOWN_BRAND_MAPPINGS[lower_q]
            synonyms = {cleaned.lower(), lower_q, canonical.lower()}
            # Add all other brand names for this canonical molecule
            for brand, gen in KNOWN_BRAND_MAPPINGS.items():
                if gen.lower() == canonical.lower():
                    synonyms.add(brand)
            logger.info("SynonymResolver: Mapped brand '%s' -> Canonical '%s'", cleaned, canonical)
            return SynonymResult(query_name=cleaned, canonical_name=canonical, synonyms=synonyms)

        # 2. Check if query is generic name of known compound
        canonical = stripped.capitalize()
        synonyms = {cleaned.lower(), lower_q}
        matched_known = False
        for brand, gen in KNOWN_BRAND_MAPPINGS.items():
            if gen.lower() == lower_q:
                synonyms.add(brand)
                canonical = gen
                matched_known = True

        # 3. Dynamic PubChem PUG-REST API lookup (also resolves canonical title for brand names like Ketorol -> Ketorolac)
        pubchem_synonyms, pubchem_title = self._fetch_pubchem_data(stripped)
        synonyms.update(pubchem_synonyms)
        if not matched_known and pubchem_title:
            canonical = pubchem_title
            synonyms.add(pubchem_title.lower())
            matched_known = True
            logger.info("SynonymResolver: PubChem resolved '%s' -> '%s'", cleaned, canonical)

        # 4. Free openFDA brand-to-generic lookup (no API key needed)
        if not matched_known:
            fda_generic = self._resolve_with_openfda(stripped)
            if fda_generic:
                canonical = fda_generic
                synonyms.add(fda_generic.lower())
                matched_known = True
                logger.info("SynonymResolver: openFDA resolved '%s' -> '%s'", cleaned, canonical)

        # 5. Gemini universal brand resolver (handles regional/Indian medicines like Azithral, Zerodol, etc.)
        if not matched_known:
            gemini_molecule = self._resolve_with_gemini(cleaned)
            if gemini_molecule:
                canonical = gemini_molecule
                synonyms.add(gemini_molecule.lower())
                logger.info("SynonymResolver: Gemini resolved '%s' -> '%s'", cleaned, canonical)

        return SynonymResult(
            query_name=cleaned,
            canonical_name=canonical,
            synonyms=synonyms
        )

    def _fetch_pubchem_synonyms(self, compound_name: str) -> Set[str]:
        """Backwards-compatible helper returning only the PubChem synonym set."""
        syns, _ = self._fetch_pubchem_data(compound_name)
        return syns

    def _fetch_pubchem_data(self, compound_name: str) -> tuple[Set[str], Optional[str]]:
        """
        Fetches synonyms and canonical compound Title from PubChem PUG-REST API.
        Fails silently and returns (empty set, None) if unreachable or non-existent.
        """
        syns: Set[str] = set()
        canonical_title: Optional[str] = None
        encoded = urllib.parse.quote(compound_name.strip())
        syn_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/synonyms/JSON"
        title_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/property/Title/JSON"

        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(syn_url)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_syns = (
                        data.get("InformationList", {})
                        .get("Information", [{}])[0]
                        .get("Synonym", [])
                    )
                    for item in raw_syns:
                        if isinstance(item, str) and len(item) <= 30:
                            syns.add(item.lower())
                            if len(syns) >= 10:
                                break

                    title_resp = client.get(title_url)
                    if title_resp.status_code == 200:
                        props = title_resp.json().get("PropertyTable", {}).get("Properties", [])
                        if props and props[0].get("Title"):
                            raw_title = props[0]["Title"].strip()
                            # Strip common salt suffixes for cleaner clinical/literature queries
                            base_title = re.sub(
                                r"\s+(?:tromethamine|trometamol|hydrochloride|hcl|sodium|potassium|maleate|tartrate|mesylate|sulfate)\b",
                                "",
                                raw_title,
                                flags=re.IGNORECASE,
                            ).strip()
                            canonical_title = (base_title or raw_title).title()
        except Exception as exc:
            logger.debug("PubChem lookup skipped for '%s': %s", compound_name, exc)

        return syns, canonical_title

    def _resolve_with_openfda(self, brand_name: str) -> Optional[str]:
        """Resolves a brand medicine name to its FDA generic molecule via openFDA (free, no key)."""
        clean = brand_name.strip().replace('"', '')
        if not clean:
            return None
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(
                    "https://api.fda.gov/drug/drugsfda.json",
                    params={"search": f'openfda.brand_name:"{clean}"', "limit": 1},
                )
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        gen_list = results[0].get("openfda", {}).get("generic_name", [])
                        if gen_list and isinstance(gen_list, list):
                            # Take primary molecule if single-ingredient
                            primary = gen_list[0].split(",")[0].strip()
                            if primary and len(primary) <= 45:
                                return primary.title()
        except Exception as exc:
            logger.debug("openFDA brand lookup skipped for '%s': %s", brand_name, exc)
        return None

    def _resolve_with_gemini(self, brand_or_query: str) -> Optional[str]:
        """Resolves an unknown brand/medicine name to its active generic molecule using Gemini with model fallback."""
        if not settings.GEMINI_API_KEY:
            logger.warning("SynonymResolver: GEMINI_API_KEY not set — skipping Gemini brand resolution for '%s'", brand_or_query)
            return None
        candidate_models = list(dict.fromkeys([
            settings.GEMINI_MODEL,
            "gemini-flash-lite-latest",
            "gemini-3.1-flash-lite-preview",
        ]))
        prompt = (
            f"What is the single primary generic active pharmaceutical molecule name for the medicine '{brand_or_query}'? "
            "Reply with ONLY the single generic molecule name (for example: Ketorolac, Paracetamol, Azithromycin) "
            "or UNKNOWN if it is not a medicine."
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 25},
        }
        with httpx.Client(timeout=8.0) as client:
            for model in candidate_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        cands = resp.json().get("candidates", [])
                        if cands:
                            ans = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip().strip(".\"'")
                            ans = ans.split(",")[0].strip()
                            if ans and ans.upper() != "UNKNOWN" and len(ans) <= 45 and "\n" not in ans:
                                return ans.title()
                    logger.debug("Gemini model %s returned %d for '%s'", model, resp.status_code, brand_or_query)
                except Exception as exc:
                    logger.debug("Gemini model %s failed for '%s': %s", model, brand_or_query, exc)
        return None

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
