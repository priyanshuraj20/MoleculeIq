"""
services/__init__.py

Exposes AggregationService, ScoringService, ExecutiveReportService, PDFReportService, and functional entrypoints.
"""

from app.services.aggregation_service import AggregationService, build_research_context
from app.services.scoring_service import ScoringService, calculate_opportunity_score
from app.services.executive_report_service import ExecutiveReportService, generate_executive_report
from app.services.pdf_service import PDFReportService, generate_pdf_report

__all__ = [
    "AggregationService",
    "build_research_context",
    "ScoringService",
    "calculate_opportunity_score",
    "ExecutiveReportService",
    "generate_executive_report",
    "PDFReportService",
    "generate_pdf_report",
]
