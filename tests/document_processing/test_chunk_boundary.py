import pytest
from app.document_processing.chunk_boundary import BoundaryManager
from app.document_processing.chunker import TextSplitter


def test_empty_and_single_chunk_overlap():
    """Verifies handling of empty chunk lists and single chunks."""
    bm = BoundaryManager()
    assert bm.apply_overlap([]) == []
    assert bm.apply_overlap(["Single standalone chunk."]) == ["Single standalone chunk."]


def test_exact_150_char_consecutive_overlap():
    """Verifies the Definition of Done (DoD):

    100% of consecutive chunk pairs share exact 150-character overlap.
    """
    bm = BoundaryManager()
    c1 = (
        "Operating revenue for the third fiscal quarter reached $4.2 billion, driven by cloud infrastructure expansions. "
        "Enterprise subscription renewals continued at a 94% retention rate across major global enterprise accounts."
    )
    c2 = (
        "Capital expenditures stood at $650 million, focused on high-density GPU data centers and power modernization. "
        "Management authorized an incremental share repurchase program to optimize shareholder return metrics."
    )
    c3 = (
        "Operating cash flows exceeded $1.1 billion, maintaining liquidity reserves well above credit facility thresholds. "
        "Debt-to-equity ratio improved to 0.42x reflecting disciplined repayment of short-term notes."
    )

    chunks = [c1, c2, c3]
    result = bm.apply_overlap(chunks, overlap_size=150)
    assert len(result) == 3

    # Check 100% of consecutive pairs
    for i in range(1, len(result)):
        prev_chunk = result[i - 1]
        curr_chunk = result[i]
        expected_overlap = prev_chunk[-150:]
        assert len(expected_overlap) == 150
        assert curr_chunk.startswith(expected_overlap), (
            f"Consecutive pair ({i-1}, {i}) failed 150-character overlap check.\n"
            f"Expected prefix: '{expected_overlap}'\n"
            f"Actual start: '{curr_chunk[:160]}'"
        )


def test_custom_overlap_size():
    """Verifies that custom overlap sizes are applied properly."""
    bm = BoundaryManager()
    c1 = "Revenue expansion was supported by strong consumer demand across international markets in FY25."
    c2 = "Gross margins expanded by 180 basis points driven by favorable product mix and component deflation."
    result = bm.apply_overlap([c1, c2], overlap_size=50)

    expected_overlap = c1[-50:]
    assert result[1].startswith(expected_overlap)


def test_overlap_when_chunk_shorter_than_overlap_size():
    """Verifies safe behavior when previous chunk is shorter than overlap_size."""
    bm = BoundaryManager()
    c1 = "Short text."  # 11 characters < 150
    c2 = "Following section reviewing balance sheet assets and liabilities."
    result = bm.apply_overlap([c1, c2], overlap_size=150)
    assert len(result) == 2
    assert result[1].startswith(c1)


def test_table_integrity_lock_merges_split_table():
    """Verifies that a continuous markdown table split across chunks is locked together."""
    bm = BoundaryManager(target_window=600)
    c1 = (
        "Financial Statement Summary:\n"
        "| Quarter | Revenue ($M) | Operating Income ($M) |\n"
        "| Q1 | 1200 | 250 |\n"
        "| Q2 | 1350 | 290 |"
    )
    c2 = (
        "| Q3 | 1420 | 310 |\n"
        "| Q4 | 1580 | 360 |\n"
        "End of quarterly summary table."
    )

    result = bm.apply_overlap([c1, c2], overlap_size=50)
    # Both parts form a table and total length (around 240 chars) fits well within target_window (600)
    assert len(result) == 1
    full_text = result[0]
    assert "| Q1 | 1200 | 250 |" in full_text
    assert "| Q4 | 1580 | 360 |" in full_text


def test_table_integrity_lock_respects_target_window():
    """Verifies that when combined table text exceeds target_window, it respects row boundaries without merge."""
    bm = BoundaryManager(target_window=70)
    c1 = (
        "| Q1 | 1200 | 250 |\n"
        "| Q2 | 1350 | 290 |"
    )
    c2 = (
        "| Q3 | 1420 | 310 |\n"
        "| Q4 | 1580 | 360 |"
    )
    # Total length (87 chars) exceeds target_window (70), so chunks must not be merged past target window
    result = bm.apply_overlap([c1, c2], overlap_size=20)
    assert len(result) == 2



def test_repair_split_cell_rows_zero_mid_cell_splits():
    """Verifies the Definition of Done (DoD): zero markdown tables split across a single cell row."""
    bm = BoundaryManager()
    # Chunk 1 ends in the middle of a row ('| Q2 | 1350 |')
    c1 = (
        "Quarterly Highlights:\n"
        "| Quarter | Revenue ($M) | Net Profit ($M) |\n"
        "| Q1 | 1200 | 250 |\n"
        "| Q2 | 1350 |"
    )
    # Chunk 2 begins with the remainder of that cut cell row ('290 |')
    c2 = (
        " 290 |\n"
        "| Q3 | 1420 | 310 |\n"
        "Additional notes on performance."
    )

    result = bm.apply_overlap([c1, c2], overlap_size=50)
    # The split row '| Q2 | 1350 | 290 |' must be repaired into a complete row
    combined = "\n".join(result)
    assert "| Q2 | 1350 | 290 |" in combined
    # No ragged incomplete line with '| Q2 | 1350 |' ending without closing cell
    for chunk in result:
        for line in chunk.splitlines():
            s = line.strip()
            if s.startswith("|"):
                assert s.endswith("|"), f"Found table row split mid-cell: '{line}'"


def test_overlap_preserves_table_formatting():
    """Verifies that prepending overlap before a table row maintains valid markdown table lines."""
    bm = BoundaryManager()
    c1 = "A" * 200  # Narrative text
    c2 = (
        "| Metric | Value |\n"
        "| Revenue | $500M |\n"
        "| Margin | 25% |"
    )
    result = bm.apply_overlap([c1, c2], overlap_size=150)
    assert len(result) == 2

    # Verify overlap
    assert result[1].startswith(c1[-150:])

    # Verify the table rows are on their own lines (not mashed onto narrative text)
    lines = [l.strip() for l in result[1].splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|")]
    assert len(table_lines) == 3
    assert table_lines[0] == "| Metric | Value |"
    assert table_lines[1] == "| Revenue | $500M |"
    assert table_lines[2] == "| Margin | 25% |"


def test_pipeline_integration_with_text_splitter():
    """Verifies end-to-end integration: TextSplitter raw chunks -> BoundaryManager overlap application."""
    splitter = TextSplitter(target_chunk_size=400, min_chunk_size=100)
    bm = BoundaryManager(target_window=850)

    text = (
        "Operating profit expanded across all three divisions during the fiscal year 2025. "
        "The software solutions division generated $2.4 billion in annual recurring revenue, up 18% YoY. "
        "Hardware and device shipments experienced modest deceleration due to supply constraints in Asia Pacific.\n\n"
        "| Division | Revenue ($M) | Operating Margin (%) |\n"
        "| Cloud Software | 2400 | 32.5 |\n"
        "| Enterprise Hardware | 1100 | 14.2 |\n"
        "| Professional Services | 650 | 21.0 |\n\n"
        "Cash flow generation remained resilient with free cash flow reaching $820 million. "
        "The Company allocated $300 million to strategic venture investments and $250 million to debt service. "
        "Liquidity metrics remain robust heading into the next operating cycle."
    )

    raw_chunks = splitter.split_text(text)
    assert len(raw_chunks) >= 2

    processed_chunks = bm.apply_overlap(raw_chunks, overlap_size=150)
    assert len(processed_chunks) >= 2

    # Check 100% consecutive 150-char overlap
    for i in range(1, len(processed_chunks)):
        prev = processed_chunks[i - 1]
        curr = processed_chunks[i]
        assert curr.startswith(prev[-150:])


def test_invalid_parameters():
    """Verifies validation exceptions for illegal configuration values."""
    with pytest.raises(ValueError, match="target_window must be a positive integer"):
        BoundaryManager(target_window=0)

    with pytest.raises(ValueError, match="target_window must be a positive integer"):
        BoundaryManager(target_window=-100)

    bm = BoundaryManager()
    with pytest.raises(ValueError, match="overlap_size cannot be negative"):
        bm.apply_overlap(["Chunk 1", "Chunk 2"], overlap_size=-10)
