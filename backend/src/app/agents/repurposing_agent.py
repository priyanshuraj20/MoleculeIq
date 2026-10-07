"""
agents/repurposing_agent.py

Drug Repurposing Discovery Worker Agent.

Responsibility:
  1. Accepts AgentState.
  2. Resolves molecule to ChEMBL ID (via OpenTargetsClient / ChEMBL fallback).
  3. Fetches mechanism of action and protein targets from Open Targets Platform.
  4. Fetches already-known / approved indications for the drug.
  5. Queries target-associated diseases and filters out known indications strictly
     by normalized disease ontology ID (EFO / MONDO IDs).
  6. Ranks candidate indications by target association score and selects top 5.
  7. Queries ClinicalTrials.gov and Europe PMC for real external supporting evidence
     (real NCT IDs and PMIDs only — zero padding).
  8. Generates a concise factual explanation (via Gemini or deterministic fallback)
     strictly bounded by the provided structured data and tagged as AI-generated.
  9. Caches the result in Redis with TTL.
 10. Attaches RepurposingDomain to state.repurposing.
"""

import json
import logging
import time
from typing import Optional, List, Dict, Any, Set
import httpx

from app.core.config import settings
from app.domain.agent_state import AgentState
from app.domain.repurposing import (
    EvidenceItem,
    RepurposingCandidate,
    RepurposingDomain,
)
from app.infrastructure.clients.opentargets_client import OpenTargetsClient
from app.infrastructure.clients.clinicaltrials_client import ClinicalTrialsClient
from app.infrastructure.clients.europepmc_client import EuropePMCClient
from app.infrastructure.cache.redis_client import AsyncRedisClient
from app.services.synonym_service import SynonymResolver

logger = logging.getLogger(__name__)


def normalize_ontology_id(oid: str) -> str:
    """Normalizes ontology IDs across colon/underscore conventions (e.g. MONDO:0005233 -> MONDO_0005233)."""
    if not oid:
        return ""
    return oid.strip().replace(":", "_").upper()


class RepurposingAgent:
    """
    Worker agent for discovering new indications for existing pharmaceutical compounds.
    """

    def __init__(
        self,
        ot_client: Optional[OpenTargetsClient] = None,
        ct_client: Optional[ClinicalTrialsClient] = None,
        epmc_client: Optional[EuropePMCClient] = None,
        redis_client: Optional[AsyncRedisClient] = None,
        synonym_resolver: Optional[SynonymResolver] = None,
    ):
        self._ot_client = ot_client or OpenTargetsClient()
        self._ct_client = ct_client or ClinicalTrialsClient()
        self._epmc_client = epmc_client or EuropePMCClient()
        self._redis = redis_client or AsyncRedisClient()
        self._resolver = synonym_resolver or SynonymResolver()

    async def execute(self, state: AgentState) -> AgentState:
        molecule_name = state.molecule_name
        logger.info("[RepurposingAgent] Starting repurposing discovery for '%s'", molecule_name)
        start_time = time.monotonic()

        # 1. Resolve canonical name using existing SynonymResolver
        syn_result = self._resolver.resolve(molecule_name)
        canonical = syn_result.canonical_name or molecule_name
        cache_key = f"moleculeiq:repurposing:{canonical.lower()}"

        try:
            # 2. Check Redis cache
            cached_data = await self._redis.get(cache_key)
            if cached_data:
                try:
                    parsed = json.loads(cached_data)
                    candidates = [
                        RepurposingCandidate(
                            disease_name=c["disease_name"],
                            disease_id=c["disease_id"],
                            association_score=float(c["association_score"]),
                            target_symbols=c.get("target_symbols", []),
                            target_names=c.get("target_names", []),
                            mechanisms_of_action=c.get("mechanisms_of_action", []),
                            evidence=[
                                EvidenceItem(
                                    evidence_type=e["evidence_type"],
                                    id=e["id"],
                                    title=e["title"],
                                    url=e["url"]
                                )
                                for e in c.get("evidence", [])
                            ],
                            evidence_counts=c.get("evidence_counts", {"trials_count": 0, "publications_count": 0}),
                            explanation=c.get("explanation", ""),
                            explanation_ai_generated=c.get("explanation_ai_generated", True),
                            provenance=c.get("provenance", "real"),
                        )
                        for c in parsed.get("candidates", [])
                    ]
                    domain = RepurposingDomain(
                        molecule_name=canonical,
                        chembl_id=parsed.get("chembl_id"),
                        candidates=candidates,
                        total_candidates=len(candidates),
                        source="Open Targets Platform",
                        provenance="real",
                    )
                    state.repurposing = domain
                    elapsed = round(time.monotonic() - start_time, 2)
                    logger.info("[RepurposingAgent] Served from cache in %.2fs (%d candidates)", elapsed, len(candidates))
                    return state
                except Exception as exc:
                    logger.warning("[RepurposingAgent] Cache deserialize error: %s (querying live)", str(exc))

            # 3. Resolve drug to ChEMBL ID via Open Targets search (with ChEMBL REST fallback)
            chembl_id = await self._ot_client.search_drug(canonical)
            if not chembl_id and molecule_name != canonical:
                chembl_id = await self._ot_client.search_drug(molecule_name)

            if not chembl_id:
                logger.warning("[RepurposingAgent] Could not resolve ChEMBL ID for '%s'", molecule_name)
                state.repurposing = RepurposingDomain(
                    molecule_name=canonical,
                    candidates=[],
                    total_candidates=0,
                    source="Open Targets Platform",
                    provenance="real"
                )
                return state

            # 4. Fetch mechanisms of action, targets, and known indications from Open Targets
            drug_details = await self._ot_client.get_drug_details(chembl_id)
            if not drug_details:
                logger.warning("[RepurposingAgent] No drug details returned for %s", chembl_id)
                state.repurposing = RepurposingDomain(
                    molecule_name=canonical,
                    chembl_id=chembl_id,
                    candidates=[],
                    total_candidates=0,
                    provenance="real"
                )
                return state

            # Extract known indications as normalized ontology IDs
            known_indication_ids: Set[str] = set()
            for row in (drug_details.get("indications", {}).get("rows") or []):
                disease_obj = row.get("disease")
                if disease_obj and disease_obj.get("id"):
                    known_indication_ids.add(normalize_ontology_id(disease_obj["id"]))

            logger.info("[RepurposingAgent] Found %d known/approved indication IDs for %s", len(known_indication_ids), canonical)

            # Extract targets and mechanisms of action
            targets: Dict[str, Dict[str, Any]] = {}
            for moa_row in (drug_details.get("mechanismsOfAction", {}).get("rows") or []):
                moa_desc = moa_row.get("mechanismOfAction") or ""
                for target_obj in (moa_row.get("targets") or []):
                    tid = target_obj.get("id")
                    if tid:
                        if tid not in targets:
                            targets[tid] = {
                                "id": tid,
                                "symbol": target_obj.get("approvedSymbol") or tid,
                                "name": target_obj.get("approvedName") or "",
                                "mechanisms": []
                            }
                        if moa_desc and moa_desc not in targets[tid]["mechanisms"]:
                            targets[tid]["mechanisms"].append(moa_desc)

            logger.info("[RepurposingAgent] Identified %d protein target(s) for %s", len(targets), canonical)

            if not targets:
                logger.info("[RepurposingAgent] No protein targets associated with %s", canonical)
                state.repurposing = RepurposingDomain(
                    molecule_name=canonical,
                    chembl_id=chembl_id,
                    candidates=[],
                    total_candidates=0,
                    provenance="real"
                )
                return state

            # 5. For each target, query associated diseases with score
            candidate_pool: Dict[str, Dict[str, Any]] = {}

            # Query up to 10 targets to maintain low latency
            for tid, tinfo in list(targets.items())[:10]:
                assoc_rows = await self._ot_client.get_target_associated_diseases(tid, size=100)
                for a in assoc_rows:
                    dis = a.get("disease")
                    score = float(a.get("score") or 0.0)
                    if not dis or not dis.get("id"):
                        continue

                    raw_did = dis["id"]
                    norm_did = normalize_ontology_id(raw_did)

                    # Exclude diseases already approved or investigational for the drug
                    if norm_did in known_indication_ids:
                        continue

                    # Filter out generic high-level umbrella terms that aren't actionable
                    name_lower = dis.get("name", "").lower()
                    if name_lower in ("disease", "genetic disorder", "syndrome", "phenotype"):
                        continue

                    if norm_did not in candidate_pool:
                        candidate_pool[norm_did] = {
                            "disease_name": dis.get("name", "Unknown Disease"),
                            "disease_id": raw_did,
                            "association_score": score,
                            "target_symbols": [tinfo["symbol"]],
                            "target_names": [tinfo["name"]] if tinfo["name"] else [],
                            "mechanisms": list(tinfo["mechanisms"]),
                        }
                    else:
                        if score > candidate_pool[norm_did]["association_score"]:
                            candidate_pool[norm_did]["association_score"] = score
                        if tinfo["symbol"] not in candidate_pool[norm_did]["target_symbols"]:
                            candidate_pool[norm_did]["target_symbols"].append(tinfo["symbol"])
                        if tinfo["name"] and tinfo["name"] not in candidate_pool[norm_did]["target_names"]:
                            candidate_pool[norm_did]["target_names"].append(tinfo["name"])
                        for m in tinfo["mechanisms"]:
                            if m not in candidate_pool[norm_did]["mechanisms"]:
                                candidate_pool[norm_did]["mechanisms"].append(m)

            # 6. Rank remaining diseases by association score. Take top 5.
            sorted_candidates = sorted(
                candidate_pool.values(),
                key=lambda x: x["association_score"],
                reverse=True
            )[:5]

            logger.info(
                "[RepurposingAgent] Selected top %d candidate indications for %s",
                len(sorted_candidates), canonical
            )

            # 7. For each candidate, attach real supporting evidence
            final_candidates: List[RepurposingCandidate] = []
            for item in sorted_candidates:
                evidence_items, evidence_counts = await self._fetch_real_evidence(
                    drug_name=canonical,
                    disease_name=item["disease_name"]
                )

                # 8. Generate short explanation strictly bounded by provided data
                explanation = await self._generate_explanation(
                    drug_name=canonical,
                    candidate=item,
                    evidence_counts=evidence_counts
                )

                candidate_obj = RepurposingCandidate(
                    disease_name=item["disease_name"],
                    disease_id=item["disease_id"],
                    association_score=round(item["association_score"], 4),
                    target_symbols=item["target_symbols"],
                    target_names=item["target_names"],
                    mechanisms_of_action=item["mechanisms"],
                    evidence=evidence_items,
                    evidence_counts=evidence_counts,
                    explanation=explanation,
                    explanation_ai_generated=True,
                    provenance="real"
                )
                final_candidates.append(candidate_obj)

            domain = RepurposingDomain(
                molecule_name=canonical,
                chembl_id=chembl_id,
                candidates=final_candidates,
                total_candidates=len(final_candidates),
                source="Open Targets Platform",
                provenance="real",
            )

            state.repurposing = domain

            # 9. Cache in Redis (serialize to JSON)
            try:
                cache_payload = {
                    "chembl_id": chembl_id,
                    "candidates": [
                        {
                            "disease_name": c.disease_name,
                            "disease_id": c.disease_id,
                            "association_score": c.association_score,
                            "target_symbols": c.target_symbols,
                            "target_names": c.target_names,
                            "mechanisms_of_action": c.mechanisms_of_action,
                            "evidence": [
                                {
                                    "evidence_type": e.evidence_type,
                                    "id": e.id,
                                    "title": e.title,
                                    "url": e.url,
                                }
                                for e in c.evidence
                            ],
                            "evidence_counts": c.evidence_counts,
                            "explanation": c.explanation,
                            "explanation_ai_generated": c.explanation_ai_generated,
                            "provenance": c.provenance,
                        }
                        for c in final_candidates
                    ]
                }
                await self._redis.set(cache_key, json.dumps(cache_payload), ttl_seconds=settings.REDIS_TTL_SECONDS)
                logger.info("[RepurposingAgent] Saved %d candidates to Redis (key='%s')", len(final_candidates), cache_key)
            except Exception as cache_err:
                logger.warning("[RepurposingAgent] Failed to cache in Redis: %s", str(cache_err))

            elapsed = round(time.monotonic() - start_time, 2)
            logger.info("[RepurposingAgent] Completed in %.2fs: %d candidates found", elapsed, len(final_candidates))

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            err_msg = f"RepurposingAgent failed for '{molecule_name}': {str(exc)}"
            logger.error("[RepurposingAgent] %s (after %.2fs)", err_msg, elapsed, exc_info=True)
            state.repurposing = RepurposingDomain(
                molecule_name=canonical,
                candidates=[],
                total_candidates=0,
                provenance="real"
            )
            state.warnings.append(err_msg)

        return state

    # ------------------------------------------------------------------ #
    # Helper: Real Evidence Retrieval (ClinicalTrials.gov & Europe PMC)
    # ------------------------------------------------------------------ #

    async def _fetch_real_evidence(self, drug_name: str, disease_name: str) -> tuple[List[EvidenceItem], Dict[str, int]]:
        """
        Retrieves live clinical trials and scientific publications for (drug AND disease).
        Citations and counts strictly come from real API responses.
        """
        evidence_items: List[EvidenceItem] = []
        trials_count = 0
        pubs_count = 0

        # 1. Search ClinicalTrials.gov
        try:
            ct_url = f"{settings.CLINICALTRIALS_BASE_URL}/studies"
            query_term = f"{drug_name} {disease_name}"
            ct_res = await self._ct_client._get(
                ct_url,
                params={"query.term": query_term, "pageSize": 3, "format": "json"}
            )
            studies = ct_res.get("studies", [])
            trials_count = ct_res.get("totalCount", len(studies))
            for s in studies[:2]:
                protocol = s.get("protocolSection", {})
                nct_id = protocol.get("identificationModule", {}).get("nctId")
                title = protocol.get("identificationModule", {}).get("briefTitle") or "Untitled Trial"
                if nct_id:
                    evidence_items.append(EvidenceItem(
                        evidence_type="clinical_trial",
                        id=nct_id,
                        title=title,
                        url=f"https://clinicaltrials.gov/study/{nct_id}"
                    ))
        except Exception as exc:
            logger.debug("[RepurposingAgent] Clinical trials query failed for '%s + %s': %s", drug_name, disease_name, exc)

        # 2. Search Europe PMC
        try:
            epmc_url = f"{settings.EUROPEPMC_BASE_URL}/search"
            clean_drug = drug_name.strip().replace('"', '')
            clean_dis = disease_name.strip().replace('"', '')
            query = f'"{clean_drug}" AND "{clean_dis}" AND (SRC:MED OR SRC:PMC)'
            epmc_res = await self._epmc_client._get(
                epmc_url,
                params={"query": query, "pageSize": 3, "format": "json", "resultType": "lite"}
            )
            results = epmc_res.get("resultList", {}).get("result", [])
            pubs_count = epmc_res.get("hitCount", len(results))
            for p in results[:2]:
                pmid = p.get("pmid")
                title = p.get("title", "Untitled Article").rstrip(".")
                if pmid:
                    evidence_items.append(EvidenceItem(
                        evidence_type="literature",
                        id=pmid,
                        title=title,
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    ))
        except Exception as exc:
            logger.debug("[RepurposingAgent] Europe PMC query failed for '%s + %s': %s", drug_name, disease_name, exc)

        return evidence_items, {"trials_count": trials_count, "publications_count": pubs_count}

    # ------------------------------------------------------------------ #
    # Helper: Constrained LLM or Deterministic Explanation
    # ------------------------------------------------------------------ #

    async def _generate_explanation(self, drug_name: str, candidate: Dict[str, Any], evidence_counts: Dict[str, int]) -> str:
        """
        Generates a 2-3 sentence 'why this could work' explanation.
        Strictly forbidden from inventing facts, IDs, or citations not in the data.
        """
        targets_str = ", ".join(candidate["target_symbols"])
        score = candidate["association_score"]
        disease = candidate["disease_name"]
        trials_n = evidence_counts.get("trials_count", 0)
        pubs_n = evidence_counts.get("publications_count", 0)

        # 1. Attempt Gemini if configured
        if settings.GEMINI_API_KEY:
            try:
                system_prompt = (
                    "You are a strict pharmaceutical computational biologist. "
                    "Write exactly 2 concise sentences explaining why the given drug might be repurposed for the candidate disease. "
                    "STRICT RULES: Rely ONLY on the provided structured facts: target(s), association score, and found trial/paper counts. "
                    "You must NOT invent external clinical data, trials, IDs, mechanisms, or claims."
                )
                user_prompt = (
                    f"Drug: {drug_name}\n"
                    f"Candidate Indication: {disease}\n"
                    f"Associated Target(s): {targets_str}\n"
                    f"Target-Disease Open Targets Score: {score:.3f}\n"
                    f"Related Registered Clinical Trials: {trials_n}\n"
                    f"Related Scientific Publications: {pubs_n}"
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": system_prompt},
                                {"text": user_prompt}
                            ]
                        }
                    ],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 150}
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        cands = resp.json().get("candidates", [])
                        if cands:
                            text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            if text:
                                return text
            except Exception as exc:
                logger.debug("[RepurposingAgent] Gemini explanation generation skipped: %s", exc)

        # 2. Deterministic evidence-based fallback
        evidence_phrase = []
        if trials_n > 0:
            evidence_phrase.append(f"{trials_n} related clinical study record(s)")
        if pubs_n > 0:
            evidence_phrase.append(f"{pubs_n} indexed scientific publication(s)")
        evidence_str = f" Supported by {' and '.join(evidence_phrase)}." if evidence_phrase else " Primary clinical validation is in early stages."

        return (
            f"{drug_name} acts on target {targets_str}, which shares a strong genetic and biological association "
            f"(score {score:.2f}) with {disease} in Open Targets Platform.{evidence_str}"
        )


async def run_repurposing_agent(state: AgentState) -> AgentState:
    """Standalone entrypoint for LangGraph node."""
    agent = RepurposingAgent()
    return await agent.execute(state)
