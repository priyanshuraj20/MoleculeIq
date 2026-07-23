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
from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, field_validator

from app.orchestrator import run_research_pipeline
from app.services import AggregationService, ScoringService

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
async def execute_research_pipeline(payload: ResearchRequest):
    """
    FastAPI endpoint executing research pipeline, aggregation, and scoring.
    """
    molecule_name = payload.molecule_name
    start_time = time.monotonic()
    logger.info("[API: POST /api/research] Request received for molecule '%s'", molecule_name)

    try:
        # Step 1: Run LangGraph multi-agent research pipeline
        agent_state = await run_research_pipeline(molecule_name)

        # Step 2: Build normalized ResearchContext via AggregationService
        research_context = _agg_service.build_context(agent_state)

        # Step 3: Compute OpportunityScore & attach via ScoringService
        scored_context = _score_service.evaluate_and_attach(research_context)

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[API: POST /api/research] Completed for '%s' in %.2fs (Overall Score: %s)",
            molecule_name,
            elapsed,
            scored_context.score.overall_score if scored_context.score else "N/A"
        )

        # Convert dataclass structure to JSON-serializable dictionary
        return dataclasses.asdict(scored_context)

    except HTTPException:
        # Re-raise HTTPExceptions raised by validation or middleware
        raise
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        logger.error(
            "[API: POST /api/research] Internal error for '%s' after %.2fs: %s",
            molecule_name, elapsed, str(exc), exc_info=True
        )
        # Never expose raw python stack traces to API clients
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred while researching molecule '{molecule_name}'."
        )


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
    )
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
