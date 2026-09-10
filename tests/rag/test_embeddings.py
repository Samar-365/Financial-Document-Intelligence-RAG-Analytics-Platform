import time
import numpy as np
import pytest
from app.rag.embeddings import EmbeddingGenerator, EmbeddingError


@pytest.fixture(scope="module")
def generator():
    """Module-scoped fixture to share loaded model instance across tests."""
    return EmbeddingGenerator(model_name="all-MiniLM-L6-v2", device="cpu", batch_size=32)


def test_generator_initialization_and_properties(generator):
    """Verifies that the EmbeddingGenerator initializes with correct defaults and properties."""
    assert generator.dimension == 384
    assert generator.model_name == "all-MiniLM-L6-v2"
    assert generator.device == "cpu"
    assert generator.batch_size == 32


def test_invalid_initialization_parameters():
    """Verifies that invalid initialization parameters raise appropriate exceptions."""
    with pytest.raises(ValueError, match="model_name must be a non-empty string"):
        EmbeddingGenerator(model_name="")

    with pytest.raises(ValueError, match="batch_size must be a positive integer"):
        EmbeddingGenerator(batch_size=0)

    with pytest.raises(ValueError, match="batch_size must be a positive integer"):
        EmbeddingGenerator(batch_size=-5)

    with pytest.raises(EmbeddingError, match="PROC_003"):
        EmbeddingGenerator(model_name="non-existent-dummy-model-xyz-12345")


def test_empty_input(generator):
    """Verifies that an empty input list returns a (0, 384) numpy array."""
    embeddings = generator.generate_embeddings([])
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (0, 384)
    assert embeddings.dtype == np.float32


def test_single_text_embedding(generator):
    """Verifies that a single text input returns an array of shape (1, 384)."""
    text = ["Net revenue for fiscal year 2025 totaled $12.4 billion, up 18% year-over-year."]
    embeddings = generator.generate_embeddings(text)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (1, 384)
    assert embeddings.dtype == np.float32


def test_batch_texts_embedding(generator):
    """Verifies batch inference returns correct shape (N, 384)."""
    texts = [
        "Operating income expanded to $3.2B with an operating margin of 25.8%.",
        "Cash and cash equivalents stood at $4.5B at the end of the second quarter.",
        "Operating cash flows were driven by sustained customer adoption and enterprise renewals.",
        "The board of directors declared a quarterly dividend of $0.25 per share.",
    ]
    embeddings = generator.generate_embeddings(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (4, 384)
    assert embeddings.dtype == np.float32


def test_l2_unit_normalization_dod(generator):
    """Verifies the Definition of Done (DoD):

    Every output vector has Euclidean norm equal to 1.0 (+- 1e-5).
    """
    sample_texts = [
        "Consolidated Financial Statements for the fiscal year ended December 31, 2025.",
        "Diluted earnings per share (EPS) was $4.12 compared to $3.50 in the prior year.",
        "Capital expenditures for cloud infrastructure totaled $850 million.",
        "Research and development investments represented 14% of gross revenue.",
        "Short-term borrowings decreased following debt repurchases in Q3.",
        "Risk factors include foreign currency exchange rate fluctuations.",
        "Segment report: North America segment grew 12%, EMEA grew 15%.",
        "Income tax expense was recognized at an effective tax rate of 21.5%.",
    ]

    embeddings = generator.generate_embeddings(sample_texts)

    # Compute Euclidean norms (L2) for all rows
    norms = np.linalg.norm(embeddings, ord=2, axis=1)

    for i, norm in enumerate(norms):
        assert abs(norm - 1.0) <= 1e-5, f"Vector at index {i} failed unit norm DoD: norm={norm}"


def test_dot_product_equals_cosine_similarity(generator):
    """Verifies that because vectors are L2-normalized, the dot product is exactly cosine similarity."""
    texts = [
        "SaaS annualized recurring revenue (ARR) exceeded $2.1 billion.",
        "Subscription revenue grew substantially over the fiscal period.",
    ]
    embeddings = generator.generate_embeddings(texts)
    vec1, vec2 = embeddings[0], embeddings[1]

    # Compute dot product
    dot_product = float(np.dot(vec1, vec2))

    # Compute cosine similarity manually: (u . v) / (||u|| * ||v||)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    cosine_sim = float(np.dot(vec1, vec2) / (norm1 * norm2))

    assert np.isclose(dot_product, cosine_sim, atol=1e-5)


def test_semantic_similarity_ranking(generator):
    """Verifies that semantically related financial statements have higher dot products than unrelated ones."""
    query = ["Cloud software recurring revenue increased 25%."]
    relevant = ["Subscription and cloud services ARR grew 25% year-over-year."]
    irrelevant = ["The corporate cafeteria was closed on bank holidays."]

    query_emb = generator.generate_embeddings(query)[0]
    relevant_emb = generator.generate_embeddings(relevant)[0]
    irrelevant_emb = generator.generate_embeddings(irrelevant)[0]

    similarity_relevant = float(np.dot(query_emb, relevant_emb))
    similarity_irrelevant = float(np.dot(query_emb, irrelevant_emb))

    assert similarity_relevant > similarity_irrelevant
    assert similarity_relevant > 0.6  # High semantic correlation
    assert similarity_irrelevant < 0.4  # Low semantic correlation


def test_multibatch_boundary_processing(generator):
    """Verifies that chunk lists exceeding a single batch_size (32) are accurately processed."""
    # 75 chunks spanning 3 batches (32 + 32 + 11)
    texts = [f"Financial disclosure statement section {i} for financial audit compliance." for i in range(75)]
    embeddings = generator.generate_embeddings(texts)

    assert embeddings.shape == (75, 384)
    norms = np.linalg.norm(embeddings, ord=2, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-5)


def test_input_validation_errors(generator):
    """Verifies error handling for invalid input types."""
    with pytest.raises(TypeError, match="texts must be a list of strings"):
        generator.generate_embeddings("single string instead of list")

    with pytest.raises(TypeError, match="texts must be a list of strings"):
        generator.generate_embeddings(12345)

    with pytest.raises(TypeError, match="All elements in texts must be strings"):
        generator.generate_embeddings(["valid string", 999, "another valid string"])

    with pytest.raises(TypeError, match="All elements in texts must be strings"):
        generator.generate_embeddings([None])


def test_throughput_benchmark(generator):
    """Verifies throughput on standard CPU for batch embeddings."""
    texts = [
        f"Quarterly report chunk {i}: Operating revenue was ${100 + i}.5 million with EBITDA margin of 22%."
        for i in range(100)
    ]
    start_time = time.perf_counter()
    embeddings = generator.generate_embeddings(texts)
    elapsed = time.perf_counter() - start_time

    assert embeddings.shape == (100, 384)
    # 100 chunks should comfortably complete in well under 2 seconds on CPU
    assert elapsed < 3.0, f"Embedding 100 chunks took {elapsed:.2f}s, expected < 3.0s"
