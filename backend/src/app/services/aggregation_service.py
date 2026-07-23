"""
services/aggregation_service.py

Research Aggregation Service.

Responsibility:
  Consumes the AgentState produced by the LangGraph research pipeline and deterministically
  combines clinical, literature, market, and patent domains into a unified ResearchContext entity.
  Calculates deterministic aggregate metadata without AI or LLM reasoning.
"""

import logging
import time

from app.domain.agent_state import AgentState
from app.domain.research_context import ResearchContext, ResearchMetadata

logger = logging.getLogger(__name__)


class AggregationService:
    """
    Deterministic service for building a normalized ResearchContext from AgentState.
    """

    def build_context(self, state: AgentState) -> ResearchContext:
        """
        Aggregates AgentState into a structured ResearchContext object.

        Args:
            state: AgentState output from LangGraph pipeline execution.

        Returns:
            ResearchContext containing attached domain objects and computed metadata.
        """
        molecule_name = state.molecule_name
        logger.info("[AggregationService] Starting aggregation for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        try:
            # 1. Identify populated domains
            domains_available = []
            if state.clinical_trials and not state.clinical_trials.is_empty:
                domains_available.append("clinical")
            if state.literature and not state.literature.is_empty:
                domains_available.append("literature")
            if state.market and not state.market.is_empty:
                domains_available.append("market")
            if state.patent and not state.patent.is_empty:
                domains_available.append("patent")

            logger.info(
                "[AggregationService] Received %d populated domain(s) for '%s': %s",
                len(domains_available), molecule_name, domains_available
            )

            # 2. Compute deterministic metadata
            metadata = self._compute_metadata(state, domains_available)

            # 3. Construct ResearchContext container
            context = ResearchContext(
                molecule_name=molecule_name,
                clinical=state.clinical_trials,
                literature=state.literature,
                market=state.market,
                patent=state.patent,
                metadata=metadata,
                warnings=list(state.warnings),
                errors=list(state.errors)
            )

            elapsed = round(time.monotonic() - start_time, 2)
            logger.info(
                "[AggregationService] Aggregation completed for '%s' in %.2fs (Available domains: %s)",
                molecule_name, elapsed, domains_available
            )
            return context

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            logger.error(
                "[AggregationService] Unexpected error during aggregation for '%s': %s (after %.2fs)",
                molecule_name, str(exc), elapsed
            )
            # Fallback — return minimal context with error recorded
            fallback_errors = list(state.errors) + [f"Aggregation failure for '{molecule_name}': {str(exc)}"]
            return ResearchContext(
                molecule_name=molecule_name,
                clinical=state.clinical_trials,
                literature=state.literature,
                market=state.market,
                patent=state.patent,
                metadata=ResearchMetadata(),
                warnings=list(state.warnings),
                errors=fallback_errors
            )

    # ------------------------------------------------------------------ #
    # Helper computation functions
    # ------------------------------------------------------------------ #

    def _compute_metadata(self, state: AgentState, domains_available: list[str]) -> ResearchMetadata:
        """
        Computes deterministic metrics across available domain objects.
        """
        meta = ResearchMetadata(domains_available=domains_available)

        # Clinical metrics
        if state.clinical_trials and not state.clinical_trials.is_empty:
            meta.total_trials = state.clinical_trials.total_found or len(state.clinical_trials.trials)
            meta.active_trials_count = len(state.clinical_trials.active_trials)
            meta.completed_trials_count = len(state.clinical_trials.completed_trials)

        # Literature metrics
        if state.literature and not state.literature.is_empty:
            meta.total_publications = state.literature.total_found or len(state.literature.publications)
            meta.highly_cited_papers_count = len(state.literature.highly_cited_papers)

        # Market metrics
        if state.market and not state.market.is_empty:
            regions = [dp.region for dp in state.market.data_points if dp.region]
            meta.market_regions = list(dict.fromkeys(regions))  # Deduplicated order-preserved regions
            meta.global_market_size_usd_mn = state.market.global_market_size_usd_mn
            meta.latest_market_cagr = state.market.latest_cagr

        # Patent metrics
        if state.patent and not state.patent.is_empty:
            meta.patent_count = len(state.patent.patents)
            meta.active_patents_count = len(state.patent.active_patents)
            meta.at_risk_patents_count = len(state.patent.at_risk_patents)
            meta.fto_summary = state.patent.fto_summary

        return meta


# Helper function for functional entrypoint
def build_research_context(state: AgentState) -> ResearchContext:
    """
    Standalone function entrypoint for building a ResearchContext from AgentState.
    """
    service = AggregationService()
    return service.build_context(state)
