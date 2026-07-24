"""
services/executive_report_service.py

AI Executive Analysis Service.

Responsibility:
  Consumes normalized ResearchContext and synthesizes an executive-level C-suite
  pharmaceutical business intelligence report using LLM (Gemini) with a deterministic
  evidence-based fallback engine.

Rule:
  Consumes ONLY normalized ResearchContext objects — NEVER raw APIs or raw DB rows.
  Never crashes if the LLM API is unavailable or missing an API key.
"""

import dataclasses
import json
import logging
import time
from typing import Optional, Dict

import httpx

from app.core.config import settings
from app.domain.executive_report import ExecutiveReport
from app.domain.research_context import ResearchContext

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are MoleculeIQ's Chief Scientific & Commercial Strategy Officer.
Your mandate is to evaluate the supplied normalized ResearchContext JSON for a pharmaceutical molecule and synthesize an executive-level strategic report for C-suite decision-makers.

STRICT EXECUTIVE REPORTING RULES:
1. Maintain an authoritative, professional, evidence-based C-suite tone.
2. Rely EXCLUSIVELY on data provided in the supplied ResearchContext JSON. Do NOT hallucinate or fabricate clinical trial counts, market figures, patent numbers, or citation metrics.
3. If a domain dataset is missing or empty, explicitly state the uncertainty and lack of available evidence.
4. Output your analysis STRICTLY as a JSON object containing the exact 8 keys below:
   - "summary": Executive Summary & overall strategic thesis.
   - "commercial_opportunity": Commercial opportunity evaluation & growth drivers.
   - "clinical_analysis": Clinical trial landscape, development phases, & safety/efficacy signal.
   - "market_analysis": Market size, CAGR growth, regional presence, & competitive intensity.
   - "patent_analysis": Patent landscape, expiration timelines, & Freedom-To-Operate (FTO) risk.
   - "scientific_analysis": Academic publication volume, citation impact, & research momentum.
   - "risks": Key clinical, regulatory, legal, or commercial risks.
   - "recommendation": Final strategic investment & development recommendation.
"""


class ExecutiveReportService:
    """
    Synthesizes C-suite strategic business intelligence reports from ResearchContext.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = settings.GEMINI_MODEL

    async def generate_report(self, context: ResearchContext) -> ExecutiveReport:
        """
        Generates an ExecutiveReport from ResearchContext.

        Args:
            context: Populated ResearchContext containing domain data and scores.

        Returns:
            ExecutiveReport containing all 8 populated report sections.
        """
        molecule_name = context.molecule_name
        logger.info("[ExecutiveReportService] Report generation requested for '%s'", molecule_name)
        start_time = time.monotonic()

        if not context.has_meaningful_evidence:
            logger.warning("[ExecutiveReportService] Skipping report generation for '%s': No meaningful evidence found.", molecule_name)
            raise ValueError(f"No research data or evidence found for molecule '{molecule_name}'. Executive report cannot be generated.")

        # 1. Attempt LLM generation if API key is provided
        if self._api_key:
            try:
                llm_report = await self._generate_with_gemini(context)
                if llm_report:
                    elapsed = round(time.monotonic() - start_time, 2)
                    logger.info("[ExecutiveReportService] Gemini report generated in %.2fs", elapsed)
                    return llm_report
            except Exception as exc:
                logger.warning(
                    "[ExecutiveReportService] Gemini API call failed for '%s': %s — falling back to deterministic synthesizer",
                    molecule_name, str(exc)
                )

        # 2. Fallback to deterministic executive synthesizer if LLM unavailable
        fallback_report = self._generate_rule_based_report(context)
        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[ExecutiveReportService] Deterministic executive report synthesized in %.2fs (Model: '%s')",
            elapsed, fallback_report.model_name
        )
        return fallback_report

    # ------------------------------------------------------------------ #
    # Gemini LLM Integration
    # ------------------------------------------------------------------ #

    async def _generate_with_gemini(self, context: ResearchContext) -> Optional[ExecutiveReport]:
        """
        Invokes Google Gemini REST API with structured ResearchContext JSON payload.
        """
        context_json = json.dumps(dataclasses.asdict(context), indent=2, default=str)
        user_prompt = f"Target Molecule: '{context.molecule_name}'\n\nResearchContext Data:\n{context_json}"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": SYSTEM_PROMPT},
                        {"text": user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,  # Low temperature for strict adherence to facts
                "responseMimeType": "application/json",
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                result_data = response.json()
                candidates = result_data.get("candidates", [])
                if candidates:
                    text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    parsed = json.loads(text_out)
                    return ExecutiveReport(
                        summary=parsed.get("summary", ""),
                        commercial_opportunity=parsed.get("commercial_opportunity", ""),
                        clinical_analysis=parsed.get("clinical_analysis", ""),
                        market_analysis=parsed.get("market_analysis", ""),
                        patent_analysis=parsed.get("patent_analysis", ""),
                        scientific_analysis=parsed.get("scientific_analysis", ""),
                        risks=parsed.get("risks", ""),
                        recommendation=parsed.get("recommendation", ""),
                        model_name=f"Google Gemini ({self._model})"
                    )

        return None

    # ------------------------------------------------------------------ #
    # Deterministic Rule-Based Fallback Synthesizer
    # ------------------------------------------------------------------ #

    def _generate_rule_based_report(self, context: ResearchContext) -> ExecutiveReport:
        """
        Synthesizes a structured, highly analytical C-suite ExecutiveReport
        directly from ResearchContext metadata and scores when LLM API is unavailable.
        Guarantees 100% availability without hallucination.
        """
        m_name = context.molecule_name
        meta = context.metadata
        score = context.score

        ov_score = score.overall_score if score else "N/A"
        conf_score = score.confidence_score if score else "N/A"

        # 1. Executive Summary
        summary = (
            f"Strategic Intelligence Summary for {m_name}:\n"
            f"{m_name} presents an overall Opportunity Score of {ov_score}/100 with a Data Confidence Score of {conf_score}/100. "
            f"Analysis across available domains indicates {meta.total_trials} total clinical trial(s), "
            f"{meta.total_publications:,} scientific publication(s), and an FTO assessment of '{meta.fto_summary}'. "
            f"Target molecule research was conducted across {len(meta.domains_available)} available domain dataset(s) ({', '.join(meta.domains_available) if meta.domains_available else 'none'})."
        )

        # 2. Commercial Opportunity
        if meta.global_market_size_usd_mn:
            comm = (
                f"Commercial Evaluation:\n"
                f"Global market size is estimated at ${meta.global_market_size_usd_mn:,.1f} Million USD "
                f"with an annual CAGR growth rate of {meta.latest_market_cagr or 0.0}%. "
                f"Market presence spans {len(meta.market_regions)} key geographic region(s) ({', '.join(meta.market_regions)}). "
                f"Market Opportunity Sub-Score: {score.market_score if score else 'N/A'}/100."
            )
        else:
            comm = f"Commercial Evaluation:\nNo regional sales or market size data available for {m_name}. Commercial feasibility is unconfirmed."

        # 3. Clinical Landscape
        if meta.total_trials > 0:
            clin = (
                f"Clinical Trial Landscape:\n"
                f"Identified {meta.total_trials} total clinical trial record(s) on ClinicalTrials.gov. "
                f"Currently {meta.active_trials_count} trial(s) are actively recruiting or in progress, while {meta.completed_trials_count} trial(s) have reached completion. "
                f"Clinical Development Sub-Score: {score.clinical_score if score else 'N/A'}/100."
            )
        else:
            clin = f"Clinical Trial Landscape:\nNo registered clinical trials found for {m_name} on ClinicalTrials.gov. Clinical validation remains unconfirmed."

        # 4. Market Analysis
        if meta.market_regions:
            mkt = (
                f"Market Insights & Competitive Intensity:\n"
                f"Commercial sales records identified in {len(meta.market_regions)} key market region(s). "
                f"Primary market valuation stands at ${meta.global_market_size_usd_mn or 0.0:,.1f}M USD. "
                f"Overall Market Feasibility Sub-Score: {score.market_score if score else 'N/A'}/100."
            )
        else:
            mkt = f"Market Insights:\nMarket intelligence data unavailable for {m_name}. Further primary research is required to evaluate commercial volume."

        # 5. Patent Landscape & FTO
        if meta.patent_count > 0:
            pat = (
                f"Patent Landscape & Freedom-To-Operate (FTO):\n"
                f"Freedom-To-Operate Assessment: '{meta.fto_summary}'. "
                f"Identified {meta.patent_count} patent filing(s), including {meta.active_patents_count} active patent(s) in force "
                f"and {meta.at_risk_patents_count} active constraint(s). "
                f"Patent Landscape Sub-Score: {score.patent_score if score else 'N/A'}/100."
            )
        else:
            pat = f"Patent Landscape:\nNo patent filings registered in database for {m_name}. FTO status is unconfirmed."

        # 6. Scientific Momentum
        if meta.total_publications > 0:
            sci = (
                f"Scientific Momentum & Academic Evidence:\n"
                f"Identified {meta.total_publications:,} publication(s) in PubMed / Europe PMC repository. "
                f"Includes {meta.highly_cited_papers_count} high-impact highly cited paper(s) (>=10 citations). "
                f"Scientific Research Sub-Score: {score.research_score if score else 'N/A'}/100."
            )
        else:
            sci = f"Scientific Momentum:\nNo peer-reviewed scientific publications found for {m_name} in Europe PMC."

        # 7. Strategic Risks
        risks_list = []
        if meta.at_risk_patents_count > 0:
            risks_list.append(f"• Intellectual Property Risk: {meta.at_risk_patents_count} active patent constraint(s) may present FTO blocking risks.")
        if meta.active_trials_count == 0:
            risks_list.append("• Clinical Pipeline Risk: Zero active recruiting clinical trials detected.")
        if not meta.global_market_size_usd_mn:
            risks_list.append("• Market Risk: Unconfirmed global sales volume in primary database.")

        if not risks_list:
            risks_list.append("• Favorable risk profile — no major blocking constraints identified in available datasets.")

        risks = "Strategic Risk Factors:\n" + "\n".join(risks_list)

        # 8. Investment Recommendation
        if score and score.overall_score >= 70.0:
            recom = f"Investment Recommendation: HIGH OPPORTUNITY (Score: {ov_score}/100). Proceed with advanced commercial planning and licensing formulation."
        elif score and score.overall_score >= 40.0:
            recom = f"Investment Recommendation: MODERATE OPPORTUNITY (Score: {ov_score}/100). Conduct detailed FTO legal review and market entry positioning."
        else:
            recom = f"Investment Recommendation: HIGH UNCERTAINTY / LOW PRIORITY (Score: {ov_score}/100). Data coverage is limited; require further data validation before capital allocation."

        return ExecutiveReport(
            summary=summary,
            commercial_opportunity=comm,
            clinical_analysis=clin,
            market_analysis=mkt,
            patent_analysis=pat,
            scientific_analysis=sci,
            risks=risks,
            recommendation=recom,
            model_name="MoleculeIQ C-Suite Executive Synthesizer (Fallback)"
        )


# Helper function for functional entrypoint
async def generate_executive_report(context: ResearchContext) -> ExecutiveReport:
    """
    Standalone async function entrypoint for generating an ExecutiveReport.
    """
    service = ExecutiveReportService()
    return await service.generate_report(context)
