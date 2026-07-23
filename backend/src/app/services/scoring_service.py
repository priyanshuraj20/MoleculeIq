"""
services/scoring_service.py

Hybrid Opportunity Scoring Engine.

Responsibility:
  1. Accepts a ResearchContext object.
  2. Evaluates deterministic, explainable scoring heuristics across:
     - Market Sub-Score (30% weight)
     - Clinical Sub-Score (25% weight)
     - Patent / FTO Sub-Score (25% weight)
     - Literature / Research Sub-Score (20% weight)
  3. Computes data completeness Confidence Score (0-100).
  4. Generates an overall OpportunityScore with detailed transparent breakdown explanations.
  5. Attaches OpportunityScore to ResearchContext.score.

Zero AI reasoning. Zero LLM calls. 100% reproducible and auditable.
"""

import logging
import time
from typing import Tuple

from app.domain.opportunity_score import OpportunityScore, ScoreBreakdown
from app.domain.research_context import ResearchContext

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Deterministic scoring engine that computes opportunity and confidence scores
    from a ResearchContext entity.
    """

    def calculate(self, context: ResearchContext) -> OpportunityScore:
        """
        Calculates the OpportunityScore and detailed breakdown for a ResearchContext.

        Args:
            context: ResearchContext containing populated domain models and metadata.

        Returns:
            OpportunityScore containing overall score, sub-scores, and explanations.
        """
        logger.info("[ScoringService] Starting opportunity calculation for '%s'", context.molecule_name)
        start_time = time.monotonic()

        meta = context.metadata
        explanations = []

        # 1. Compute Market Sub-Score (30% weight)
        market_score, market_factors, m_expl = self._score_market(context)
        explanations.extend(m_expl)

        # 2. Compute Clinical Sub-Score (25% weight)
        clinical_score, clinical_factors, c_expl = self._score_clinical(context)
        explanations.extend(c_expl)

        # 3. Compute Patent Sub-Score (25% weight)
        patent_score, patent_factors, p_expl = self._score_patent(context)
        explanations.extend(p_expl)

        # 4. Compute Research / Literature Sub-Score (20% weight)
        research_score, lit_factors, l_expl = self._score_literature(context)
        explanations.extend(l_expl)

        # 5. Compute Overall Score
        overall_score = round(
            (0.30 * market_score) +
            (0.25 * clinical_score) +
            (0.25 * patent_score) +
            (0.20 * research_score),
            1
        )
        explanations.append(
            f"Overall Opportunity Score: {overall_score}/100 "
            f"(Weighted: 30% Market [{market_score}], 25% Clinical [{clinical_score}], "
            f"25% Patent [{patent_score}], 20% Literature [{research_score}])"
        )

        # 6. Compute Confidence Score
        confidence_score, confidence_factors, conf_expl = self._score_confidence(context)
        explanations.extend(conf_expl)

        # 7. Construct ScoreBreakdown & OpportunityScore
        breakdown = ScoreBreakdown(
            clinical_factors=clinical_factors,
            market_factors=market_factors,
            patent_factors=patent_factors,
            literature_factors=lit_factors,
            confidence_factors=confidence_factors,
            explanation=explanations
        )

        score_obj = OpportunityScore(
            overall_score=overall_score,
            clinical_score=clinical_score,
            market_score=market_score,
            patent_score=patent_score,
            research_score=research_score,
            confidence_score=confidence_score,
            score_breakdown=breakdown
        )

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[ScoringService] Score calculated for '%s' in %.2fs — Overall: %.1f, Confidence: %.1f",
            context.molecule_name, elapsed, overall_score, confidence_score
        )
        return score_obj

    def evaluate_and_attach(self, context: ResearchContext) -> ResearchContext:
        """
        Calculates OpportunityScore and attaches it to context.score directly.

        Returns:
            Updated ResearchContext with context.score populated.
        """
        context.score = self.calculate(context)
        return context

    # ------------------------------------------------------------------ #
    # Category Sub-Score Heuristics
    # ------------------------------------------------------------------ #

    def _score_market(self, context: ResearchContext) -> Tuple[float, dict, list]:
        """Market sub-score heuristic (0-100 scale)."""
        factors = {}
        expl = []
        meta = context.metadata
        size = meta.global_market_size_usd_mn
        cagr = meta.latest_market_cagr

        # Size points
        if size is None:
            size_pts = 0.0
            expl.append("Market Size: No global sales size data available (0/40 pts)")
        elif size >= 5000:
            size_pts = 40.0
            expl.append(f"Market Size: Large global market (${size:.1f}M >= $5,000M) (+40/40 pts)")
        elif size >= 1000:
            size_pts = 30.0
            expl.append(f"Market Size: Substantial global market (${size:.1f}M >= $1,000M) (+30/40 pts)")
        elif size >= 100:
            size_pts = 20.0
            expl.append(f"Market Size: Moderate market size (${size:.1f}M >= $100M) (+20/40 pts)")
        else:
            size_pts = 10.0
            expl.append(f"Market Size: Niche market size (${size:.1f}M) (+10/40 pts)")

        factors["market_size_points"] = size_pts

        # Growth points (CAGR)
        if cagr is None:
            cagr_pts = 0.0
            expl.append("Market CAGR: No growth rate data available (0/40 pts)")
        elif cagr >= 10.0:
            cagr_pts = 40.0
            expl.append(f"Market CAGR: High commercial growth ({cagr:.1f}% >= 10%) (+40/40 pts)")
        elif cagr >= 5.0:
            cagr_pts = 30.0
            expl.append(f"Market CAGR: Strong growth ({cagr:.1f}% >= 5%) (+30/40 pts)")
        elif cagr >= 0.0:
            cagr_pts = 20.0
            expl.append(f"Market CAGR: Stable growth ({cagr:.1f}%) (+20/40 pts)")
        else:
            cagr_pts = 5.0
            expl.append(f"Market CAGR: Declining market ({cagr:.1f}%) (+5/40 pts)")

        factors["cagr_points"] = cagr_pts

        # Region spread points
        region_count = len(meta.market_regions)
        region_pts = min(20.0, float(region_count * 5))
        factors["region_footprint_points"] = region_pts
        if region_count > 0:
            expl.append(f"Market Regions: Represented in {region_count} region(s) (+{region_pts:.0f}/20 pts)")

        total = min(100.0, round(size_pts + cagr_pts + region_pts, 1))
        return total, factors, expl

    def _score_clinical(self, context: ResearchContext) -> Tuple[float, dict, list]:
        """Clinical sub-score heuristic (0-100 scale)."""
        factors = {}
        expl = []
        meta = context.metadata

        # Active trial momentum (+15 per active trial, max 45)
        active_pts = min(45.0, float(meta.active_trials_count * 15))
        factors["active_trial_points"] = active_pts
        if meta.active_trials_count > 0:
            expl.append(f"Clinical Active: {meta.active_trials_count} active trial(s) (+{active_pts:.0f}/45 pts)")
        else:
            expl.append("Clinical Active: 0 active recruiting trials (0/45 pts)")

        # Completed trial validation (+10 per completed trial, max 40)
        completed_pts = min(40.0, float(meta.completed_trials_count * 10))
        factors["completed_trial_points"] = completed_pts
        if meta.completed_trials_count > 0:
            expl.append(f"Clinical Completed: {meta.completed_trials_count} completed trial(s) (+{completed_pts:.0f}/40 pts)")

        # Late stage phase bonus (+15 for Phase 3/4)
        has_late_phase = False
        if context.clinical and context.clinical.phase_distribution:
            phases = context.clinical.phase_distribution
            has_late_phase = "PHASE3" in phases or "PHASE4" in phases

        phase_pts = 15.0 if has_late_phase else 0.0
        factors["late_phase_bonus"] = phase_pts
        if has_late_phase:
            expl.append("Clinical Phase: Late-stage Phase 3/4 trials present (+15/15 pts)")

        total = min(100.0, round(active_pts + completed_pts + phase_pts, 1))
        return total, factors, expl

    def _score_patent(self, context: ResearchContext) -> Tuple[float, dict, list]:
        """Patent / Freedom-To-Operate sub-score heuristic (0-100 scale)."""
        factors = {}
        expl = []
        meta = context.metadata
        summary = meta.fto_summary

        # Base FTO status score
        if "Free to Operate" in summary:
            base_pts = 70.0
            expl.append("Patent FTO: Free to Operate status confirmed (+70/70 base pts)")
        elif "At Risk" in summary:
            base_pts = 30.0
            expl.append("Patent FTO: At Risk status due to active constraints (+30/70 base pts)")
        elif "Blocked" in summary:
            base_pts = 0.0
            expl.append("Patent FTO: Blocked status (0/70 base pts)")
        else:
            base_pts = 50.0
            expl.append("Patent FTO: Unconfirmed patent landscape (+50/70 base pts)")

        factors["fto_base_points"] = base_pts

        # At-risk constraint penalty (-10 per constraint)
        penalty = float(meta.at_risk_patents_count * 10)
        factors["at_risk_penalty"] = penalty
        if penalty > 0:
            expl.append(f"Patent Penalty: {meta.at_risk_patents_count} active constraint(s) (-{penalty:.0f} pts penalty)")

        # Expired generic entry opportunity bonus (+30)
        expired_count = meta.patent_count - meta.active_patents_count
        generic_pts = 30.0 if expired_count > 0 else 0.0
        factors["generic_entry_bonus"] = generic_pts
        if generic_pts > 0:
            expl.append(f"Patent Opportunity: {expired_count} expired patent(s) open for generic market entry (+30/30 pts)")

        total = max(0.0, min(100.0, round(base_pts - penalty + generic_pts, 1)))
        return total, factors, expl

    def _score_literature(self, context: ResearchContext) -> Tuple[float, dict, list]:
        """Scientific literature sub-score heuristic (0-100 scale)."""
        factors = {}
        expl = []
        meta = context.metadata
        pubs = meta.total_publications
        cites = meta.highly_cited_papers_count

        # Volume points
        if pubs >= 50000:
            vol_pts = 40.0
            expl.append(f"Literature Volume: Extensive academic evidence base ({pubs:,} papers >= 50,000) (+40/40 pts)")
        elif pubs >= 10000:
            vol_pts = 30.0
            expl.append(f"Literature Volume: High volume ({pubs:,} papers >= 10,000) (+30/40 pts)")
        elif pubs >= 1000:
            vol_pts = 20.0
            expl.append(f"Literature Volume: Moderate volume ({pubs:,} papers >= 1,000) (+20/40 pts)")
        elif pubs > 0:
            vol_pts = 10.0
            expl.append(f"Literature Volume: Emerging literature ({pubs} papers) (+10/40 pts)")
        else:
            vol_pts = 0.0
            expl.append("Literature Volume: 0 papers found (0/40 pts)")

        factors["volume_points"] = vol_pts

        # High-impact citation points (+5 per highly cited paper, max 40)
        cite_pts = min(40.0, float(cites * 5))
        factors["citation_impact_points"] = cite_pts
        if cites > 0:
            expl.append(f"Literature Impact: {cites} highly cited paper(s) (+{cite_pts:.0f}/40 pts)")

        # Recency bonus (+20 if recent papers present)
        has_recent = False
        if context.literature and context.literature.recent_papers:
            has_recent = len(context.literature.recent_papers) > 0

        recent_pts = 20.0 if has_recent else 0.0
        factors["recency_bonus"] = recent_pts
        if has_recent:
            expl.append("Literature Recency: Active publication interest since 2020 (+20/20 pts)")

        total = min(100.0, round(vol_pts + cite_pts + recent_pts, 1))
        return total, factors, expl

    def _score_confidence(self, context: ResearchContext) -> Tuple[float, dict, list]:
        """Confidence score heuristic based on data availability & completeness (0-100 scale)."""
        factors = {}
        expl = []
        meta = context.metadata
        available = meta.domains_available

        # Domain availability (+20 per domain, max 80)
        domain_pts = float(len(available) * 20)
        factors["domain_availability_points"] = domain_pts
        expl.append(f"Confidence: {len(available)} of 4 domain(s) available ({', '.join(available) if available else 'none'}) (+{domain_pts:.0f}/80 pts)")

        # Full completeness bonus (+20 if all 4 domains present)
        completeness_pts = 20.0 if len(available) == 4 else 0.0
        factors["full_completeness_bonus"] = completeness_pts
        if completeness_pts > 0:
            expl.append("Confidence: Complete 360-degree research dataset across all 4 domains (+20/20 pts)")
        else:
            missing_count = 4 - len(available)
            expl.append(f"Confidence: Data incomplete — missing {missing_count} domain(s)")

        total = min(100.0, round(domain_pts + completeness_pts, 1))
        return total, factors, expl


# Helper function for functional entrypoint
def calculate_opportunity_score(context: ResearchContext) -> OpportunityScore:
    """
    Standalone function entrypoint for calculating an OpportunityScore.
    """
    service = ScoringService()
    return service.calculate(context)
