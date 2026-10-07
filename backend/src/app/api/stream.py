"""
api/stream.py

FastAPI Server-Sent Events (SSE) streaming endpoint for real-time research progress tracking.

Exposes:
  GET /api/v1/research/stream?molecule_name=Metformin

Emits deterministic SSE event sequence:
  1. event: research_started
  2. event: clinical_started
  3. event: clinical_completed
  4. event: literature_started
  5. event: literature_completed
  6. event: market_started
  7. event: market_completed
  8. event: patent_started
  9. event: patent_completed
 10. event: aggregation_completed
 11. event: scoring_completed
 12. event: research_completed (Data payload contains full ResearchContext JSON)
"""

import asyncio
import dataclasses
import json
import logging
import time
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import StreamingResponse
from app.auth import get_current_user
from app.domain.agent_state import AgentState

from app.agents.clinical_agent import ClinicalTrialsAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.market_agent import MarketAgent
from app.agents.patent_agent import PatentAgent
from app.agents.repurposing_agent import RepurposingAgent
from app.services import AggregationService, ScoringService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/research", tags=["Research Streaming"])

# Reusable agent and service singletons
_clinical_agent   = ClinicalTrialsAgent()
_literature_agent = LiteratureAgent()
_market_agent     = MarketAgent()
_patent_agent     = PatentAgent()
_repurposing_agent = RepurposingAgent()
_agg_service      = AggregationService()
_score_service    = ScoringService()


def sse_json_serializer(obj):
    """
    JSON serializer helper for objects not serializable by default json.dumps
    (e.g., datetime.date and datetime.datetime).
    """
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not JSON serializable")


def format_sse(event: str, data: dict) -> str:
    """
    Formats event name and JSON dictionary into standard SSE wire format.
    Wire format:
      event: <event_name>\n
      data: <json_data>\n\n
    """
    json_str = json.dumps(data, default=sse_json_serializer, ensure_ascii=False)
    return f"event: {event}\ndata: {json_str}\n\n"


from app.services.synonym_service import SynonymResolver

_synonym_resolver = SynonymResolver()

async def generate_research_stream(molecule_name: str) -> AsyncGenerator[str, None]:
    """
    Async generator yielding real-time SSE progress events while running
    multi-agent research, aggregation, and scoring.
    Supports single compound research and dual molecule comparison ("A vs B").
    """
    start_time = time.monotonic()
    logger.info("[SSE Stream] Commencing stream for molecule '%s'", molecule_name)

    # 0. Validate pharmaceutical entity (reject non-drug substances like water, h2o, air, etc.)
    from app.services.synonym_service import is_non_pharmaceutical
    is_invalid, error_msg = is_non_pharmaceutical(molecule_name)
    if is_invalid:
        logger.info("[SSE Stream] Rejected non-pharmaceutical query: '%s'", molecule_name)
        yield format_sse("research_failed", {
            "molecule_name": molecule_name,
            "status": "failed",
            "error": error_msg,
            "execution_time_seconds": 0.01
        })
        return

    # 1. Check Redis cache
    try:
        from app.services.cache_service import CacheService
        _cache_service = CacheService()
        cached_res = await _cache_service.get_report(molecule_name)
        if cached_res:
            yield format_sse("research_started", {
                "molecule_name": molecule_name,
                "status": "cached",
                "message": f"Loading cached dossier for '{molecule_name}'...",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            yield format_sse("research_completed", cached_res)
            return
    except Exception as exc:
        logger.warning("[SSE Stream] Cache check warning: %s", exc)

    # 2. Check for comparison query (e.g. "Pembrolizumab vs Semaglutide")
    lower_q = molecule_name.lower()
    if " vs " in lower_q or " vs. " in lower_q:
        parts = lower_q.replace(" vs. ", " vs ").split(" vs ")
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            mol_a = parts[0].strip()
            mol_b = parts[1].strip()
            yield format_sse("research_started", {
                "molecule_name": f"{mol_a.title()} vs {mol_b.title()}",
                "query_name": molecule_name,
                "status": "started",
                "message": f"Benchmarking {mol_a.title()} against {mol_b.title()} across dual multi-agent pipelines...",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            yield format_sse("clinical_started", {
                "step": "clinical",
                "status": "in_progress",
                "message": f"Analyzing clinical trials for {mol_a.title()} and {mol_b.title()}..."
            })
            try:
                from app.services.comparison_service import ComparisonService
                comp_service = ComparisonService()
                
                # Execute comparison task asynchronously in background
                comp_task = asyncio.create_task(comp_service.compare(mol_a, mol_b))

                # Stream progressive milestones while dual pipelines execute
                progress_milestones = [
                    ("clinical_started", "clinical", "Mining ClinicalTrials.gov databases for both molecules...", 2.5),
                    ("clinical_completed", "clinical", f"Clinical trial records indexed ({mol_a.title()} vs {mol_b.title()}).", 2.5),
                    ("literature_started", "literature", "Querying scientific publications on Europe PMC...", 3.0),
                    ("literature_completed", "literature", "Scientific publication volumes & citations indexed.", 2.5),
                    ("market_started", "market", "Evaluating commercial market size & differential growth...", 2.5),
                    ("market_completed", "market", "Market size differentials mapped.", 2.5),
                    ("patent_started", "patent", "Reviewing patent landscape and freedom-to-operate horizons...", 2.5),
                    ("patent_completed", "patent", "Patent horizons and exclusivity windows evaluated.", 2.5),
                    ("repurposing_started", "repurposing", "Screening novel repurposing indications (Open Targets + ChEMBL)...", 2.5),
                    ("repurposing_completed", "repurposing", "Repurposing profiles cross-referenced.", 2.0),
                    ("aggregation_completed", "aggregation", "Comparative analysis matrices aggregated.", 1.5),
                    ("scoring_completed", "scoring", "Differential commercial advantages scored.", 1.5),
                ]

                idx = 0
                while not comp_task.done():
                    if idx < len(progress_milestones):
                        evt_name, step_name, msg_text, wait_sec = progress_milestones[idx]
                        yield format_sse(evt_name, {
                            "step": step_name,
                            "status": "in_progress" if "started" in evt_name else "completed",
                            "message": msg_text
                        })
                        idx += 1
                        try:
                            await asyncio.wait_for(asyncio.shield(comp_task), timeout=wait_sec)
                        except asyncio.TimeoutError:
                            pass
                    else:
                        # Keep-alive comment ping to prevent connection timeout
                        yield ": keepalive\n\n"
                        try:
                            await asyncio.wait_for(asyncio.shield(comp_task), timeout=2.0)
                        except asyncio.TimeoutError:
                            pass

                comp_report = await comp_task

                # Ensure terminal aggregation and scoring events are emitted
                yield format_sse("aggregation_completed", {
                    "step": "aggregation",
                    "status": "completed",
                    "message": "Comparative analysis matrices aggregated."
                })
                yield format_sse("scoring_completed", {
                    "step": "scoring",
                    "status": "completed",
                    "message": "Differential commercial advantages scored."
                })

                res_dict = {
                    "mode": "comparison",
                    "data": dataclasses.asdict(comp_report)
                }

                # Store comparison in Redis / fallback cache
                try:
                    await _cache_service.set_report(molecule_name, res_dict)
                except Exception:
                    pass

                yield format_sse("research_completed", res_dict)
                return

            except Exception as exc:
                err_msg = f"Comparison failed between '{mol_a}' and '{mol_b}': {str(exc)}"
                logger.error("[SSE Stream] %s", err_msg, exc_info=True)
                yield format_sse("research_failed", {
                    "molecule_name": molecule_name,
                    "status": "failed",
                    "error": err_msg,
                    "execution_time_seconds": round(time.monotonic() - start_time, 2)
                })
                return

    syn_result = _synonym_resolver.resolve(molecule_name)
    canonical = syn_result.canonical_name or molecule_name

    state = AgentState(
        molecule_name=canonical,
        synonyms=list(syn_result.synonyms),
    )

    try:
        # Event 1: research_started
        yield format_sse("research_started", {
            "molecule_name": canonical,
            "query_name": molecule_name,
            "status": "started",
            "message": f"Finding molecule '{canonical}' & resolving synonyms...",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

        # Step 1: Clinical Trials Agent
        yield format_sse("clinical_started", {"step": "clinical", "status": "in_progress", "message": "Searching clinical databases..."})
        state = await _clinical_agent.execute(state)
        trials_count = len(state.clinical_trials.trials) if state.clinical_trials else 0
        yield format_sse("clinical_completed", {
            "step": "clinical",
            "status": "completed",
            "message": f"Clinical analysis complete ({trials_count} trials mapped)",
            "trials_found": trials_count,
            "total_found": state.clinical_trials.total_found if state.clinical_trials else 0
        })

        # Step 2: Scientific Literature Agent
        yield format_sse("literature_started", {"step": "literature", "status": "in_progress", "message": "Collecting scientific literature..."})
        state = await _literature_agent.execute(state)
        pubs_count = len(state.literature.publications) if state.literature else 0
        yield format_sse("literature_completed", {
            "step": "literature",
            "status": "completed",
            "message": f"Literature analysis complete ({pubs_count} papers mapped)",
            "papers_found": pubs_count,
            "total_found": state.literature.total_found if state.literature else 0
        })

        # Step 3: Market Insights Agent
        yield format_sse("market_started", {"step": "market", "status": "in_progress", "message": "Analyzing market intelligence..."})
        state = _market_agent.execute(state)
        points_count = len(state.market.data_points) if state.market else 0
        yield format_sse("market_completed", {
            "step": "market",
            "status": "completed",
            "message": "Market analysis complete",
            "points_found": points_count,
            "global_size_usd_mn": state.market.global_market_size_usd_mn if state.market else None
        })

        # Step 4: Patent Landscape Agent
        yield format_sse("patent_started", {"step": "patent", "status": "in_progress", "message": "Searching patent databases..."})
        state = _patent_agent.execute(state)
        patents_count = len(state.patent.patents) if state.patent else 0
        yield format_sse("patent_completed", {
            "step": "patent",
            "status": "completed",
            "message": f"Patent analysis complete ({patents_count} patents mapped)",
            "records_found": patents_count,
            "fto_summary": state.patent.fto_summary if state.patent else "N/A"
        })

        # Step 4.5: Drug Repurposing Discovery Agent
        yield format_sse("repurposing_started", {"step": "repurposing", "status": "in_progress", "message": "Discovering drug repurposing indications..."})
        state = await _repurposing_agent.execute(state)
        candidates_count = len(state.repurposing.candidates) if state.repurposing else 0
        yield format_sse("repurposing_completed", {
            "step": "repurposing",
            "status": "completed",
            "message": f"Repurposing discovery complete ({candidates_count} candidate indications identified)",
            "candidates_found": candidates_count,
            "provenance": "real"
        })

        # Step 5: Research Aggregation Service
        context = _agg_service.build_context(state)
        yield format_sse("aggregation_completed", {
            "step": "aggregation",
            "status": "completed",
            "domains_available": context.metadata.domains_available
        })

        # Step 5.5: Validate meaningful evidence existence
        if not context.has_meaningful_evidence:
            err_msg = f"No research data or evidence found for molecule '{molecule_name}'. Please verify the spelling or search for an active pharmaceutical compound."
            logger.warning("[SSE Stream] Terminating stream for '%s': %s", molecule_name, err_msg)
            yield format_sse("research_failed", {
                "molecule_name": molecule_name,
                "status": "failed",
                "error": err_msg,
                "execution_time_seconds": round(time.monotonic() - start_time, 2)
            })
            return

        # Step 6: Hybrid Opportunity Scoring Service
        scored_context = _score_service.evaluate_and_attach(context)
        yield format_sse("scoring_completed", {
            "step": "scoring",
            "status": "completed",
            "overall_score": scored_context.score.overall_score if scored_context.score else 0.0,
            "confidence_score": scored_context.score.confidence_score if scored_context.score else 0.0
        })

        # Final Event: research_completed with full serialized ResearchContext
        elapsed = round(time.monotonic() - start_time, 2)
        context_dict = dataclasses.asdict(scored_context)

        logger.info("[SSE Stream] Stream completed for '%s' in %.2fs", molecule_name, elapsed)
        try:
            from app.services.cache_service import CacheService
            _cache_service = CacheService()
            await _cache_service.set_report(molecule_name, context_dict)
        except Exception:
            pass
        yield format_sse("research_completed", context_dict)

    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        error_msg = f"Streaming research pipeline failed for '{molecule_name}': {str(exc)}"
        logger.error("[SSE Stream] %s (after %.2fs)", error_msg, elapsed)
        yield format_sse("research_failed", {
            "molecule_name": molecule_name,
            "status": "failed",
            "error": error_msg,
            "execution_time_seconds": elapsed
        })


@router.get(
    "/stream",
    summary="Real-Time Research Pipeline Stream (SSE)",
    description=(
        "Establishes a Server-Sent Events (SSE) connection that streams real-time progress events "
        "as each worker agent executes. The final event ('research_completed') contains the full ResearchContext."
    )
)
async def stream_research_pipeline(
    molecule_name: str = Query(
        ...,
        description="Target drug or chemical molecule name to research (e.g. 'Metformin', 'Ibuprofen').",
        examples=["Metformin"]
    ),
    current_user: dict = Depends(get_current_user)
):
    """
    FastAPI GET endpoint streaming real-time SSE research events.
    """
    cleaned_name = molecule_name.strip()
    if not cleaned_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="molecule_name query parameter cannot be empty or whitespace."
        )

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disables proxy buffering (e.g. Nginx)
    }

    return StreamingResponse(
        generate_research_stream(cleaned_name),
        media_type="text/event-stream",
        headers=headers
    )
