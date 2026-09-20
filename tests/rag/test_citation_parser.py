import pytest
from pydantic import ValidationError

from app.rag.citation_parser import CitationParser, RawCitationToken


def test_parse_single_citation_dod():
    """Verifies Definition of Done (DoD):

    Parses [Doc: annual_report.pdf, Page: 42] into structured token with page integer 42.
    """
    text = "Consolidated revenue grew 14% to $120M [Doc: annual_report.pdf, Page: 42]."
    tokens = CitationParser.parse_citations(text)

    assert len(tokens) == 1
    assert tokens[0].document_name == "annual_report.pdf"
    assert tokens[0].page_number == 42
    assert isinstance(tokens[0].page_number, int)


def test_citation_deduplication_preserves_first_occurrence_order():
    """Verifies Task 2 (Citation Deduplication):

    Deduplicates multiple identical page citations while strictly preserving first-occurrence order.
    """
    text = (
        "Operating profit expanded [Doc: 10K_2025.pdf, Page: 15]. "
        "Gross margin was 45.2% [Doc: 10Q_Q3.pdf, Page: 8]. "
        "EBITDA reached $35M [Doc: 10K_2025.pdf, Page: 15]. "
        "Free cash flow was positive [Doc: investor_presentation.pdf, Page: 22]. "
        "Operating expenses declined 4% [Doc: 10Q_Q3.pdf, Page: 8]. "
        "Capital expenditure totaled $12M [Doc: 10K_2025.pdf, Page: 15]."
    )

    tokens = CitationParser.parse_citations(text)

    assert len(tokens) == 3
    assert tokens[0] == RawCitationToken(document_name="10K_2025.pdf", page_number=15)
    assert tokens[1] == RawCitationToken(document_name="10Q_Q3.pdf", page_number=8)
    assert tokens[2] == RawCitationToken(
        document_name="investor_presentation.pdf", page_number=22
    )


def test_same_doc_different_pages_and_different_docs_same_page():
    """Verifies that citations sharing doc name or page number are treated as distinct tokens."""
    text = (
        "Item A [Doc: filing.pdf, Page: 10]. "
        "Item B [Doc: filing.pdf, Page: 25]. "
        "Item C [Doc: other_filing.pdf, Page: 10]."
    )
    tokens = CitationParser.parse_citations(text)

    assert len(tokens) == 3
    assert tokens[0] == RawCitationToken(document_name="filing.pdf", page_number=10)
    assert tokens[1] == RawCitationToken(document_name="filing.pdf", page_number=25)
    assert tokens[2] == RawCitationToken(document_name="other_filing.pdf", page_number=10)


def test_whitespace_and_padding_tolerance():
    """Verifies that variations in spacing inside citation tags are trimmed and handled cleanly."""
    text = (
        "Net income reached $500M [Doc:   annual_report_fy25.pdf  ,  Page:   104  ]. "
        "Debt-to-equity ratio improved [Doc:balance_sheet.pdf,Page:5]."
    )
    tokens = CitationParser.parse_citations(text)

    assert len(tokens) == 2
    assert tokens[0].document_name == "annual_report_fy25.pdf"
    assert tokens[0].page_number == 104
    assert tokens[1].document_name == "balance_sheet.pdf"
    assert tokens[1].page_number == 5


def test_case_insensitive_citation_markers():
    """Verifies case insensitivity for 'Doc' and 'Page' labels."""
    text = (
        "Fact 1 [doc: report.pdf, page: 3]. "
        "Fact 2 [DOC: report.pdf, PAGE: 7]. "
        "Fact 3 [Doc: report.pdf, Page: 3]."  # Duplicate of Fact 1
    )
    tokens = CitationParser.parse_citations(text)

    assert len(tokens) == 2
    assert tokens[0] == RawCitationToken(document_name="report.pdf", page_number=3)
    assert tokens[1] == RawCitationToken(document_name="report.pdf", page_number=7)


def test_empty_or_absent_citations():
    """Verifies that strings without citations or empty strings return empty lists."""
    assert CitationParser.parse_citations("") == []
    assert CitationParser.parse_citations("   \n\t  ") == []
    assert (
        CitationParser.parse_citations(
            "The provided document does not contain sufficient information to answer this query."
        )
        == []
    )
    assert (
        CitationParser.parse_citations(
            "There are brackets here [like this] and numbers (42) but no valid citation."
        )
        == []
    )


def test_input_type_validation():
    """Verifies that passing non-string arguments raises TypeError."""
    with pytest.raises(TypeError, match="text must be a string"):
        CitationParser.parse_citations(None)  # type: ignore

    with pytest.raises(TypeError, match="text must be a string"):
        CitationParser.parse_citations(123)  # type: ignore

    with pytest.raises(TypeError, match="text must be a string"):
        CitationParser.parse_citations(["[Doc: doc.pdf, Page: 1]"])  # type: ignore


def test_raw_citation_token_validation():
    """Verifies Pydantic model validation on RawCitationToken."""
    token = RawCitationToken(document_name="filing.pdf", page_number=1)
    assert token.document_name == "filing.pdf"
    assert token.page_number == 1

    with pytest.raises(ValidationError):
        # page_number must be ge=1
        RawCitationToken(document_name="filing.pdf", page_number=0)

    with pytest.raises(ValidationError):
        RawCitationToken(document_name="filing.pdf", page_number=-5)


def test_strip_citations_helper():
    """Verifies that strip_citations cleanly removes citation tags and fixes punctuation spacing."""
    text = (
        "Total revenue in fiscal 2025 was $420 billion [Doc: AAPL-10K, Page: 15]. "
        "Gross margins reached 46.2% [Doc: AAPL-10K, Page: 18]."
    )
    cleaned = CitationParser.strip_citations(text)
    assert "[Doc:" not in cleaned
    assert (
        cleaned
        == "Total revenue in fiscal 2025 was $420 billion. Gross margins reached 46.2%."
    )


def test_strip_citations_input_validation():
    """Verifies input validation on strip_citations."""
    with pytest.raises(TypeError, match="text must be a string"):
        CitationParser.strip_citations(None)  # type: ignore
