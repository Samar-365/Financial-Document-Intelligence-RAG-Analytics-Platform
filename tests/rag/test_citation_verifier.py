import pytest
from app.rag.citation_parser import RawCitationToken
from app.rag.citation_verifier import CitationVerifier, VerifiedCitationDTO
from app.rag.retriever import RetrievedChunkDTO


def _create_chunk(
    doc_id: str,
    page: int,
    content: str,
    index: int = 0,
    score: float = 0.88,
) -> RetrievedChunkDTO:
    return RetrievedChunkDTO(
        chunk_id=f"chunk-{doc_id}-{page}-{index}",
        document_id=doc_id,
        chunk_index=index,
        page_number=page,
        content=content,
        similarity_score=score,
    )


def test_citation_verification_dod():
    """Verifies Definition of Done (DoD):

    100% of valid citations contain verifiable snippet text; phantom citations flagged is_verified=False.
    """
    verifier = CitationVerifier()

    chunks = [
        _create_chunk(
            doc_id="annual_report.pdf",
            page=42,
            content="Total operating revenue expanded 14.5% to reach $1.2 billion for the fiscal year ended December 31. Working capital remained stable at $340 million.",
        ),
        _create_chunk(
            doc_id="annual_report.pdf",
            page=45,
            content="Research and development expenditures rose to $120 million, representing 10% of total revenue.",
        ),
    ]

    tokens = [
        RawCitationToken(document_name="annual_report.pdf", page_number=42),  # Valid
        RawCitationToken(document_name="annual_report.pdf", page_number=99),  # Phantom (wrong page)
        RawCitationToken(document_name="phantom_filing.pdf", page_number=10), # Phantom (wrong doc)
    ]

    results = verifier.verify_citations(tokens, chunks)

    assert len(results) == 3

    # Valid citation on page 42
    assert results[0].is_verified is True
    assert results[0].document_name == "annual_report.pdf"
    assert results[0].page_number == 42
    assert len(results[0].source_snippet) > 0
    assert "operating revenue expanded 14.5%" in results[0].source_snippet

    # Phantom citation (page 99)
    assert results[1].is_verified is False
    assert results[1].document_name == "annual_report.pdf"
    assert results[1].page_number == 99
    assert results[1].source_snippet == ""

    # Phantom citation (phantom_filing.pdf)
    assert results[2].is_verified is False
    assert results[2].document_name == "phantom_filing.pdf"
    assert results[2].page_number == 10
    assert results[2].source_snippet == ""


def test_multiple_chunks_same_page():
    """Verifies that evidence can be extracted across multiple chunks belonging to the same page."""
    verifier = CitationVerifier()

    chunks = [
        _create_chunk("10K-FY25", 12, "Section 1: General executive summary and market outlook.", index=0),
        _create_chunk("10K-FY25", 12, "Section 2: Operating income increased 22% to $450 million.", index=1),
    ]

    tokens = [RawCitationToken(document_name="10K-FY25", page_number=12)]

    results = verifier.verify_citations(
        tokens,
        chunks,
        claim_context="Operating income increased 22% to $450 million.",
    )

    assert len(results) == 1
    assert results[0].is_verified is True
    assert "Operating income increased 22% to $450 million." in results[0].source_snippet


def test_claim_context_sentence_alignment():
    """Verifies that when claim_context is supplied, the sentence with highest semantic keyword overlap is selected."""
    verifier = CitationVerifier()

    content = (
        "Global headcount remained flat at 45,000 employees worldwide. "
        "Automotive gross margin improved to 21.4% driven by lower battery material costs. "
        "Income tax expense was recognized at an effective rate of 16.5%."
    )
    chunks = [_create_chunk("TSLA-10Q", 5, content)]

    tokens = [RawCitationToken(document_name="TSLA-10Q", page_number=5)]

    results = verifier.verify_citations(
        tokens,
        chunks,
        claim_context="Automotive gross margin was 21.4% due to cheaper battery costs.",
    )

    assert len(results) == 1
    assert results[0].is_verified is True
    assert results[0].source_snippet == "Automotive gross margin improved to 21.4% driven by lower battery material costs."


def test_table_markdown_evidence_extraction():
    """Verifies evidence extraction when chunk contains a markdown pipe-delimited table."""
    verifier = CitationVerifier()

    table_content = (
        "| Financial Metric | FY24 | FY25 |\n"
        "| :--- | :--- | :--- |\n"
        "| Net Sales | $8,500M | $9,800M |\n"
        "| Gross Profit | $3,200M | $3,900M |\n"
        "| Operating Margin | 15.2% | 18.1% |"
    )
    chunks = [_create_chunk("financial_statements.pdf", 20, table_content)]

    tokens = [RawCitationToken(document_name="financial_statements.pdf", page_number=20)]

    results = verifier.verify_citations(
        tokens,
        chunks,
        claim_context="Net sales were $9,800M in FY25.",
    )

    assert len(results) == 1
    assert results[0].is_verified is True
    assert "Net Sales" in results[0].source_snippet
    assert "$9,800M" in results[0].source_snippet


def test_case_insensitive_matching_and_whitespace():
    """Verifies case-insensitive and trimmed matching between token and chunk document names."""
    verifier = CitationVerifier()

    chunks = [
        _create_chunk("Apple_10K_Report.pdf", 8, "Cash flow from operations reached $110 billion.")
    ]

    tokens = [
        RawCitationToken(document_name="apple_10k_report.pdf", page_number=8)
    ]

    results = verifier.verify_citations(tokens, chunks)

    assert len(results) == 1
    assert results[0].is_verified is True
    assert results[0].document_name == "apple_10k_report.pdf"
    assert "Cash flow from operations reached $110 billion." in results[0].source_snippet


def test_empty_tokens_and_empty_chunks():
    """Verifies proper handling of empty token lists or empty chunk lists."""
    verifier = CitationVerifier()

    # Empty tokens
    assert verifier.verify_citations([], [_create_chunk("doc.pdf", 1, "test")]) == []

    # Empty chunks -> all citations flagged as phantom
    tokens = [RawCitationToken(document_name="doc.pdf", page_number=1)]
    results = verifier.verify_citations(tokens, [])
    assert len(results) == 1
    assert results[0].is_verified is False
    assert results[0].source_snippet == ""


def test_input_type_validation():
    """Verifies that non-list or mismatched element types raise TypeError."""
    verifier = CitationVerifier()

    with pytest.raises(TypeError, match="tokens must be a list"):
        verifier.verify_citations("not_a_list", [])  # type: ignore

    with pytest.raises(TypeError, match="retrieved_chunks must be a list"):
        verifier.verify_citations([], "not_a_list")  # type: ignore

    with pytest.raises(TypeError, match="expected RawCitationToken"):
        verifier.verify_citations([{"doc": "test"}], [])  # type: ignore

    with pytest.raises(TypeError, match="expected RetrievedChunkDTO"):
        token = RawCitationToken(document_name="doc.pdf", page_number=1)
        verifier.verify_citations([token], [{"content": "invalid"}])  # type: ignore


def test_verify_answer_end_to_end():
    """Verifies end-to-end convenience method combining citation parsing and verification."""
    verifier = CitationVerifier()

    chunks = [
        _create_chunk("AAPL-FY25.pdf", 14, "Total revenue for fiscal 2025 rose to $420B."),
        _create_chunk("AAPL-FY25.pdf", 20, "Diluted earnings per share increased to $6.75 per share."),
    ]

    answer = (
        "In fiscal 2025, Apple generated $420B in revenue [Doc: AAPL-FY25.pdf, Page: 14]. "
        "Diluted EPS was $6.75 [Doc: AAPL-FY25.pdf, Page: 20]. "
        "They also announced a $500B dividend [Doc: FakeNews.pdf, Page: 1]."
    )

    results = verifier.verify_answer(answer, chunks)

    assert len(results) == 3
    # First citation (page 14)
    assert results[0].document_name == "AAPL-FY25.pdf"
    assert results[0].page_number == 14
    assert results[0].is_verified is True
    assert "revenue for fiscal 2025" in results[0].source_snippet

    # Second citation (page 20)
    assert results[1].document_name == "AAPL-FY25.pdf"
    assert results[1].page_number == 20
    assert results[1].is_verified is True
    assert "earnings per share" in results[1].source_snippet

    # Third citation (FakeNews.pdf)
    assert results[2].document_name == "FakeNews.pdf"
    assert results[2].page_number == 1
    assert results[2].is_verified is False
    assert results[2].source_snippet == ""


def test_verify_answer_input_validation():
    """Verifies input validation on verify_answer."""
    verifier = CitationVerifier()

    with pytest.raises(TypeError, match="generated_text must be a string"):
        verifier.verify_answer(12345, [])  # type: ignore
