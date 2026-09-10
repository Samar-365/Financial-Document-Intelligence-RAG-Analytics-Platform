import pytest
from app.document_processing.chunker import TextSplitter


def test_empty_and_whitespace_input():
    """Verifies that empty string or whitespace-only strings return an empty list."""
    splitter = TextSplitter()
    assert splitter.split_text("") == []
    assert splitter.split_text("   \n\t   \n   ") == []


def test_single_short_chunk_below_target():
    """Verifies that text smaller than target_chunk_size is returned as a single chunk."""
    splitter = TextSplitter(target_chunk_size=800, min_chunk_size=100)
    text = "Consolidated net profit for Q3 FY26 stood at INR 4,520 crore, marking a 14.5% year-over-year increase."
    chunks = splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_short_text_below_min_threshold():
    """Verifies that text smaller than min_chunk_size (when standalone) is safely returned as 1 chunk."""
    splitter = TextSplitter(target_chunk_size=800, min_chunk_size=100)
    text = "Short disclaimer note."
    assert len(text) < 100
    chunks = splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0] == "Short disclaimer note."


def test_hierarchical_recursive_splitting():
    """Verifies that splitting respects the hierarchy (\n\n -> \n -> .  -> ;  -> ' ')."""
    splitter = TextSplitter(target_chunk_size=120, min_chunk_size=40)
    p1 = "First financial paragraph discussing operating margin expansion and gross revenue."
    p2 = "Second financial paragraph outlining working capital cycles and debt repayments."
    p3 = "Third financial paragraph reviewing capital expenditures on data center modernization."
    text = f"{p1}\n\n{p2}\n\n{p3}"

    chunks = splitter.split_text(text)
    assert len(chunks) >= 2
    # Ensure paragraph contents were preserved across chunks
    assert any("First financial paragraph" in c for c in chunks)
    assert any("Third financial paragraph" in c for c in chunks)


def test_minimum_chunk_threshold_merging():
    """Verifies that a trailing fragment smaller than min_chunk_size is merged into the preceding chunk."""
    splitter = TextSplitter(target_chunk_size=300, min_chunk_size=100)
    # Long paragraph ~250 chars followed by a tiny 40-character fragment
    part1 = (
        "Operating activities provided positive net cash flows of $850 million for the fiscal quarter. "
        "Inventories decreased significantly due to accelerated shipment schedules across European and Asian supply hubs."
    )
    part2 = "Audited results remain subject to review."  # 41 chars < min_chunk_size (100)
    text = f"{part1}\n\n{part2}"

    chunks = splitter.split_text(text)
    # The trailing 41-character fragment must be merged into the previous chunk, not emitted as a standalone chunk
    assert len(chunks) == 1
    assert "Audited results remain subject to review." in chunks[0]
    assert len(chunks[0]) >= len(part1)


def test_no_chunks_below_min_size_on_multichunk():
    """Verifies that zero chunks in a multi-chunk document are smaller than min_chunk_size."""
    splitter = TextSplitter(target_chunk_size=500, min_chunk_size=100)
    text = (
        "In fiscal 2025, operating revenue increased by 22% compared to fiscal 2024. "
        "The primary drivers of this top-line expansion included strong enterprise cloud adoption, "
        "strategic geographic diversification, and robust demand for recurring software licenses.\n\n"
        "Operating costs increased at a moderate rate of 8%, resulting in an operating margin expansion "
        "of 340 basis points to reach an all-time high of 28.5%. "
        "Research and development investments totaled $1.2 billion, concentrated in generative AI.\n\n"
        "Free cash flow conversion reached 112% of net income, bolstered by disciplined working capital management. "
        "The Board of Directors approved a quarterly dividend increase of 10% alongside an expanded share repurchase authorization. "
        "Management remains optimistic regarding macroeconomic tailwinds across emerging markets.\n\n"
        "Short tail end."
    )
    chunks = splitter.split_text(text)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert len(chunk) >= 100, f"Chunk {i} has length {len(chunk)} < 100: '{chunk}'"


def test_chunk_length_distribution_dod():
    """Verifies the Definition of Done (DoD):

    Document splits with >= 90% of chunks between 650 and 850 characters; zero chunks < 100 characters.
    """
    splitter = TextSplitter(target_chunk_size=800, min_chunk_size=100)

    # Realistic financial report text (~10,000 characters across multiple paragraphs)
    sample_paragraph = (
        "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, "
        "and accessories, and sells a variety of related services. The Company's fiscal year is the 52- or 53-week period "
        "that ends on the last Saturday of September. Total net sales increased 2% or $7.5 billion during 2024 compared to 2023, "
        "driven by growth in Services and Mac, partially offset by lower net sales of iPad and Wearables, Home and Accessories. "
        "Services net sales increased 13% or $11.1 billion during 2024 compared to 2023, primarily due to higher net sales "
        "from advertising, cloud services, and App Store. Mac net sales increased 2% or $581 million during 2024 compared to 2023, "
        "primarily driven by higher net sales of MacBook Air powered by the M3 chip.\n\n"
        "Operating income for 2024 was $123.2 billion, representing an increase of 7.8% compared to $114.3 billion for 2023. "
        "Gross margin increased to $180.7 billion compared to $169.1 billion, driven by product cost savings and higher Services "
        "revenue mix. Operating expenses were $57.5 billion compared to $54.8 billion in 2023, reflecting increased research and "
        "development investments in artificial intelligence and machine learning technologies. Diluted earnings per share reached "
        "$6.08 for the fiscal year, an increase of 10% over the prior year figure of $5.53. The Company repurchased $95 billion "
        "of common stock and paid $15.2 billion in dividends to shareholders. Cash generated from operations totaled $118.3 billion.\n\n"
        "The Company continues to navigate dynamic macroeconomic environments, including foreign exchange fluctuations, inflation, "
        "and changing consumer spending patterns. International net sales accounted for 58% of total revenue in 2024, highlighting "
        "the Company's broad global footprint across Europe, Greater China, Japan, and Rest of Asia Pacific. Management remains "
        "confident in long-term platform investments, supply chain agility, and customer loyalty across all geographic operating segments."
    )
    long_document = "\n\n".join([sample_paragraph] * 5)

    chunks = splitter.split_text(long_document)
    assert len(chunks) >= 10

    # DoD 1: Zero chunks smaller than min_chunk_size (100)
    for i, c in enumerate(chunks):
        assert len(c) >= 100, f"Chunk {i} has length {len(c)} < 100"

    # DoD 2: >= 90% of chunks between 650 and 850 characters
    in_range = sum(1 for c in chunks if 650 <= len(c) <= 850)
    ratio = in_range / len(chunks)
    assert ratio >= 0.90, f"Only {in_range}/{len(chunks)} ({ratio*100:.1f}%) chunks in [650, 850]"


def test_fallback_character_split_unsplittable_text():
    """Verifies fallback character slicing when text contains no delimiters and exceeds target_chunk_size."""
    splitter = TextSplitter(target_chunk_size=200, min_chunk_size=50)
    unsplittable = "X" * 550
    chunks = splitter.split_text(unsplittable)
    assert len(chunks) == 3
    # 200 + 200 + 150 = 550
    assert len(chunks[0]) == 200
    assert len(chunks[1]) == 200
    assert len(chunks[2]) == 150
    assert "".join(chunks) == unsplittable


def test_invalid_init_parameters():
    """Verifies validation exceptions for illegal configuration values."""
    with pytest.raises(ValueError, match="target_chunk_size must be a positive integer"):
        TextSplitter(target_chunk_size=0)

    with pytest.raises(ValueError, match="target_chunk_size must be a positive integer"):
        TextSplitter(target_chunk_size=-500)

    with pytest.raises(ValueError, match="min_chunk_size cannot be negative"):
        TextSplitter(target_chunk_size=800, min_chunk_size=-10)

    with pytest.raises(ValueError, match="min_chunk_size cannot exceed target_chunk_size"):
        TextSplitter(target_chunk_size=500, min_chunk_size=600)


def test_custom_separators():
    """Verifies that custom separator sequences can be provided and utilized."""
    splitter = TextSplitter(target_chunk_size=80, min_chunk_size=20, separators=[" | ", " "])
    text = (
        "Segment A with financial revenue data | "
        "Segment B with detailed expenditure analysis | "
        "Segment C with operational margin calculations | "
        "Segment D with long-term forecasts"
    )
    chunks = splitter.split_text(text)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) >= 20
