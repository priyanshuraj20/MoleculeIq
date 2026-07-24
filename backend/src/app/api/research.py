"""
api/research.py

FastAPI REST API router for MoleculeIQ research pipeline execution.

Exposes:
  POST /api/research

Pipeline Execution Sequence:
  1. Validates incoming JSON request payload.
  2. Runs LangGraph research pipeline (Clinical, Literature, Market, Patent worker nodes).
  3. Invokes AggregationService to build normalized ResearchContext entity.
  4. Invokes ScoringService to compute deterministic OpportunityScore & confidence.
  5. Returns fully populated ResearchContext JSON payload.
"""

import dataclasses
import logging
import time
from fastapi import APIRouter, HTTPException, Query, Response, status, Depends
from pydantic import BaseModel, Field, field_validator

from app.orchestrator import run_research_pipeline
from app.services import AggregationService, ScoringService
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Research Pipeline"])

# Instantiate service singletons for endpoint execution
_agg_service   = AggregationService()
_score_service = ScoringService()


class ResearchRequest(BaseModel):
    """
    JSON request body for research pipeline execution.
    """
    molecule_name: str = Field(
        ...,
        description="Target drug or chemical molecule name to research (e.g. 'Metformin', 'Ibuprofen').",
        examples=["Metformin"]
    )

    @field_validator("molecule_name")
    @classmethod
    def validate_molecule_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("molecule_name parameter cannot be empty or whitespace.")
        return cleaned


@router.post(
    "/research",
    status_code=status.HTTP_200_OK,
    summary="Execute Multi-Agent Research Pipeline",
    description=(
        "Executes the full MoleculeIQ multi-agent research pipeline for a molecule. "
        "Gathers clinical trials, literature publications, market sales, and patent landscape data, "
        "aggregates domain context, and computes an overall commercial OpportunityScore."
    )
)
class ComparisonRequest(BaseModel):
    molecule_a: str = Field(..., description="First compound name (e.g. 'Metformin').")
    molecule_b: str = Field(..., description="Second compound name (e.g. 'Semaglutide').")


from app.services.cache_service import CacheService

_cache_service = CacheService()


@router.post(
    "/research",
    status_code=status.HTTP_200_OK,
    summary="Execute Multi-Agent Research Pipeline",
    description="Executes full research pipeline for single molecule or auto-detects ' vs ' comparison queries."
)
async def execute_research_pipeline(payload: ResearchRequest, current_user: dict = Depends(get_current_user)):
    """
    FastAPI endpoint executing research pipeline, aggregation, and scoring.
    Checks Redis cache first. On miss, runs LangGraph and saves report to Redis.
    """
    query_name = payload.molecule_name
    start_time = time.monotonic()
    logger.info("[API: POST /api/research] Request received for '%s'", query_name)

    # 1. Check Upstash Redis Cache
    try:
        cached_res = await _cache_service.get_report(query_name)
        if cached_res:
            logger.info("[API: POST /api/research] CACHE HIT for '%s' (served in 0.005s)", query_name)
            return cached_res
    except Exception as exc:
        logger.warning("[API: POST /api/research] Cache check error (bypassing cache): %s", str(exc))

    # 2. Check for comparison query (e.g., "Metformin vs Semaglutide")
    lower_q = query_name.lower()
    if " vs " in lower_q or " vs. " in lower_q:
        parts = lower_q.replace(" vs. ", " vs ").split(" vs ")
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            from app.services.comparison_service import ComparisonService
            comp_service = ComparisonService()
            comp_report = await comp_service.compare(parts[0].strip(), parts[1].strip())
            res_dict = {
                "mode": "comparison",
                "data": dataclasses.asdict(comp_report)
            }
            # Save to Redis (dynamic TTL from settings.REDIS_TTL_SECONDS)
            await _cache_service.set_report(query_name, res_dict)
            return res_dict

    try:
        # Step 1: Run LangGraph multi-agent research pipeline
        agent_state = await run_research_pipeline(query_name)

        # Step 2: Build normalized ResearchContext via AggregationService
        research_context = _agg_service.build_context(agent_state)

        # Step 2.5: Check for meaningful evidence
        if not research_context.has_meaningful_evidence:
            logger.warning("[API: POST /api/research] No evidence found for molecule '%s'", query_name)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No research data or evidence found for molecule '{query_name}'. Please verify the spelling or search for an active pharmaceutical compound."
            )

        # Step 3: Compute OpportunityScore & attach via ScoringService
        scored_context = _score_service.evaluate_and_attach(research_context)

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[API: POST /api/research] Completed for '%s' in %.2fs (Overall Score: %s)",
            query_name,
            elapsed,
            scored_context.score.overall_score if scored_context.score else "N/A"
        )

        res_dict = dataclasses.asdict(scored_context)
        res_dict["mode"] = "single"
        res_dict["processing_time_sec"] = elapsed

        # 3. Store result in Redis (dynamic TTL from settings.REDIS_TTL_SECONDS)
        await _cache_service.set_report(query_name, res_dict)

        return res_dict

    except HTTPException:
        raise
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        logger.error(
            "[API: POST /api/research] Internal error for '%s' after %.2fs: %s",
            query_name, elapsed, str(exc), exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred while researching molecule '{query_name}'."
        )


@router.post(
    "/research/compare",
    status_code=status.HTTP_200_OK,
    summary="Execute Parallel Molecule Comparison",
    description="Runs parallel research for two molecules and synthesizes side-by-side domain comparison matrix."
)
async def execute_molecule_comparison(payload: ComparisonRequest, current_user: dict = Depends(get_current_user)):
    """
    Dedicated endpoint for comparing two molecules side-by-side.
    """
    from app.services.comparison_service import ComparisonService
    comp_service = ComparisonService()
    comp_report = await comp_service.compare(payload.molecule_a, payload.molecule_b)
    return {
        "mode": "comparison",
        "data": dataclasses.asdict(comp_report)
    }


@router.post(
    "/research/json",
    status_code=status.HTTP_200_OK,
    summary="Generate Downloadable JSON Research Report",
    description="Returns standardized downstream API JSON report with processing metadata and citations."
)
async def export_research_json(payload: ResearchRequest, current_user: dict = Depends(get_current_user)):
    """
    FastAPI endpoint returning structured JSON report export.
    """
    from app.services.json_service import JSONReportService
    start_time = time.monotonic()
    query_name = payload.molecule_name

    agent_state = await run_research_pipeline(query_name)
    research_context = _agg_service.build_context(agent_state)

    if not research_context.has_meaningful_evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No research evidence found for molecule '{query_name}'."
        )

    scored_context = _score_service.evaluate_and_attach(research_context)
    elapsed = round(time.monotonic() - start_time, 2)

    json_service = JSONReportService()
    return json_service.generate(scored_context, query_input=query_name, processing_time_sec=elapsed)


@router.get(
    "/research/pdf",
    response_class=Response,
    summary="Download Executive PDF Research Report",
    description=(
        "Executes research pipeline, aggregation, scoring, and executive report synthesis, "
        "and returns a publication-grade C-suite PDF document ready for HTTP download."
    )
)
async def download_research_pdf(
    molecule_name: str = Query(
        ...,
        description="Target drug or chemical molecule name (e.g. 'Metformin', 'Ibuprofen').",
        examples=["Metformin"]
    ),
    current_user: dict = Depends(get_current_user)
):
    """
    FastAPI GET endpoint generating and serving an executive PDF research report.
    """
    cleaned_name = molecule_name.strip()
    if not cleaned_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="molecule_name query parameter cannot be empty or whitespace."
        )

    start_time = time.monotonic()
    logger.info("[API: GET /api/research/pdf] PDF request received for molecule '%s'", cleaned_name)

    try:
        from app.services import ExecutiveReportService, PDFReportService

        # Step 1: Run research pipeline
        agent_state = await run_research_pipeline(cleaned_name)

        # Step 2: Aggregate context
        context = _agg_service.build_context(agent_state)

        # Step 2.5: Check for meaningful evidence
        if not context.has_meaningful_evidence:
            logger.warning("[API: GET /api/research/pdf] No evidence found for molecule '%s'", cleaned_name)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No research evidence found for molecule '{cleaned_name}'. PDF report cannot be generated."
            )

        # Step 3: Compute opportunity score
        scored_context = _score_service.evaluate_and_attach(context)

        # Step 4: Synthesize executive report
        report_service = ExecutiveReportService()
        exec_report = await report_service.generate_report(scored_context)

        # Step 5: Render PDF document bytes
        pdf_service = PDFReportService()
        pdf_bytes = pdf_service.generate_pdf(scored_context, exec_report)

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[API: GET /api/research/pdf] PDF generated for '%s' in %.2fs (%d bytes)",
            cleaned_name, elapsed, len(pdf_bytes)
        )

        filename = f"{cleaned_name.replace(' ', '_')}_Executive_Report.pdf"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }

        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

    except HTTPException:
        raise
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        logger.error(
            "[API: GET /api/research/pdf] Internal error for '%s' after %.2fs: %s",
            cleaned_name, elapsed, str(exc), exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred while generating PDF for '{cleaned_name}'."
        )
