"""One-Click Executive PDF Briefing Exporter.

Generates a formatted C-suite financial intelligence briefing report
using ReportLab, including KPI scorecards, ratios, health scores, and risk disclosures.
"""

import io
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether,
        HRFlowable,
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_executive_pdf_report(
    company_name: str,
    fiscal_period: str,
    document_filename: str,
    health_score: float,
    dimension_scores: Dict[str, float],
    metrics: List[Dict[str, Any]],
    ratios: Dict[str, Any],
    risks: List[str],
) -> bytes:
    """Generates an executive briefing PDF and returns raw bytes for download."""
    if not HAS_REPORTLAB:
        # Fallback text output if ReportLab is unavailable
        content = f"FINANCIAL INTELLIGENCE BRIEFING: {company_name} ({fiscal_period})\n"
        content += f"Health Score: {health_score}/100\nDocument: {document_filename}\n"
        return content.encode("utf-8")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0d47a1"),
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1565c0"),
        spaceBefore=10,
        spaceAfter=5,
    )
    normal_style = styles["Normal"]

    story = []

    # 1. Header Banner
    story.append(Paragraph("Executive Financial Intelligence Briefing", title_style))
    story.append(Paragraph(f"<b>Company:</b> {company_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Filing Period:</b> {fiscal_period} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph(f"<font size=8 color='#666666'>Source: {document_filename}</font>", normal_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d47a1"), spaceAfter=15))

    # 2. Corporate Health Scorecard
    story.append(Paragraph("1. Corporate Health Scorecard (5-Dimension Model)", section_style))
    health_table_data = [
        ["Overall Health Score", f"{health_score:.1f} / 100", "Composite Rating: Investment Grade"],
        ["Growth Dimension (20%)", f"{dimension_scores.get('growth_score', 0):.1f} / 100", "Top-line revenue trajectory"],
        ["Profitability Dimension (25%)", f"{dimension_scores.get('profitability_score', 0):.1f} / 100", "Operating & net margin strength"],
        ["Liquidity Dimension (20%)", f"{dimension_scores.get('liquidity_score', 0):.1f} / 100", "Short-term solvency coverage"],
        ["Leverage Dimension (20%)", f"{dimension_scores.get('leverage_score', 0):.1f} / 100", "Debt-to-equity resilience"],
        ["Cash Flow Dimension (15%)", f"{dimension_scores.get('cash_flow_score', 0):.1f} / 100", "Operating cash conversion quality"],
    ]
    t_health = Table(health_table_data, colWidths=[200, 100, 230])
    t_health.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e3f2fd")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_health)
    story.append(Spacer(1, 15))

    # 3. Key Financial Ratios Table
    story.append(Paragraph("2. Financial Ratios Analysis", section_style))
    ratio_rows = [
        ["Ratio", "Calculated Value", "Standard Benchmark"],
        ["Operating Profit Margin (OPM)", f"{ratios.get('opm', 0):.2f}%", "> 15.0% (Healthy)"],
        ["Net Profit Margin (NPM)", f"{ratios.get('npm', 0):.2f}%", "> 10.0% (Strong)"],
        ["Return on Equity (ROE)", f"{ratios.get('roe', 0):.2f}%", "> 15.0% (Efficient)"],
        ["Current Ratio", f"{ratios.get('current_ratio', 0):.2f}x", "> 1.50x (Adequate)"],
        ["Debt to Equity", f"{ratios.get('debt_to_equity', 0):.2f}x", "< 1.00x (Conservative)"],
        ["Interest Coverage Ratio", f"{ratios.get('interest_coverage', 0):.2f}x", "> 3.00x (Low Risk)"],
    ]
    t_ratios = Table(ratio_rows, colWidths=[200, 140, 190])
    t_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ratios)
    story.append(Spacer(1, 15))

    # 4. Top Qualitative Risk Disclosures
    story.append(Paragraph("3. Qualitative Risk Highlights (Item 1A / Notes)", section_style))
    risk_data = [["#", "Identified Risk Disclosure Factor"]]
    for idx, risk in enumerate(risks[:5], start=1):
        if isinstance(risk, dict):
            desc = str(risk.get("description") or risk.get("category") or str(risk))
        else:
            desc = str(risk)
        risk_data.append([str(idx), desc])
    if len(risk_data) == 1:
        risk_data.append(["1", "No critical qualitative risk flags identified."])

    t_risks = Table(risk_data, colWidths=[30, 500])
    t_risks.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#fff3e0")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_risks)

    doc.build(story)
    return buffer.getvalue()
