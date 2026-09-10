import uuid
import pytest
from app.document_processing.metadata_tagger import MetadataTagger, TextChunkDTO
from app.document_processing.cleaner import TextCleaner
from app.document_processing.chunker import TextSplitter
from app.document_processing.chunk_boundary import BoundaryManager


def test_empty_page_chunks():
    """Verifies that an empty list of page chunks returns an empty list."""
    tagger = MetadataTagger()
    result = tagger.tag_chunks("doc-101", [])
    assert result == []


def test_tag_chunks_provenance_and_indexing():
    """Verifies the Definition of Done (DoD):

    Every chunk emits valid metadata with non-null page_number matching originating PDF page.
    Also verifies UUID uniqueness, correct document_id, and sequential 0-based indexing.
    """
    tagger = MetadataTagger()
    doc_id = "doc-fy25-annual-report"
    page_chunks = [
        (1, "Executive overview and operational summary of fiscal 2025."),
        (1, "Detailed breakdown of cloud software ARR growth of 24%."),
        (2, "Balance sheet highlights: Cash reserves stand at $4.5B."),
        (3, "Auditor's report confirming fair presentation of accounts."),
    ]

    tagged = tagger.tag_chunks(doc_id, page_chunks)
    assert len(tagged) == 4

    # Check UUID uniqueness
    chunk_ids = [c.chunk_id for c in tagged]
    assert len(set(chunk_ids)) == 4
    for cid in chunk_ids:
        # Validate UUID format
        parsed_uuid = uuid.UUID(cid)
        assert str(parsed_uuid) == cid

    # Verify sequential chunk_index
    assert [c.chunk_index for c in tagged] == [0, 1, 2, 3]

    # Verify document_id
    assert all(c.document_id == doc_id for c in tagged)

    # Verify matching page numbers (DoD)
    expected_pages = [1, 1, 2, 3]
    for i, c in enumerate(tagged):
        assert c.page_number == expected_pages[i]
        assert c.page_number is not None
        assert c.content == page_chunks[i][1]


def test_token_estimate_calculation():
    """Verifies token count estimation using 4-character-per-token heuristic."""
    tagger = MetadataTagger()
    # 800 characters -> exactly 200 tokens
    text_800 = "A" * 800
    # 10 characters -> ceil(10/4) = 3 tokens
    text_10 = "1234567890"
    # Empty string -> 0 tokens
    text_empty = ""

    chunks = [
        (1, text_800),
        (1, text_10),
        (2, text_empty),
    ]
    tagged = tagger.tag_chunks("doc-tokens", chunks)
    assert tagged[0].token_estimate == 200
    assert tagged[1].token_estimate == 3
    assert tagged[2].token_estimate == 0


def test_table_chunk_detection():
    """Verifies boolean tagging of is_table_chunk for markdown tables vs pure narrative."""
    tagger = MetadataTagger()
    narrative = (
        "In fiscal 2025, operating profit margins expanded significantly due to "
        "disciplined cost control, higher operating leverage, and international volume expansion."
    )
    table_content = (
        "Key Financial Metrics Summary:\n"
        "| Metric | FY24 ($M) | FY25 ($M) |\n"
        "| Revenue | 1200 | 1450 |\n"
        "| Net Profit | 220 | 280 |"
    )

    tagged = tagger.tag_chunks("doc-table", [(1, narrative), (2, table_content)])
    assert tagged[0].is_table_chunk is False
    assert tagged[1].is_table_chunk is True


def test_mixed_narrative_and_table_pages():
    """Verifies multi-page document with mixed content types correctly sets provenance and flags."""
    tagger = MetadataTagger()
    doc_id = "doc-mixed-99"
    input_data = [
        (1, "Page 1 intro narrative without tables."),
        (1, "| Metric | Value |\n| Margin | 34% |"),
        (2, "Page 2 narrative continuation."),
        (3, "| Assets | Liabilities |\n| 5000 | 2300 |"),
    ]

    tagged = tagger.tag_chunks(doc_id, input_data)
    assert len(tagged) == 4

    assert tagged[0].page_number == 1
    assert tagged[0].is_table_chunk is False

    assert tagged[1].page_number == 1
    assert tagged[1].is_table_chunk is True

    assert tagged[2].page_number == 2
    assert tagged[2].is_table_chunk is False

    assert tagged[3].page_number == 3
    assert tagged[3].is_table_chunk is True


def test_validation_errors():
    """Verifies validation error handling for illegal arguments."""
    tagger = MetadataTagger()

    # Empty document ID
    with pytest.raises(ValueError, match="document_id must be a non-empty string"):
        tagger.tag_chunks("", [(1, "Some content")])

    with pytest.raises(ValueError, match="document_id must be a non-empty string"):
        tagger.tag_chunks("   ", [(1, "Some content")])

    # Invalid page number (< 1)
    with pytest.raises(ValueError, match="Page numbers must be >= 1"):
        tagger.tag_chunks("doc-1", [(0, "Invalid page 0")])

    with pytest.raises(ValueError, match="Page numbers must be >= 1"):
        tagger.tag_chunks("doc-1", [(-2, "Invalid negative page")])


def test_dto_serialization():
    """Verifies TextChunkDTO serialization to dictionary and pydantic schema validation."""
    dto = TextChunkDTO(
        chunk_id=str(uuid.uuid4()),
        document_id="doc-serialization-test",
        chunk_index=0,
        page_number=1,
        content="Sample chunk content.",
        token_estimate=5,
        is_table_chunk=False,
    )
    data = dto.model_dump()
    assert isinstance(data, dict)
    assert data["chunk_index"] == 0
    assert data["page_number"] == 1
    assert data["token_estimate"] == 5
    assert data["is_table_chunk"] is False


def test_end_to_end_pipeline_integration():
    """Verifies the complete Sprint 1 Phase 1 & 2 pipeline integration:

    Raw Text -> TextCleaner -> TextSplitter -> BoundaryManager -> MetadataTagger -> List[TextChunkDTO].
    """
    raw_page_1 = (
        "ABC Holdings Annual Report 2025\n"
        "The Company experienced strong ﬁnancial ﬂow across its core software business.\n"
        "Consolidated revenue reached $3,450,000,000, representing a 15% increase.\n"
        "Page 1 of 12"
    )
    raw_page_2 = (
        "Operating expenses were tightly managed: oper-\n"
        "ating income was $820.50 million.\n"
        "| Segment | Revenue ($M) |\n"
        "| Cloud | 2100 |\n"
        "| Enterprise | 1350 |\n"
        "- 2 -"
    )

    cleaner = TextCleaner()
    splitter = TextSplitter(target_chunk_size=400, min_chunk_size=50)
    boundary_manager = BoundaryManager(target_window=850)
    tagger = MetadataTagger()

    # Clean pages
    cleaned_p1 = cleaner.clean_text(raw_page_1)
    cleaned_p2 = cleaner.clean_text(raw_page_2)

    # Split pages
    p1_chunks = splitter.split_text(cleaned_p1)
    p2_chunks = splitter.split_text(cleaned_p2)

    # Apply overlap across each page's chunks
    p1_overlap = boundary_manager.apply_overlap(p1_chunks, overlap_size=50)
    p2_overlap = boundary_manager.apply_overlap(p2_chunks, overlap_size=50)

    # Assemble page tuples
    page_tuples = [(1, c) for c in p1_overlap] + [(2, c) for c in p2_overlap]

    # Tag chunks
    final_dtos = tagger.tag_chunks("doc-pipeline-test", page_tuples)

    assert len(final_dtos) >= 2
    # Verify provenance
    assert all(c.document_id == "doc-pipeline-test" for c in final_dtos)
    assert all(c.page_number in (1, 2) for c in final_dtos)
    assert any(c.is_table_chunk for c in final_dtos)
    # Verify ligatures were cleaned in content
    assert any("financial flow" in c.content for c in final_dtos)
    # Verify dehyphenation in content
    assert any("operating income" in c.content for c in final_dtos)
