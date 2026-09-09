import pytest
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from app.document_processing.table_extractor import TableExtractor, ExtractedTableDTO


@pytest.fixture
def sample_pdf_with_table(tmp_path) -> str:
    """Fixture to generate a PDF containing a bordered financial statement table."""
    pdf_path = str(tmp_path / "financial_table.pdf")
    doc = SimpleDocTemplate(pdf_path)
    data = [
        ["Line Item", "FY2023", "FY2024"],
        ["Cash & Equivalents", "$12,400", "$15,200"],
        ["Total Assets", "$95,000", "$110,000"],
    ]
    t = Table(data)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    doc.build([t])
    return pdf_path


@pytest.fixture
def empty_pdf(tmp_path) -> str:
    """Fixture to generate a PDF with no tables."""
    from reportlab.pdfgen import canvas

    pdf_path = str(tmp_path / "plain_text.pdf")
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Pure narrative paragraph with no tabular structures.")
    c.save()
    return pdf_path


def test_serialize_to_markdown_formatting():
    """Verifies that 2D raw list converts into valid pipe-delimited markdown with padding and headers."""
    raw_data = [
        ["Metric", "FY23", "FY24"],
        ["Operating\nCash Flow", "1,200", "1,450"],
        ["Net Margin | %", "15.2%", "16.8%"],
    ]
    markdown_str, row_count, col_count = TableExtractor._serialize_to_markdown(raw_data)

    assert row_count == 3
    assert col_count == 3

    lines = markdown_str.split("\n")
    assert lines[0] == "| Metric | FY23 | FY24 |"
    assert lines[1] == "| :--- | :--- | :--- |"
    # Verify newline replacement in cell
    assert "| Operating Cash Flow | 1,200 | 1,450 |" in lines[2]
    # Verify pipe character escaping
    assert "Net Margin \\| %" in lines[3]


def test_serialize_ragged_rows():
    """Verifies that rows with differing column counts are padded to uniform width."""
    ragged_data = [
        ["Col1", "Col2", "Col3"],
        ["Val1"],
        ["ValA", "ValB"],
    ]
    markdown_str, row_count, col_count = TableExtractor._serialize_to_markdown(ragged_data)
    assert row_count == 3
    assert col_count == 3
    lines = markdown_str.split("\n")
    assert lines[2] == "| Val1 |  |  |"
    assert lines[3] == "| ValA | ValB |  |"


def test_extract_tables_from_pdf(sample_pdf_with_table):
    """Verifies extraction and markdown serialization of a real financial table in a PDF."""
    extractor = TableExtractor()
    tables = extractor.extract_tables(sample_pdf_with_table)

    assert len(tables) == 1
    table_dto = tables[0]
    assert isinstance(table_dto, ExtractedTableDTO)
    assert table_dto.page_number == 1
    assert table_dto.table_index == 0
    assert table_dto.row_count == 3
    assert table_dto.col_count == 3

    # Validate markdown contents
    assert "| Line Item | FY2023 | FY2024 |" in table_dto.markdown_table
    assert "| :--- | :--- | :--- |" in table_dto.markdown_table
    assert "Cash & Equivalents" in table_dto.markdown_table
    assert "$15,200" in table_dto.markdown_table


def test_extract_tables_none_present(empty_pdf):
    """Verifies that a document with no tabular borders returns an empty list."""
    extractor = TableExtractor()
    tables = extractor.extract_tables(empty_pdf)
    assert tables == []


def test_extract_tables_file_not_found(tmp_path):
    """Verifies that attempting extraction on a non-existent path raises FileNotFoundError."""
    extractor = TableExtractor()
    missing_path = str(tmp_path / "missing_file.pdf")
    with pytest.raises(FileNotFoundError):
        extractor.extract_tables(missing_path)
