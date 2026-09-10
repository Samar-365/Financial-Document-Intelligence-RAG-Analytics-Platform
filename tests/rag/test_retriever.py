import time
import uuid
import numpy as np
import pytest

from app.document_processing.metadata_tagger import TextChunkDTO
from app.rag.embeddings import EmbeddingGenerator
from app.rag.faiss_store import FAISSVectorStore
from app.rag.retriever import VectorRetriever, RetrievedChunkDTO


def _create_chunk(document_id: str, index: int, content: str, page: int = 1) -> TextChunkDTO:
    """Helper to generate a TextChunkDTO."""
    return TextChunkDTO(
        chunk_id=str(uuid.uuid4()),
        document_id=document_id,
        chunk_index=index,
        page_number=page,
        content=content,
        token_estimate=len(content) // 4,
        is_table_chunk="|" in content,
    )


def _make_unit_vector(dimension: int = 384) -> np.ndarray:
    """Helper to generate a single 1D unit vector."""
    v = np.random.randn(dimension).astype(np.float32)
    return v / np.linalg.norm(v)


def test_retriever_initialization():
    """Verifies that VectorRetriever initializes correctly with default and custom thresholds."""
    store = FAISSVectorStore(dimension=384)
    retriever = VectorRetriever(store)
    assert retriever.vector_store is store
    assert retriever.min_similarity_threshold == 0.45

    custom_retriever = VectorRetriever(store, min_similarity_threshold=0.60)
    assert custom_retriever.min_similarity_threshold == 0.60


def test_invalid_initialization():
    """Verifies invalid parameter handling during VectorRetriever initialization."""
    store = FAISSVectorStore(dimension=384)

    with pytest.raises(TypeError, match="vector_store must be an instance of FAISSVectorStore"):
        VectorRetriever("not-a-store")

    with pytest.raises(ValueError, match="min_similarity_threshold must be between"):
        VectorRetriever(store, min_similarity_threshold=1.5)

    with pytest.raises(ValueError, match="min_similarity_threshold must be between"):
        VectorRetriever(store, min_similarity_threshold=-1.5)


def test_top_k_similarity_retrieval_and_ordering():
    """Verifies Task 1: Given a query vector, retrieves Top-K candidates in descending score order."""
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-topk"

    # Base query vector
    query_vector = _make_unit_vector(384)

    # Construct vectors with descending known cosine similarities
    # v = cos(theta) * query + sin(theta) * orthogonal
    ortho = np.random.randn(384).astype(np.float32)
    ortho -= np.dot(ortho, query_vector) * query_vector
    ortho /= np.linalg.norm(ortho)

    target_similarities = [0.95, 0.85, 0.70, 0.55, 0.50]
    chunks = []
    embeddings = []

    for i, sim in enumerate(target_similarities):
        theta = np.arccos(sim)
        v = (np.cos(theta) * query_vector + np.sin(theta) * ortho).astype(np.float32)
        v /= np.linalg.norm(v)
        embeddings.append(v)
        chunks.append(_create_chunk(doc_id, i, f"Financial statement chunk {i} with sim {sim:.2f}"))

    embeddings_matrix = np.vstack(embeddings)
    store.add_vectors(doc_id, embeddings_matrix, chunks)

    retriever = VectorRetriever(store, min_similarity_threshold=0.45)
    results = retriever.retrieve(doc_id, query_vector, top_k=3)

    assert len(results) == 3
    assert all(isinstance(r, RetrievedChunkDTO) for r in results)

    # Scores must be sorted descending
    scores = [r.similarity_score for r in results]
    assert scores == sorted(scores, reverse=True)
    assert np.isclose(scores[0], 0.95, atol=1e-2)
    assert np.isclose(scores[1], 0.85, atol=1e-2)
    assert np.isclose(scores[2], 0.70, atol=1e-2)


def test_confidence_threshold_filtering_dod():
    """Verifies Task 2 & Definition of Done (DoD):

    Chunks with cosine similarity score < 0.45 are discarded.
    """
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-thresh"

    query_vector = _make_unit_vector(384)
    ortho = np.random.randn(384).astype(np.float32)
    ortho -= np.dot(ortho, query_vector) * query_vector
    ortho /= np.linalg.norm(ortho)

    # 4 chunks: 2 above 0.45 (0.80, 0.50), 2 below 0.45 (0.35, 0.10)
    sims = [0.80, 0.50, 0.35, 0.10]
    chunks = []
    embeddings = []

    for i, sim in enumerate(sims):
        theta = np.arccos(sim)
        v = (np.cos(theta) * query_vector + np.sin(theta) * ortho).astype(np.float32)
        v /= np.linalg.norm(v)
        embeddings.append(v)
        chunks.append(_create_chunk(doc_id, i, f"Chunk {i} with sim {sim}"))

    store.add_vectors(doc_id, np.vstack(embeddings), chunks)

    retriever = VectorRetriever(store, min_similarity_threshold=0.45)
    # Request top_k=4, but only 2 chunks satisfy the threshold
    results = retriever.retrieve(doc_id, query_vector, top_k=4)

    assert len(results) == 2
    for r in results:
        assert r.similarity_score >= 0.45, f"Chunk score {r.similarity_score} < 0.45 threshold DoD"

    # Verify discarded chunks are not present
    retrieved_indices = [r.chunk_index for r in results]
    assert retrieved_indices == [0, 1]


def test_document_id_isolation():
    """Verifies document_id filtering isolates search to the requested document."""
    store = FAISSVectorStore(dimension=384)

    query_vector = _make_unit_vector(384)

    # Doc A has chunk with similarity 0.90
    doc_a_chunk = _create_chunk("doc-A", 0, "Doc A chunk")
    doc_a_vec = query_vector.reshape(1, -1)
    store.add_vectors("doc-A", doc_a_vec, [doc_a_chunk])

    # Doc B has chunk with similarity 0.90
    doc_b_chunk = _create_chunk("doc-B", 0, "Doc B chunk")
    doc_b_vec = query_vector.reshape(1, -1)
    store.add_vectors("doc-B", doc_b_vec, [doc_b_chunk])

    retriever = VectorRetriever(store, min_similarity_threshold=0.45)

    # Search only doc-A
    res_a = retriever.retrieve("doc-A", query_vector, top_k=5)
    assert len(res_a) == 1
    assert res_a[0].document_id == "doc-A"
    assert res_a[0].chunk_id == doc_a_chunk.chunk_id

    # Search only doc-B
    res_b = retriever.retrieve("doc-B", query_vector, top_k=5)
    assert len(res_b) == 1
    assert res_b[0].document_id == "doc-B"
    assert res_b[0].chunk_id == doc_b_chunk.chunk_id

    # Search all (document_id=None or "*")
    res_all = retriever.retrieve(None, query_vector, top_k=5)
    assert len(res_all) == 2


def test_empty_store_and_no_matches():
    """Verifies that an empty store or zero matches above threshold return empty lists."""
    store = FAISSVectorStore(dimension=384)
    retriever = VectorRetriever(store, min_similarity_threshold=0.45)

    query = _make_unit_vector(384)
    assert retriever.retrieve("doc-x", query, top_k=5) == []

    # Add chunk with very low similarity (~0.1)
    ortho = np.random.randn(384).astype(np.float32)
    ortho -= np.dot(ortho, query) * query
    ortho /= np.linalg.norm(ortho)
    theta = np.arccos(0.10)
    low_sim_vec = (np.cos(theta) * query + np.sin(theta) * ortho).reshape(1, -1)

    store.add_vectors("doc-low", low_sim_vec, [_create_chunk("doc-low", 0, "Unrelated text")])
    assert retriever.retrieve("doc-low", query, top_k=5) == []


def test_sub_20ms_latency_dod():
    """Verifies Definition of Done (DoD):

    Sub-20ms search response time across indexed corpus.
    """
    store = FAISSVectorStore(dimension=384)
    doc_id = "doc-bench"

    # Index 200 chunks
    raw_vecs = np.random.randn(200, 384).astype(np.float32)
    norms = np.linalg.norm(raw_vecs, axis=1, keepdims=True)
    embeddings = raw_vecs / norms
    chunks = [_create_chunk(doc_id, i, f"Corpus text chunk index {i}") for i in range(200)]

    store.add_vectors(doc_id, embeddings, chunks)
    retriever = VectorRetriever(store, min_similarity_threshold=0.0)

    query = _make_unit_vector(384)

    # Warm-up search
    retriever.retrieve(doc_id, query, top_k=5)

    # Benchmark search latency
    start = time.perf_counter()
    results = retriever.retrieve(doc_id, query, top_k=5)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert len(results) == 5
    assert elapsed_ms < 20.0, f"Search latency {elapsed_ms:.2f}ms exceeded 20ms DoD threshold"


def test_validation_errors():
    """Verifies strict input parameter validation."""
    store = FAISSVectorStore(dimension=384)
    retriever = VectorRetriever(store)
    query = _make_unit_vector(384)

    # Invalid top_k
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        retriever.retrieve("doc-1", query, top_k=0)

    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        retriever.retrieve("doc-1", query, top_k=-5)

    # Non-numpy query
    with pytest.raises(TypeError, match="query_vector must be a numpy ndarray"):
        retriever.retrieve("doc-1", [1.0, 2.0], top_k=5)

    # Wrong dimension (128 instead of 384)
    wrong_dim = np.random.randn(1, 128).astype(np.float32)
    with pytest.raises(ValueError, match="Query vector dimension 128 does not match index dimension 384"):
        retriever.retrieve("doc-1", wrong_dim, top_k=5)


def test_end_to_end_rag_retrieval():
    """Verifies complete integration: text -> EmbeddingGenerator -> FAISSVectorStore -> VectorRetriever."""
    generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", device="cpu", batch_size=32)
    store = FAISSVectorStore(dimension=generator.dimension)
    retriever = VectorRetriever(store, min_similarity_threshold=0.45)

    texts = [
        "Cloud software annual recurring revenue (ARR) grew 34% to $2.8 billion in FY25.",
        "Operating lease commitments for server hardware total $120 million through 2028.",
        "The company experienced zero material cybersecurity breaches during the audit cycle.",
    ]
    doc_id = "doc-fy25-annual"
    chunks = [_create_chunk(doc_id, i, t, page=i + 1) for i, t in enumerate(texts)]

    embeddings = generator.generate_embeddings(texts)
    store.add_vectors(doc_id, embeddings, chunks)

    # Semantic query
    query_text = ["What is the annual recurring revenue for cloud software?"]
    query_vec = generator.generate_embeddings(query_text)

    results = retriever.retrieve(doc_id, query_vec, top_k=3)

    assert len(results) >= 1
    top = results[0]
    assert top.chunk_index == 0
    assert "Cloud software annual recurring revenue" in top.content
    assert top.similarity_score >= 0.45
    assert top.page_number == 1
    assert top.document_id == doc_id
