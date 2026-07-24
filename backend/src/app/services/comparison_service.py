"""
services/comparison_service.py

Molecule Comparison Engine.
Executes parallel multi-agent research pipelines for two molecules and synthesizes
a side-by-side comparative analysis report with category winner determinations.
"""

import asyncio
import logging
import time
from typing import Tuple

from app.domain.comparison import (
    ComparisonReport,
    DomainComparisonItem,
    ExecutiveComparisonSummary,
)
from app.domain.research_context import ResearchContext
from app.orchestrator.graph import run_research_pipeline
from app.services.aggregation_service import AggregationService
from app.services.scoring_service import ScoringService

logger = logging.getLogger(__name__)


class ComparisonService:
    """
    Service coordinating side-by-side comparative research between two molecules.
    """

    def __init__(self):
        self._agg_service = AggregationService()
        self._scoring_service = ScoringService()

    async def compare(self, molecule_a_name: str, molecule_b_name: str) -> ComparisonReport:
        """
        Executes parallel multi-agent research for molecule A and molecule B,
        then synthesizes a structured ComparisonReport.
        """
        start_time = time.monotonic()
        logger.info(
            "[ComparisonService] Executing comparative research: '%s' vs '%s'",
            molecule_a_name, molecule_b_name
        )

        # 1. Run parallel research pipelines
        state_a, state_b = await asyncio.gather(
            run_research_pipeline(molecule_a_name),
            run_research_pipeline(molecule_b_name)
        )

        # 2. Build contexts & calculate opportunity scores
        context_a = self._agg_service.build_context(state_a)
        context_b = self._agg_service.build_context(state_b)

        if context_a.has_meaningful_evidence:
            self._scoring_service.evaluate_and_attach(context_a)
        if context_b.has_meaningful_evidence:
            self._scoring_service.evaluate_and_attach(context_b)

        name_a = context_a.molecule_name
        name_b = context_b.molecule_name

        # 3. Domain Comparisons
        clin_comp = self._compare_clinical(context_a, context_b, name_a, name_b)
        lit_comp = self._compare_literature(context_a, context_b, name_a, name_b)
        pat_comp = self._compare_patent(context_a, context_b, name_a, name_b)
        mkt_comp = self._compare_market(context_a, context_b, name_a, name_b)

        # 4. Overall Winner & Score Difference
        score_a = context_a.score.overall_score if context_a.score else 0.0
        score_b = context_b.score.overall_score if context_b.score else 0.0
        diff = round(abs(score_a - score_b), 1)

        if score_a > score_b:
            overall_winner = "molecule_a"
        elif score_b > score_a:
            overall_winner = "molecule_b"
        else:
            overall_winner = "tie"

        # 5. Executive Comparison Summary
        exec_summary = self._generate_executive_comparison_summary(
            context_a, context_b, name_a, name_b, clin_comp, pat_comp, mkt_comp, overall_winner
        )

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[ComparisonService] Completed comparison in %.2fs (Winner: %s, Diff: %.1f)",
            elapsed, overall_winner, diff
        )

        return ComparisonReport(
            molecule_a_name=name_a,
            molecule_b_name=name_b,
            molecule_a_context=context_a,
            molecule_b_context=context_b,
            clinical_comparison=clin_comp,
            literature_comparison=lit_comp,
            patent_comparison=pat_comp,
            market_comparison=mkt_comp,
            overall_winner=overall_winner,
            score_difference=diff,
            executive_summary=exec_summary,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            processing_time_sec=elapsed
        )

    def _compare_clinical(self, ctx_a: ResearchContext, ctx_b: ResearchContext, name_a: str, name_b: str) -> DomainComparisonItem:
        t_a = len(ctx_a.clinical.trials) if ctx_a.clinical else 0
        t_b = len(ctx_b.clinical.trials) if ctx_b.clinical else 0

        val_a = f"{t_a} trial(s)"
        val_b = f"{t_b} trial(s)"

        if t_a > t_b:
            winner = "molecule_a"
            summary = f"{name_a} demonstrates higher clinical activity ({t_a} vs {t_b} trials)."
        elif t_b > t_a:
            winner = "molecule_b"
            summary = f"{name_b} demonstrates higher clinical activity ({t_b} vs {t_a} trials)."
        else:
            winner = "tie"
            summary = f"Both molecules show equal clinical trial volume ({t_a} trials each)."

        return DomainComparisonItem(
            domain_name="Clinical Evidence",
            molecule_a_val=val_a,
            molecule_b_val=val_b,
            winner=winner,
            summary=summary
        )

    def _compare_literature(self, ctx_a: ResearchContext, ctx_b: ResearchContext, name_a: str, name_b: str) -> DomainComparisonItem:
        p_a = len(ctx_a.literature.publications) if ctx_a.literature else 0
        p_b = len(ctx_b.literature.publications) if ctx_b.literature else 0

        val_a = f"{p_a} paper(s)"
        val_b = f"{p_b} paper(s)"

        if p_a > p_b:
            winner = "molecule_a"
            summary = f"{name_a} leads in scientific literature volume ({p_a} vs {p_b} publications)."
        elif p_b > p_a:
            winner = "molecule_b"
            summary = f"{name_b} leads in scientific literature volume ({p_b} vs {p_a} publications)."
        else:
            winner = "tie"
            summary = f"Equal publication volume identified ({p_a} papers each)."

        return DomainComparisonItem(
            domain_name="Scientific Literature",
            molecule_a_val=val_a,
            molecule_b_val=val_b,
            winner=winner,
            summary=summary
        )

    def _compare_patent(self, ctx_a: ResearchContext, ctx_b: ResearchContext, name_a: str, name_b: str) -> DomainComparisonItem:
        score_a = ctx_a.score.patent_score if ctx_a.score else 50.0
        score_b = ctx_b.score.patent_score if ctx_b.score else 50.0

        val_a = f"FTO Score: {score_a:.0f}/100 ({ctx_a.metadata.fto_summary})"
        val_b = f"FTO Score: {score_b:.0f}/100 ({ctx_b.metadata.fto_summary})"

        if score_a > score_b:
            winner = "molecule_a"
            summary = f"{name_a} presents lower FTO patent barrier risks."
        elif score_b > score_a:
            winner = "molecule_b"
            summary = f"{name_b} presents lower FTO patent barrier risks."
        else:
            winner = "tie"
            summary = "Both compounds exhibit similar patent landscape barrier characteristics."

        return DomainComparisonItem(
            domain_name="Patent & FTO Landscape",
            molecule_a_val=val_a,
            molecule_b_val=val_b,
            winner=winner,
            summary=summary
        )

    def _compare_market(self, ctx_a: ResearchContext, ctx_b: ResearchContext, name_a: str, name_b: str) -> DomainComparisonItem:
        sz_a = ctx_a.metadata.global_market_size_usd_mn or 0.0
        sz_b = ctx_b.metadata.global_market_size_usd_mn or 0.0

        val_a = f"${sz_a:,.1f}M USD" if sz_a > 0 else "Limited Data"
        val_b = f"${sz_b:,.1f}M USD" if sz_b > 0 else "Limited Data"

        if sz_a > sz_b:
            winner = "molecule_a"
            summary = f"{name_a} addresses a significantly larger market opportunity (${sz_a:,.1f}M vs ${sz_b:,.1f}M USD)."
        elif sz_b > sz_a:
            winner = "molecule_b"
            summary = f"{name_b} addresses a significantly larger market opportunity (${sz_b:,.1f}M vs ${sz_a:,.1f}M USD)."
        else:
            winner = "tie"
            summary = "Comparable global commercial market scales."

        return DomainComparisonItem(
            domain_name="Market Intelligence",
            molecule_a_val=val_a,
            molecule_b_val=val_b,
            winner=winner,
            summary=summary
        )

    def _generate_executive_comparison_summary(
        self,
        ctx_a: ResearchContext,
        ctx_b: ResearchContext,
        name_a: str,
        name_b: str,
        clin_comp: DomainComparisonItem,
        pat_comp: DomainComparisonItem,
        mkt_comp: DomainComparisonItem,
        overall_winner: str
    ) -> ExecutiveComparisonSummary:
        diff_items = []
        if clin_comp.winner != "tie":
            diff_items.append(f"Clinical Trial Pipeline: {clin_comp.summary}")
        if pat_comp.winner != "tie":
            diff_items.append(f"Intellectual Property Barrier: {pat_comp.summary}")
        if mkt_comp.winner != "tie":
            diff_items.append(f"Commercial Market Scale: {mkt_comp.summary}")

        if not diff_items:
            diff_items.append("Both molecules exhibit closely aligned multi-domain research profiles.")

        winner_name = name_a if overall_winner == "molecule_a" else (name_b if overall_winner == "molecule_b" else "Neither (Equal Rating)")

        rec = (
            f"Based on 360-degree commercial opportunity scoring, {winner_name} represents the preferred "
            f"innovation candidate due to favorable market scale, patent FTO freedom, and clinical trial evidence."
            if overall_winner != "tie" else
            f"Both {name_a} and {name_b} demonstrate equivalent overall commercial opportunity ratings. "
            f"Further indication-specific clinical subgroup analysis is recommended."
        )

        return ExecutiveComparisonSummary(
            key_differentiators=diff_items,
            clinical_winner_reason=clin_comp.summary,
            patent_winner_reason=pat_comp.summary,
            market_winner_reason=mkt_comp.summary,
            strategic_recommendation=rec
        )
