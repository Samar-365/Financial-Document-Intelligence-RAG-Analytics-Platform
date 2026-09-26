"""Unit tests for Executive PDF Report Generator (Developer 3 & 4)."""

import io
from app.services.report_generator import generate_executive_pdf_report


def test_generate_executive_pdf_report_success():
    """Generates an executive briefing PDF with valid metadata and returns valid PDF bytes."""
    company_name = "Reliance Industries Ltd"
    fiscal_period = "FY 2024-25"
    document_filename = "RIL_Annual_Report_2025.pdf"
    health_score = 84.5
    dimension_scores = {
        "Growth": 85.0,
        "Profitability": 88.0,
        "Liquidity": 78.0,
        "Leverage": 82.0,
        "Cash Flow": 89.5,
    }
    metrics = [
        {"metric_name": "Revenue", "value": 11450.0, "unit": "INR Cr", "page_number": 42},
        {"metric_name": "Operating Profit", "value": 2450.0, "unit": "INR Cr", "page_number": 43},
        {"metric_name": "Net Income", "value": 1820.0, "unit": "INR Cr", "page_number": 44},
    ]
    ratios = {
        "Operating Margin": "21.4%",
        "Net Profit Margin": "15.9%",
        "Return on Equity": "18.2%",
        "Current Ratio": "1.85",
        "Debt to Equity": "0.62",
    }
    risks = [
        "Foreign exchange currency fluctuation risk across global operations.",
        "Regulatory revisions in commodity tariffs.",
    ]

    pdf_bytes = generate_executive_pdf_report(
        company_name=company_name,
        fiscal_period=fiscal_period,
        document_filename=document_filename,
        health_score=health_score,
        dimension_scores=dimension_scores,
        metrics=metrics,
        ratios=ratios,
        risks=risks,
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF files start with %PDF
    assert pdf_bytes.startswith(b"%PDF")
