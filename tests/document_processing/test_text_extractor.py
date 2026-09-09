import pytest
from reportlab.pdfgen import canvas
from app.document_processing.text_extractor import (
    TextExtractor,
    ScannedPDFError,
    ExtractedPageTextDTO,
)


@pytest.fixture
def sample_digital_pdf(tmp_path) -> str:
    """Fixture to generate a multi-page valid digital PDF with readable financial text."""
    pdf_path = str(tmp_path / "annual_report.pdf")
    c = canvas.Canvas(pdf_path)

    # Page 1: Financial Highlights
    c.drawString(100, 750, "Annual Report Fiscal Year 2024 - Financial Highlights")
    c.drawString(100, 730, "Total Consolidated Revenue grew by 15.4% year-over-year.")
    c.showPage()

    # Page 2: Management Discussion
    c.drawString(100, 750, "Item 7: Management Discussion and Operating Review")
    c.drawString(100, 730, "Gross profit margins expanded to 42.1% driven by cloud services.")
    c.showPage()

    c.save()
    return pdf_path


@pytest.fixture
def blank_scanned_pdf(tmp_path) -> str:
    """Fixture to generate a PDF with blank pages representing a scanned document without OCR."""
    pdf_path = str(tmp_path / "scanned_doc.pdf")
    c = canvas.Canvas(pdf_path)
    # Add 2 empty pages without drawing text
    c.showPage()
    c.showPage()
    c.save()
    return pdf_path


def test_extract_text_by_page_success(sample_digital_pdf):
    """Verifies that digital text is extracted page by page with sequential page numbers and counts."""
    extractor = TextExtractor()
    pages = extractor.extract_text_by_page(sample_digital_pdf)

    assert len(pages) == 2
    assert isinstance(pages[0], ExtractedPageTextDTO)

    # Page 1 verification
    assert pages[0].page_number == 1
    assert "Annual Report Fiscal Year 2024" in pages[0].raw_text
    assert pages[0].char_count > 0

    # Page 2 verification
    assert pages[1].page_number == 2
    assert "Management Discussion" in pages[1].raw_text
    assert pages[1].char_count > 0


def test_scanned_pdf_raises_proc_002(blank_scanned_pdf):
    """Verifies that a document with 0 extractable characters raises ScannedPDFError with code PROC_002."""
    extractor = TextExtractor()

    with pytest.raises(ScannedPDFError) as exc_info:
        extractor.extract_text_by_page(blank_scanned_pdf)

    assert exc_info.value.error_code == "PROC_002"
    assert "PROC_002" in str(exc_info.value)
    assert "scanned pdf requiring ocr" in str(exc_info.value).lower()


def test_extract_text_missing_file(tmp_path):
    """Verifies that attempting extraction on a non-existent file path raises FileNotFoundError."""
    extractor = TextExtractor()
    nonexistent = str(tmp_path / "nonexistent_file.pdf")

    with pytest.raises(FileNotFoundError):
        extractor.extract_text_by_page(nonexistent)
