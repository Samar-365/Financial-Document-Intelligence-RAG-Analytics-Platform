import uuid
import numpy as np
import pytest

from app.document_processing.metadata_tagger import TextChunkDTO
from app.rag.embeddings import EmbeddingGenerator
from app.rag.faiss_store import FAISSVectorStore, VectorStorageError


def _create_sample_chunk(document_id: str, index: int, content: str, page: int = 1) -> TextChunkDTO:
    """Helper to generate a TextChunkDTO instance."""
    return TextChunkDTO(
        chunk_id=str(uuid.uuid4()),
        document_id=document_id,
        chunk_index=index,
        page_number=page,
        content=content,
        token_estimate=len(content) // 4,
        is_table_chunk="|" in content,
    )


def _generate_normalized_vectors(count: int, dimension: int = 384) -> np.ndarray:
    """Helper to generate mock unit-normalized random vectors."""
    raw = np.random.randn(count, dimension).astype(np.float32)
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    return raw / norms


def test_store_initialization_defaults_and_properties():
    """Verifies that FAISSVectorStore initializes with correct default dimension and empty state."""
    store = FAISSVectorStore()
    assert store.dimension == 384
    assert store.total_vectors == 0
    assert len(store) == 0

    custom_store = FAISSVectorStore(dimension=128)
    assert custom_store.dimension == 128
    assert custom_store.total_vectors == 0


def test_invalid_initialization():
    """Verifies that non-positive dimensions raise ValueError."""
    with pytest.raises(ValueError, match="dimension must be a positive integer"):
        FAISSVectorStore(dimension=0)

    with pytest.raises(ValueError, match="dimension must be a positive integer"):
        FAISSVectorStore(dimension=-384)


def test_empty_vector_addition():
    """Verifies that adding zero chunks or empty embeddings returns 0 and does not error."""
    store = FAISSVectorStore(dimension=384)
    empty_embeddings = np.empty((0, 384), dtype=np.float32)
    added = store.add_vectors("doc-empty", empty_embeddings, [])
    assert added == 0
    assert store.total_vectors == 0


def test_add_vectors_and_id_mapping_dod():
    """Verifies the Definition of Done (DoD):

    FAISS index initializes, adds vectors, and retrieves correct metadata by integer index.
    """
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-fy2025-10k"
    chunks = [
        _create_sample_chunk(doc_id, 0, "Consolidated statement of operations for FY2025.", page=1),
        _create_sample_chunk(doc_id, 1, "Operating income was $4.2B, a 22% increase.", page=2),
        _create_sample_chunk(doc_id, 2, "Cash and cash equivalents totaled $6.8B.", page=2),
    ]
    embeddings = _generate_normalized_vectors(3, dimension=384)

    added = store.add_vectors(doc_id, embeddings, chunks)
    assert added == 3
    assert store.total_vectors == 3
    assert len(store) == 3

    # Verify ID mapping lookup by FAISS integer index (DoD)
    for i, expected_chunk in enumerate(chunks):
        retrieved = store.get_chunk_by_index(i)
        assert retrieved is not None
        assert retrieved.chunk_id == expected_chunk.chunk_id
        assert retrieved.document_id == doc_id
        assert retrieved.chunk_index == i
        assert retrieved.content == expected_chunk.content
        assert retrieved.page_number == expected_chunk.page_number

    # Out of range integer index
    assert store.get_chunk_by_index(99) is None
    assert store.get_chunk_by_index(-1) is None


def test_lookup_by_chunk_id_and_document():
    """Verifies chunk retrieval by UUID and document-level chunk aggregation."""
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-q3-results"
    chunk1 = _create_sample_chunk(doc_id, 0, "Total quarterly revenues: $1.2B.")
    chunk2 = _create_sample_chunk(doc_id, 1, "Cloud segment ARR expansion rate: 128%.")
    embeddings = _generate_normalized_vectors(2, dimension=384)

    store.add_vectors(doc_id, embeddings, [chunk1, chunk2])

    # Lookup by chunk_id
    res1 = store.get_chunk_by_id(chunk1.chunk_id)
    assert res1 is not None
    assert res1.content == chunk1.content

    res2 = store.get_chunk_by_id(chunk2.chunk_id)
    assert res2 is not None
    assert res2.content == chunk2.content

    assert store.get_chunk_by_id("non-existent-uuid") is None

    # Lookup by document_id
    doc_chunks = store.get_chunks_by_document(doc_id)
    assert len(doc_chunks) == 2
    assert [c.chunk_id for c in doc_chunks] == [chunk1.chunk_id, chunk2.chunk_id]
    assert store.get_chunks_by_document("non-existent-doc") == []


def test_multi_document_incremental_additions():
    """Verifies that adding chunks across multiple documents assigns monotonic sequential indices."""
    store = FAISSVectorStore(dimension=384)

    doc1_chunks = [_create_sample_chunk("doc-1", i, f"Doc 1 chunk {i}") for i in range(3)]
    doc1_vecs = _generate_normalized_vectors(3, 384)
    store.add_vectors("doc-1", doc1_vecs, doc1_chunks)

    doc2_chunks = [_create_sample_chunk("doc-2", i, f"Doc 2 chunk {i}") for i in range(2)]
    doc2_vecs = _generate_normalized_vectors(2, 384)
    store.add_vectors("doc-2", doc2_vecs, doc2_chunks)

    assert store.total_vectors == 5

    # Indices 0..2 should map to doc 1
    for i in range(3):
        chunk = store.get_chunk_by_index(i)
        assert chunk.document_id == "doc-1"
        assert chunk.chunk_id == doc1_chunks[i].chunk_id

    # Indices 3..4 should map to doc 2
    for i in range(2):
        chunk = store.get_chunk_by_index(3 + i)
        assert chunk.document_id == "doc-2"
        assert chunk.chunk_id == doc2_chunks[i].chunk_id


def test_vector_search_exact_match():
    """Verifies that searching with an identical vector returns the exact match with similarity ~1.0."""
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-search-test"
    chunks = [
        _create_sample_chunk(doc_id, 0, "Chunk A"),
        _create_sample_chunk(doc_id, 1, "Chunk B"),
        _create_sample_chunk(doc_id, 2, "Chunk C"),
    ]
    embeddings = _generate_normalized_vectors(3, 384)
    store.add_vectors(doc_id, embeddings, chunks)

    # Query with the exact vector of Chunk B (index 1)
    query_vector = embeddings[1:2]  # shape (1, 384)
    scores, indices = store.search(query_vector, top_k=2)

    assert scores.shape == (1, 2)
    assert indices.shape == (1, 2)
    # The top result must be index 1 with dot product ~ 1.0
    assert indices[0][0] == 1
    assert np.isclose(scores[0][0], 1.0, atol=1e-5)

    # Verify matching chunk
    top_chunk = store.get_chunk_by_index(int(indices[0][0]))
    assert top_chunk.chunk_id == chunks[1].chunk_id


def test_search_empty_store():
    """Verifies that searching on an empty index returns empty results without raising errors."""
    store = FAISSVectorStore(dimension=384)
    query_vector = _generate_normalized_vectors(1, 384)
    scores, indices = store.search(query_vector, top_k=5)

    assert scores.shape == (1, 0)
    assert indices.shape == (1, 0)


def test_validation_errors():
    """Verifies strict input validation across methods."""
    store = FAISSVectorStore(dimension=384)
    chunks = [_create_sample_chunk("doc-err", 0, "Valid chunk")]
    embeddings = _generate_normalized_vectors(1, 384)

    # Empty document_id
    with pytest.raises(ValueError, match="document_id must be a non-empty string"):
        store.add_vectors("", embeddings, chunks)

    # Non-list chunks
    with pytest.raises(TypeError, match="chunks must be a list"):
        store.add_vectors("doc", embeddings, "not a list")

    # Non-numpy embeddings
    with pytest.raises(TypeError, match="embeddings must be a numpy ndarray"):
        store.add_vectors("doc", [1, 2, 3], chunks)

    # Mismatched length: 1 embedding vs 2 chunks
    with pytest.raises(ValueError, match="Number of embeddings"):
        store.add_vectors("doc", embeddings, [chunks[0], chunks[0]])

    # Wrong vector dimension: 128 vs 384
    wrong_dim_embeddings = _generate_normalized_vectors(1, 128)
    with pytest.raises(ValueError, match="Embedding dimension 128 does not match index dimension 384"):
        store.add_vectors("doc", wrong_dim_embeddings, chunks)

    # Search invalid dimension
    with pytest.raises(ValueError, match="Query vector dimension 128 does not match index dimension 384"):
        store.search(wrong_dim_embeddings, top_k=5)

    # Search invalid top_k
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        store.search(embeddings, top_k=0)


def test_reset():
    """Verifies that reset clears the FAISS index and all ID mappings."""
    store = FAISSVectorStore(dimension=384)
    chunks = [_create_sample_chunk("doc-reset", i, f"Chunk {i}") for i in range(3)]
    embeddings = _generate_normalized_vectors(3, 384)
    store.add_vectors("doc-reset", embeddings, chunks)

    assert store.total_vectors == 3
    store.reset()

    assert store.total_vectors == 0
    assert len(store) == 0
    assert store.get_chunk_by_index(0) is None
    assert store.get_chunk_by_id(chunks[0].chunk_id) is None
    assert store.get_chunks_by_document("doc-reset") == []


def test_integration_with_embedding_generator():
    """Verifies end-to-end integration: EmbeddingGenerator produces vectors and FAISSVectorStore indexes and searches them."""
    generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", device="cpu", batch_size=32)
    store = FAISSVectorStore(dimension=generator.dimension)

    texts = [
        "Annual software license recurring revenue increased by 35% in fiscal 2025.",
        "Total commercial real estate lease liabilities were $450 million.",
        "The committee approved a share repurchase authorization of $2 billion.",
    ]
    chunks = [_create_sample_chunk("doc-finance", i, text, page=i + 1) for i, text in enumerate(texts)]

    embeddings = generator.generate_embeddings(texts)
    store.add_vectors("doc-finance", embeddings, chunks)
    assert store.total_vectors == 3

    # Query with a semantic variant of the software revenue chunk
    query_text = ["Cloud and subscription revenue growth rate"]
    query_vector = generator.generate_embeddings(query_text)

    scores, indices = store.search(query_vector, top_k=1)
    best_index = int(indices[0][0])
    best_chunk = store.get_chunk_by_index(best_index)

    assert best_chunk is not None
    assert best_chunk.chunk_index == 0
    assert "recurring revenue" in best_chunk.content
    assert scores[0][0] > 0.45  # High semantic correlation
