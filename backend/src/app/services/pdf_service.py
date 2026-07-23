"""
services/pdf_service.py

Professional PDF Report Generation Service for MoleculeIQ.

Responsibility:
  Consumes ResearchContext and ExecutiveReport entities and generates a publication-grade,
  multi-page C-suite PDF report using ReportLab.

Key Features:
  - Deterministic PDF byte generation (BytesIO in-memory stream).
  - Custom NumberedCanvas for dynamic running headers & "Page X of Y" footers.
  - Sleek corporate palette (Navy #1E293B, Indigo #4F46E5, Teal #0EA5E9, Slate #64748B).
  - Explicit tables for Opportunity Scores, Clinical Trials, Market Sales, Patents, and Literature.
  - Automatic page breaking, consistent 0.5" margins, and zero temporary disk file dependency.
"""

import io
import logging
import time
from typing import Optional, List

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

from app.domain.executive_report import ExecutiveReport
from app.domain.research_context import ResearchContext

logger = logging.getLogger(__name__)

# Corporate Color Palette
PRIMARY_NAVY = HexColor("#1E293B")   # Deep Slate Navy
ACCENT_INDIGO = HexColor("#4F46E5")  # Vibrant Indigo
ACCENT_TEAL   = HexColor("#0EA5E9")  # Bright Teal
TEXT_DARK     = HexColor("#0F172A")  # Dark Charcoal Body Text
TEXT_MUTED    = HexColor("#64748B")  # Slate Subtitle Text
BG_LIGHT      = HexColor("#F8FAFC")  # Light Off-White Table Background
BORDER_COLOR  = HexColor("#E2E8F0")  # Subtle Border Gray
SUCCESS_GREEN = HexColor("#10B981")  # Score Success Green
WARNING_AMBER = HexColor("#F59E0B")  # Score Warning Amber


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas renderer for dynamic "Page X of Y" footers and running headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(TEXT_MUTED)

        # Running Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 756, "MOLECULEIQ  |  EXECUTIVE STRATEGIC INTELLIGENCE REPORT")
            self.setFont("Helvetica", 8)
            self.drawRightString(576, 756, "CONFIDENTIAL")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.75)
            self.line(36, 748, 576, 748)

        # Running Footer (all pages)
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.75)
        self.line(36, 45, 576, 45)

        self.setFont("Helvetica", 8)
        self.drawString(36, 30, "CONFIDENTIAL — FOR INTERNAL EXECUTIVE DECISION-MAKING ONLY")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


class PDFReportService:
    """
    Generates publication-ready PDF reports from ResearchContext & ExecutiveReport.
    """

    def generate_pdf(self, context: ResearchContext, report: ExecutiveReport) -> bytes:
        """
        Generates PDF document bytes for a given ResearchContext and ExecutiveReport.

        Args:
            context: Populated ResearchContext domain object.
            report: Populated ExecutiveReport domain object.

        Returns:
            Raw PDF bytes suitable for HTTP download.
        """
        molecule_name = context.molecule_name
        logger.info("[PDFReportService] Starting PDF generation for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        buffer = io.BytesIO()

        # Document setup: Letter size, 0.5" (36pt) margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=54,
            bottomMargin=54,
        )

        styles = self._setup_styles()
        story = []

        # 1. Cover / Hero Banner
        story.extend(self._build_hero_banner(context, report, styles))
        story.append(Spacer(1, 15))

        # 2. Executive Summary
        story.extend(self._build_section("1. EXECUTIVE SUMMARY", report.summary, styles))
        story.append(Spacer(1, 15))

        # 3. Commercial Opportunity & Scores
        story.extend(self._build_commercial_section(context, report, styles))
        story.append(Spacer(1, 15))

        # 4. Clinical Landscape
        story.extend(self._build_clinical_section(context, report, styles))
        story.append(Spacer(1, 15))

        # 5. Market Analysis
        story.extend(self._build_market_section(context, report, styles))
        story.append(Spacer(1, 15))

        # 6. Patent Landscape & FTO
        story.extend(self._build_patent_section(context, report, styles))
        story.append(Spacer(1, 15))

        # 7. Scientific Momentum
        story.extend(self._build_literature_section(context, report, styles))
        story.append(Spacer(1, 15))

        # 8. Strategic Risks
        story.extend(self._build_section("7. STRATEGIC RISK FACTORS", report.risks, styles))
        story.append(Spacer(1, 15))

        # 9. Investment Recommendation (Callout Box)
        story.extend(self._build_recommendation_box(report.recommendation, styles))
        story.append(Spacer(1, 20))

        # 10. Appendix & System Metadata
        story.extend(self._build_appendix(context, report, styles))

        # Build PDF using NumberedCanvas for dynamic page numbering
        doc.build(story, canvasmaker=NumberedCanvas)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        elapsed = round(time.monotonic() - start_time, 2)
        logger.info(
            "[PDFReportService] PDF generated successfully for '%s' in %.2fs (Size: %d bytes)",
            molecule_name, elapsed, len(pdf_bytes)
        )
        return pdf_bytes

    # ------------------------------------------------------------------ #
    # Styles & Layout Setup
    # ------------------------------------------------------------------ #

    def _setup_styles(self):
        styles = getSampleStyleSheet()

        # Custom Paragraph Styles
        styles.add(ParagraphStyle(
            name="ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=HexColor("#FFFFFF"),
        ))
        styles.add(ParagraphStyle(
            name="ReportSubtitle",
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=HexColor("#CBD5E1"),
        ))
        styles.add(ParagraphStyle(
            name="SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=PRIMARY_NAVY,
            spaceBefore=10,
            spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="BodyDark",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=TEXT_DARK,
            spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=HexColor("#FFFFFF"),
            alignment=0,
        ))
        styles.add(ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_DARK,
        ))
        styles.add(ParagraphStyle(
            name="TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_DARK,
        ))
        styles.add(ParagraphStyle(
            name="RecommendationText",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=15,
            textColor=PRIMARY_NAVY,
        ))

        return styles

    # ------------------------------------------------------------------ #
    # Document Flow Elements
    # ------------------------------------------------------------------ #

    def _build_hero_banner(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders the top dark hero banner with title, molecule name, date, and overall score."""
        ov_score = f"{context.score.overall_score:.1f}" if context.score else "N/A"
        conf_score = f"{context.score.confidence_score:.0f}%" if context.score else "N/A"

        banner_data = [
            [
                Paragraph(f"MOLECULEIQ RESEARCH REPORT<br/><b>{context.molecule_name.upper()}</b>", styles["ReportTitle"]),
                Paragraph(f"<b>Overall Score: {ov_score}/100</b><br/>Confidence: {conf_score}<br/>Date: {context.created_at[:10]}", styles["ReportSubtitle"])
            ]
        ]

        banner_table = Table(banner_data, colWidths=[340, 200])
        banner_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_NAVY),
            ("PADDING", (0, 0), (-1, -1), 16),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ]))
        return [banner_table]

    def _build_section(self, title: str, content: str, styles) -> List:
        """Renders a standard section header, divider line, and text content."""
        elements = [
            Paragraph(title, styles["SectionHeader"]),
            HRFlowable(width="100%", thickness=1.5, color=ACCENT_INDIGO, spaceBefore=2, spaceAfter=6),
        ]
        for paragraph in content.split("\n"):
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), styles["BodyDark"]))
        return elements

    def _build_commercial_section(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Commercial Opportunity text + Opportunity Scores Table."""
        elements = self._build_section("2. COMMERCIAL OPPORTUNITY & SCORES", report.commercial_opportunity, styles)

        if context.score:
            s = context.score
            table_data = [
                [
                    Paragraph("Scoring Category", styles["TableHeader"]),
                    Paragraph("Score (0-100)", styles["TableHeader"]),
                    Paragraph("Weight", styles["TableHeader"]),
                    Paragraph("Strategic Assessment", styles["TableHeader"])
                ],
                [Paragraph("Market Feasibility", styles["TableCellBold"]), Paragraph(f"{s.market_score:.1f}", styles["TableCell"]), Paragraph("30%", styles["TableCell"]), Paragraph("Global volume & CAGR growth", styles["TableCell"])],
                [Paragraph("Clinical Momentum", styles["TableCellBold"]), Paragraph(f"{s.clinical_score:.1f}", styles["TableCell"]), Paragraph("25%", styles["TableCell"]), Paragraph("Active & completed trial validation", styles["TableCell"])],
                [Paragraph("Patent Landscape / FTO", styles["TableCellBold"]), Paragraph(f"{s.patent_score:.1f}", styles["TableCell"]), Paragraph("25%", styles["TableCell"]), Paragraph("FTO status & patent constraint risk", styles["TableCell"])],
                [Paragraph("Scientific Research", styles["TableCellBold"]), Paragraph(f"{s.research_score:.1f}", styles["TableCell"]), Paragraph("20%", styles["TableCell"]), Paragraph("Publication volume & citation impact", styles["TableCell"])],
                [Paragraph("OVERALL OPPORTUNITY SCORE", styles["TableCellBold"]), Paragraph(f"<b>{s.overall_score:.1f}</b>", styles["TableCellBold"]), Paragraph("<b>100%</b>", styles["TableCellBold"]), Paragraph("<b>Composite weighted opportunity score</b>", styles["TableCellBold"])],
                [Paragraph("DATA CONFIDENCE SIGNAL", styles["TableCellBold"]), Paragraph(f"<b>{s.confidence_score:.1f}</b>", styles["TableCellBold"]), Paragraph("Signal", styles["TableCellBold"]), Paragraph("Data completeness across 4 domains", styles["TableCellBold"])],
            ]

            t = Table(table_data, colWidths=[150, 80, 65, 245])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
                ("BACKGROUND", (0, 1), (-1, 1), BG_LIGHT),
                ("BACKGROUND", (0, 3), (-1, 3), BG_LIGHT),
                ("BACKGROUND", (0, 5), (-1, 5), HexColor("#EEF2FF")),  # Highlight overall score row
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        return elements

    def _build_clinical_section(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Clinical Landscape text + Clinical Trials Table."""
        elements = self._build_section("3. CLINICAL DEVELOPMENT LANDSCAPE", report.clinical_analysis, styles)

        if context.clinical and context.clinical.trials:
            table_data = [
                [
                    Paragraph("NCT ID", styles["TableHeader"]),
                    Paragraph("Study Title", styles["TableHeader"]),
                    Paragraph("Status", styles["TableHeader"]),
                    Paragraph("Phases", styles["TableHeader"]),
                    Paragraph("Lead Sponsor", styles["TableHeader"])
                ]
            ]
            for trial in context.clinical.trials[:8]:  # Limit top 8 for clean page fit
                table_data.append([
                    Paragraph(trial.nct_id, styles["TableCellBold"]),
                    Paragraph(trial.title[:60] + "..." if len(trial.title) > 60 else trial.title, styles["TableCell"]),
                    Paragraph(trial.status, styles["TableCell"]),
                    Paragraph(", ".join(trial.phases) if trial.phases else "NA", styles["TableCell"]),
                    Paragraph(trial.lead_sponsor or "Unspecified", styles["TableCell"]),
                ])

            t = Table(table_data, colWidths=[75, 225, 80, 60, 100])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        return elements

    def _build_market_section(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Market Analysis text + Market Sales Table."""
        elements = self._build_section("4. MARKET ANALYSIS & SALES INTELLIGENCE", report.market_analysis, styles)

        if context.market and context.market.data_points:
            table_data = [
                [
                    Paragraph("Region", styles["TableHeader"]),
                    Paragraph("Therapeutic Area", styles["TableHeader"]),
                    Paragraph("Year", styles["TableHeader"]),
                    Paragraph("Market Size ($M)", styles["TableHeader"]),
                    Paragraph("CAGR %", styles["TableHeader"]),
                    Paragraph("Competitors", styles["TableHeader"])
                ]
            ]
            for dp in context.market.data_points:
                table_data.append([
                    Paragraph(dp.region, styles["TableCellBold"]),
                    Paragraph(dp.therapeutic_area, styles["TableCell"]),
                    Paragraph(str(dp.year), styles["TableCell"]),
                    Paragraph(f"${dp.market_size_usd_mn:,.1f}M", styles["TableCellBold"]),
                    Paragraph(f"{dp.cagr_percent}%" if dp.cagr_percent is not None else "N/A", styles["TableCell"]),
                    Paragraph(str(dp.competitor_count), styles["TableCell"]),
                ])

            t = Table(table_data, colWidths=[90, 160, 45, 95, 75, 75])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        return elements

    def _build_patent_section(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Patent Landscape text + Patent Filings Table."""
        elements = self._build_section("5. PATENT LANDSCAPE & FREEDOM-TO-OPERATE", report.patent_analysis, styles)

        if context.patent and context.patent.patents:
            table_data = [
                [
                    Paragraph("Patent No.", styles["TableHeader"]),
                    Paragraph("Jurisdiction", styles["TableHeader"]),
                    Paragraph("Status", styles["TableHeader"]),
                    Paragraph("Expiry Date", styles["TableHeader"]),
                    Paragraph("Assignee", styles["TableHeader"]),
                    Paragraph("FTO Status", styles["TableHeader"])
                ]
            ]
            for pat in context.patent.patents[:8]:
                table_data.append([
                    Paragraph(pat.patent_number or "Pending", styles["TableCellBold"]),
                    Paragraph(pat.jurisdiction, styles["TableCell"]),
                    Paragraph(pat.status, styles["TableCell"]),
                    Paragraph(str(pat.expiry_date) if pat.expiry_date else "N/A", styles["TableCell"]),
                    Paragraph(pat.assignee or "Unspecified", styles["TableCell"]),
                    Paragraph(pat.fto_status, styles["TableCellBold"]),
                ])

            t = Table(table_data, colWidths=[100, 65, 60, 75, 140, 100])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        return elements

    def _build_literature_section(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Scientific Momentum text + Literature Publications Table."""
        elements = self._build_section("6. SCIENTIFIC MOMENTUM & PUBLICATIONS", report.scientific_analysis, styles)

        if context.literature and context.literature.publications:
            table_data = [
                [
                    Paragraph("Publication Title", styles["TableHeader"]),
                    Paragraph("Journal", styles["TableHeader"]),
                    Paragraph("Year", styles["TableHeader"]),
                    Paragraph("Citations", styles["TableHeader"])
                ]
            ]
            for pub in context.literature.publications[:6]:
                table_data.append([
                    Paragraph(pub.title[:65] + "..." if len(pub.title) > 65 else pub.title, styles["TableCellBold"]),
                    Paragraph(pub.journal[:35] + "..." if len(pub.journal) > 35 else pub.journal, styles["TableCell"]),
                    Paragraph(str(pub.pub_year) if pub.pub_year else "N/A", styles["TableCell"]),
                    Paragraph(f"{pub.citation_count:,}", styles["TableCellBold"]),
                ])

            t = Table(table_data, colWidths=[240, 170, 50, 80])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        return elements

    def _build_recommendation_box(self, recommendation_text: str, styles) -> List:
        """Renders an executive callout box for the final Investment Recommendation."""
        rec_data = [
            [Paragraph(f"<b>8. STRATEGIC INVESTMENT RECOMMENDATION</b><br/><br/>{recommendation_text}", styles["RecommendationText"])]
        ]
        rec_table = Table(rec_data, colWidths=[540])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F0FDF4")),  # Subtle Light Green Callout
            ("BORDER", (0, 0), (-1, -1), 1.5, SUCCESS_GREEN),
            ("PADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return [KeepTogether([rec_table])]

    def _build_appendix(self, context: ResearchContext, report: ExecutiveReport, styles) -> List:
        """Renders Section 9: Appendix & Metadata Table."""
        elements = [
            Paragraph("9. APPENDIX & SYSTEM METADATA", styles["SectionHeader"]),
            HRFlowable(width="100%", thickness=1.5, color=ACCENT_INDIGO, spaceBefore=2, spaceAfter=6),
        ]

        meta = context.metadata
        table_data = [
            [Paragraph("Metadata Metric", styles["TableHeader"]), Paragraph("Pipeline Value", styles["TableHeader"])],
            [Paragraph("Target Molecule Name", styles["TableCellBold"]), Paragraph(context.molecule_name, styles["TableCell"])],
            [Paragraph("Pipeline Version", styles["TableCellBold"]), Paragraph(context.pipeline_version, styles["TableCell"])],
            [Paragraph("Timestamp (UTC)", styles["TableCellBold"]), Paragraph(context.created_at, styles["TableCell"])],
            [Paragraph("Report Provenance / Model", styles["TableCellBold"]), Paragraph(report.model_name, styles["TableCell"])],
            [Paragraph("Available Research Domains", styles["TableCellBold"]), Paragraph(", ".join(meta.domains_available) if meta.domains_available else "None", styles["TableCell"])],
            [Paragraph("Total Clinical Trials Evaluated", styles["TableCellBold"]), Paragraph(str(meta.total_trials), styles["TableCell"])],
            [Paragraph("Total Publications Scanned", styles["TableCellBold"]), Paragraph(f"{meta.total_publications:,}", styles["TableCell"])],
            [Paragraph("Geographic Sales Regions", styles["TableCellBold"]), Paragraph(", ".join(meta.market_regions) if meta.market_regions else "None", styles["TableCell"])],
            [Paragraph("FTO Assessment Status", styles["TableCellBold"]), Paragraph(meta.fto_summary, styles["TableCell"])],
        ]

        t = Table(table_data, colWidths=[200, 340])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t)
        return elements


# Helper function for functional entrypoint
def generate_pdf_report(context: ResearchContext, report: ExecutiveReport) -> bytes:
    """
    Standalone function entrypoint for generating a PDF report byte stream.
    """
    service = PDFReportService()
    return service.generate_pdf(context, report)
