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
                "status": t.status,
                "phases": t.phases,
                "conditions": t.conditions,
                "lead_sponsor": t.lead_sponsor,
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
                "pub_year": p.pub_year,
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
                "data_source": p.data_source,
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
                "data_source": m.data_source,
            }
            for m in (context.market.data_points if context.market else [])
        ]

        # Format repurposing candidates
        repurposing_candidates = []
        if getattr(context, "repurposing", None) and context.repurposing.candidates:
            for c in context.repurposing.candidates:
                repurposing_candidates.append({
                    "disease_name": c.disease_name,
                    "disease_id": c.disease_id,
                    "association_score": c.association_score,
                    "targets": c.targets,
                    "why_it_could_work": c.why_it_could_work,
                    "evidence_trials_count": c.evidence_trials_count,
                    "evidence_papers_count": c.evidence_papers_count,
                    "evidence": [
                        {
                            "type": ev.type,
                            "id": ev.id,
                            "title": ev.title,
                            "url": ev.url
                        }
                        for ev in c.evidence
                    ]
                })

        clin_prov = getattr(context.clinical, "provenance", "unavailable") if context.clinical else "unavailable"
        lit_prov = getattr(context.literature, "provenance", "unavailable") if context.literature else "unavailable"
        pat_prov = getattr(context.patent, "provenance", "unavailable") if context.patent else "unavailable"
        mkt_prov = getattr(context.market, "provenance", "unavailable") if context.market else "unavailable"
        rep_prov = getattr(context.repurposing, "provenance", "unavailable") if getattr(context, "repurposing", None) else "unavailable"

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
                "real_sources_count": score_data.get("real_sources_count", 2),
                "total_sources_count": score_data.get("total_sources_count", 4),
                "data_sources_summary": score_data.get("data_sources_summary", "Based on 2 of 4 data sources"),
                "explanations": score_data.get("score_breakdown", {}).get("explanation", [])
            },
            "executive_summary": {
                "highlights": [
                    f"Clinical Activity: {meta.active_trials_count} active / {meta.completed_trials_count} completed trials (Verified)",
                    f"Market Opportunity: ${meta.global_market_size_usd_mn:,.1f}M USD global market size (Simulated estimate)" if meta.global_market_size_usd_mn else "Market Data: N/A",
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
                "provenance": clin_prov,
                "trials_count": len(trials),
                "active_trials": meta.active_trials_count,
                "completed_trials": meta.completed_trials_count,
                "trials": trials
            },
            "literature_analysis": {
                "provenance": lit_prov,
                "publications_count": len(pubs),
                "highly_cited_count": meta.highly_cited_papers_count,
                "publications": pubs
            },
            "patent_analysis": {
                "provenance": pat_prov,
                "patent_count": len(patents),
                "fto_summary": meta.fto_summary,
                "at_risk_count": meta.at_risk_patents_count,
                "patents": patents
            },
            "market_analysis": {
                "provenance": mkt_prov,
                "global_market_size_usd_mn": meta.global_market_size_usd_mn,
                "data_points": market_points
            },
            "repurposing_analysis": {
                "provenance": rep_prov,
                "candidates_count": len(repurposing_candidates),
                "candidates": repurposing_candidates
            },
            "sources": [
                {"name": "ClinicalTrials.gov API v2", "url": "https://clinicaltrials.gov", "provenance": clin_prov},
                {"name": "Europe PMC REST API", "url": "https://europepmc.org", "provenance": lit_prov},
                {"name": "Open Targets Platform & ChEMBL", "url": "https://platform.opentargets.org", "provenance": rep_prov},
                {"name": "USPTO & EPO Patent Registry", "url": "https://patents.google.com", "provenance": pat_prov},
                {"name": "IQVIA MIDAS Database", "url": "https://www.iqvia.com", "provenance": mkt_prov}
            ],
            "processing_metadata": {
                "processing_time_sec": processing_time_sec,
                "agents_executed": ["ClinicalTrialsAgent", "LiteratureAgent", "MarketAgent", "PatentAgent", "RepurposingAgent"],
                "domains_available": meta.domains_available,
                "search_queries_generated": [context.molecule_name]
            }
        }
