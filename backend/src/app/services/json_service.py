"""
services/json_service.py

Standardized JSON Export Generator for MoleculeIQ research pipeline results.
"""

import dataclasses
import time
from typing import Dict, Any
from app.domain.research_context import ResearchContext


class JSONReportService:
    """
    Formats ResearchContext into a standardized JSON API payload suitable for downstream integrations.
    """

    def generate(self, context: ResearchContext, query_input: str = "", processing_time_sec: float = 0.0) -> Dict[str, Any]:
        score_data = dataclasses.asdict(context.score) if context.score else {}
        meta = context.metadata

        # Format clinical studies
        trials = [
            {
                "nct_id": t.nct_id,
                "title": t.title,
                "status": t.overall_status,
                "phase": t.phase,
                "conditions": t.conditions,
                "interventions": t.interventions,
                "sponsor": t.sponsor,
                "start_date": t.start_date,
                "completion_date": t.completion_date,
            }
            for t in (context.clinical.trials if context.clinical else [])
        ]

        # Format publications
        pubs = [
            {
                "title": p.title,
                "authors": p.authors,
                "journal": p.journal,
                "publication_year": p.publication_year,
                "pmid": p.pmid,
                "doi": p.doi,
                "citation_count": p.citation_count,
            }
            for p in (context.literature.publications if context.literature else [])
        ]

        # Format patents
        patents = [
            {
                "patent_number": p.patent_number,
                "jurisdiction": p.jurisdiction,
                "assignee": p.assignee,
                "filing_date": p.filing_date,
                "expiry_date": p.expiry_date,
                "status": p.status,
                "patent_type": p.patent_type,
                "fto_status": p.fto_status,
            }
            for p in (context.patent.patents if context.patent else [])
        ]

        # Format market points
        market_points = [
            {
                "year": m.year,
                "region": m.region,
                "therapeutic_area": m.therapeutic_area,
                "market_size_usd_mn": m.market_size_usd_mn,
                "cagr_percent": m.cagr_percent,
                "competitor_count": m.competitor_count,
            }
            for m in (context.market.data_points if context.market else [])
        ]

        return {
            "app_name": "MoleculeIQ Enterprise",
            "version": "2.0.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "query_input": query_input or context.molecule_name,
            "canonical_name": context.molecule_name,
            "has_meaningful_evidence": meta.has_meaningful_evidence,
            "confidence": {
                "score_percent": score_data.get("confidence_score", 0.0),
                "breakdown": score_data.get("confidence_breakdown", {})
            },
            "opportunity_score": {
                "overall_score": score_data.get("overall_score", 0.0),
                "clinical_subscore": score_data.get("clinical_score", 0.0),
                "market_subscore": score_data.get("market_score", 0.0),
                "patent_subscore": score_data.get("patent_score", 0.0),
                "literature_subscore": score_data.get("research_score", 0.0),
                "category_weights": score_data.get("category_weights", {}),
                "explanations": score_data.get("score_breakdown", {}).get("explanation", [])
            },
            "executive_summary": {
                "highlights": [
                    f"Clinical Activity: {meta.active_trials_count} active / {meta.completed_trials_count} completed trials",
                    f"Market Opportunity: ${meta.global_market_size_usd_mn:,.1f}M USD global market size" if meta.global_market_size_usd_mn else "Market Data: N/A",
                    f"Patent Landscape: {meta.fto_summary}"
                ],
                "risks": [
                    "Clinical trial phase failure risk",
                    "Patent expiration & generic market entry",
                    "Competitive market saturation"
                ],
                "recommended_next_steps": [
                    "Initiate targeted indication sub-population trials",
                    "Perform deep-dive freedom-to-operate patent opinion",
                    "Conduct regional payer & reimbursement interviews"
                ]
            },
            "clinical_analysis": {
                "trials_count": len(trials),
                "active_trials": meta.active_trials_count,
                "completed_trials": meta.completed_trials_count,
                "trials": trials
            },
            "literature_analysis": {
                "publications_count": len(pubs),
                "highly_cited_count": meta.highly_cited_papers_count,
                "publications": pubs
            },
            "patent_analysis": {
                "patent_count": len(patents),
                "fto_summary": meta.fto_summary,
                "at_risk_count": meta.at_risk_patents_count,
                "patents": patents
            },
            "market_analysis": {
                "global_market_size_usd_mn": meta.global_market_size_usd_mn,
                "data_points": market_points
            },
            "sources": [
                {"name": "ClinicalTrials.gov API v2", "url": "https://clinicaltrials.gov"},
                {"name": "Europe PMC REST API", "url": "https://europepmc.org"},
                {"name": "USPTO & EPO Patent Registry", "url": "https://patents.google.com"},
                {"name": "IQVIA MIDAS Database", "url": "https://www.iqvia.com"}
            ],
            "processing_metadata": {
                "processing_time_sec": processing_time_sec,
                "agents_executed": ["ClinicalTrialsAgent", "LiteratureAgent", "MarketAgent", "PatentAgent"],
                "domains_available": meta.domains_available,
                "search_queries_generated": [context.molecule_name]
            }
        }
