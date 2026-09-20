"""Unit tests for PGVectorStore (Module 10.1).

Tests cover:
1. Input validation for store_embeddings (dimension mismatch, type errors, empty inputs).
2. Input validation for search_similar (dimension mismatch, top_k, type errors).
3. Input validation for delete_document (empty/invalid document_id).
4. Store embeddings ORM logic with mocked session.
5. Search similar query construction with mocked session.
6. Delete document with mocked session.
7. Chunk count with mocked session.
8. Error handling and PGVectorStorageError propagation.
"""

import uuid
from unittest.mock import MagicMock, patch, PropertyMock

import numpy as np
import pytest

from app.document_processing.metadata_tagger import TextChunkDTO
from app.rag.pgvector_store import PGVectorStore, PGVectorStorageError
from app.rag.retriever import RetrievedChunkDTO


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    """Returns a PGVectorStore instance with default 384 dimensions."""
    return PGVectorStore(dimension=384)


@pytest.fixture
def mock_session():
    """Returns a MagicMock SQLAlchemy session."""
    session = MagicMock()
    session.add_all = MagicMock()
    session.flush = MagicMock()
    session.execute = MagicMock()
    session.rollback = MagicMock()
    session.query = MagicMock()
    return session


@pytest.fixture
def sample_chunks():
    """Returns a list of 3 sample TextChunkDTO objects."""
    return [
        TextChunkDTO(
            chunk_id=str(uuid.uuid4()),
            document_id="doc-001",
            chunk_index=i,
            page_number=i + 1,
            content=f"Sample financial text chunk {i} with revenue data.",
            token_estimate=12,
            is_table_chunk=False,
        )
        for i in range(3)
    ]


@pytest.fixture
def sample_embeddings():
    """Returns a (3, 384) numpy array of normalized random embeddings."""
    rng = np.random.default_rng(42)
    raw = rng.standard_normal((3, 384)).astype(np.float32)
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    return raw / norms


# ---------------------------------------------------------------------------
# Constructor Tests
# ---------------------------------------------------------------------------

class TestPGVectorStoreInit:
    """Tests for PGVectorStore constructor validation."""

    def test_default_dimension(self):
        """Default dimension should be 384."""
        store = PGVectorStore()
        assert store.dimension == 384

    def test_custom_dimension(self):
        """Custom dimension should be accepted."""
        store = PGVectorStore(dimension=768)
        assert store.dimension == 768

    def test_zero_dimension_raises(self):
        """Dimension of 0 should raise ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            PGVectorStore(dimension=0)

    def test_negative_dimension_raises(self):
        """Negative dimension should raise ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            PGVectorStore(dimension=-1)

    def test_non_int_dimension_raises(self):
        """Non-integer dimension should raise ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            PGVectorStore(dimension=384.5)

    def test_string_dimension_raises(self):
        """String dimension should raise ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            PGVectorStore(dimension="384")


# ---------------------------------------------------------------------------
# store_embeddings Validation Tests
# ---------------------------------------------------------------------------

class TestStoreEmbeddingsValidation:
    """Tests for store_embeddings input validation."""

    def test_empty_document_id_raises(self, store, mock_session, sample_chunks, sample_embeddings):
        """Empty document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.store_embeddings(mock_session, "", sample_chunks, sample_embeddings)

    def test_none_document_id_raises(self, store, mock_session, sample_chunks, sample_embeddings):
        """None document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.store_embeddings(mock_session, None, sample_chunks, sample_embeddings)

    def test_int_document_id_raises(self, store, mock_session, sample_chunks, sample_embeddings):
        """Integer document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.store_embeddings(mock_session, 123, sample_chunks, sample_embeddings)

    def test_non_list_chunks_raises(self, store, mock_session, sample_embeddings):
        """Non-list chunks should raise TypeError."""
        with pytest.raises(TypeError, match="list of TextChunkDTO"):
            store.store_embeddings(mock_session, "doc-001", "not_a_list", sample_embeddings)

    def test_non_ndarray_embeddings_raises(self, store, mock_session, sample_chunks):
        """Non-ndarray embeddings should raise TypeError."""
        with pytest.raises(TypeError, match="numpy ndarray"):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, [[0.1] * 384])

    def test_1d_embeddings_raises(self, store, mock_session, sample_chunks):
        """1D embeddings array should raise ValueError."""
        vec = np.zeros(384, dtype=np.float32)
        with pytest.raises(ValueError, match="2D array"):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, vec)

    def test_dimension_mismatch_raises(self, store, mock_session, sample_chunks):
        """Embedding dimension mismatch should raise ValueError."""
        wrong_dim = np.zeros((3, 128), dtype=np.float32)
        with pytest.raises(ValueError, match="does not match store dimension"):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, wrong_dim)

    def test_count_mismatch_raises(self, store, mock_session, sample_chunks):
        """Mismatched chunk/embedding counts should raise ValueError."""
        wrong_count = np.zeros((5, 384), dtype=np.float32)
        with pytest.raises(ValueError, match="does not match number of chunks"):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, wrong_count)

    def test_non_chunk_dto_in_list_raises(self, store, mock_session, sample_embeddings):
        """Non-TextChunkDTO elements should raise TypeError."""
        bad_chunks = [{"chunk_id": "x"}, {"chunk_id": "y"}, {"chunk_id": "z"}]
        with pytest.raises(TypeError, match="expected TextChunkDTO"):
            store.store_embeddings(mock_session, "doc-001", bad_chunks, sample_embeddings)

    def test_empty_inputs_returns_zero(self, store, mock_session):
        """Empty chunks and embeddings should return 0."""
        result = store.store_embeddings(
            mock_session, "doc-001", [], np.empty((0, 384), dtype=np.float32)
        )
        assert result == 0


# ---------------------------------------------------------------------------
# store_embeddings Functional Tests
# ---------------------------------------------------------------------------

class TestStoreEmbeddingsFunctional:
    """Tests for store_embeddings ORM logic with mocked session."""

    def test_successful_store_returns_count(self, store, mock_session, sample_chunks, sample_embeddings):
        """Successful store should return the number of chunks inserted."""
        result = store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        assert result == 3

    def test_session_add_all_called(self, store, mock_session, sample_chunks, sample_embeddings):
        """Session add_all should be called with DocumentChunk objects."""
        store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        mock_session.add_all.assert_called_once()
        rows = mock_session.add_all.call_args[0][0]
        assert len(rows) == 3

    def test_session_flush_called(self, store, mock_session, sample_chunks, sample_embeddings):
        """Session flush should be called after add_all."""
        store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        mock_session.flush.assert_called_once()

    def test_row_data_integrity(self, store, mock_session, sample_chunks, sample_embeddings):
        """Inserted rows should preserve chunk metadata fields."""
        store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        rows = mock_session.add_all.call_args[0][0]
        for i, row in enumerate(rows):
            assert row.document_id == "doc-001"
            assert row.chunk_id == sample_chunks[i].chunk_id
            assert row.chunk_index == sample_chunks[i].chunk_index
            assert row.page_number == sample_chunks[i].page_number
            assert row.content == sample_chunks[i].content
            assert row.token_estimate == sample_chunks[i].token_estimate
            assert row.is_table_chunk == sample_chunks[i].is_table_chunk

    def test_embedding_stored_as_list(self, store, mock_session, sample_chunks, sample_embeddings):
        """Embedding should be stored as a Python list for pgvector."""
        store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        rows = mock_session.add_all.call_args[0][0]
        for i, row in enumerate(rows):
            assert isinstance(row.embedding, list)
            assert len(row.embedding) == 384
            np.testing.assert_allclose(row.embedding, sample_embeddings[i].tolist(), rtol=1e-5)

    def test_single_chunk_store(self, store, mock_session):
        """Storing a single chunk should work correctly."""
        chunk = TextChunkDTO(
            chunk_id=str(uuid.uuid4()),
            document_id="doc-single",
            chunk_index=0,
            page_number=1,
            content="Single chunk test.",
            token_estimate=4,
            is_table_chunk=False,
        )
        embedding = np.random.randn(1, 384).astype(np.float32)
        result = store.store_embeddings(mock_session, "doc-single", [chunk], embedding)
        assert result == 1

    def test_db_error_raises_pgvector_error(self, store, mock_session, sample_chunks, sample_embeddings):
        """Database errors should be wrapped in PGVectorStorageError."""
        mock_session.flush.side_effect = RuntimeError("Connection lost")
        with pytest.raises(PGVectorStorageError, match="Failed to store embeddings"):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)

    def test_db_error_triggers_rollback(self, store, mock_session, sample_chunks, sample_embeddings):
        """Database errors should trigger session rollback."""
        mock_session.flush.side_effect = RuntimeError("Connection lost")
        with pytest.raises(PGVectorStorageError):
            store.store_embeddings(mock_session, "doc-001", sample_chunks, sample_embeddings)
        mock_session.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# search_similar Validation Tests
# ---------------------------------------------------------------------------

class TestSearchSimilarValidation:
    """Tests for search_similar input validation."""

    def test_zero_top_k_raises(self, store, mock_session):
        """top_k of 0 should raise ValueError."""
        vec = np.zeros(384, dtype=np.float32)
        with pytest.raises(ValueError, match="positive integer"):
            store.search_similar(mock_session, vec, top_k=0)

    def test_negative_top_k_raises(self, store, mock_session):
        """Negative top_k should raise ValueError."""
        vec = np.zeros(384, dtype=np.float32)
        with pytest.raises(ValueError, match="positive integer"):
            store.search_similar(mock_session, vec, top_k=-1)

    def test_non_ndarray_raises(self, store, mock_session):
        """Non-ndarray query should raise TypeError."""
        with pytest.raises(TypeError, match="numpy ndarray"):
            store.search_similar(mock_session, [0.1] * 384)

    def test_dimension_mismatch_1d_raises(self, store, mock_session):
        """1D query with wrong dimension should raise ValueError."""
        vec = np.zeros(128, dtype=np.float32)
        with pytest.raises(ValueError, match="does not match"):
            store.search_similar(mock_session, vec)

    def test_dimension_mismatch_2d_raises(self, store, mock_session):
        """2D query with wrong dimension should raise ValueError."""
        vec = np.zeros((1, 128), dtype=np.float32)
        with pytest.raises(ValueError, match="does not match"):
            store.search_similar(mock_session, vec)

    def test_3d_query_raises(self, store, mock_session):
        """3D query array should raise ValueError."""
        vec = np.zeros((1, 1, 384), dtype=np.float32)
        with pytest.raises(ValueError, match="1D or 2D"):
            store.search_similar(mock_session, vec)


# ---------------------------------------------------------------------------
# search_similar Functional Tests
# ---------------------------------------------------------------------------

class TestSearchSimilarFunctional:
    """Tests for search_similar query logic with mocked session."""

    def test_search_returns_retrieved_chunk_dtos(self, store, mock_session):
        """Search should return a list of RetrievedChunkDTO objects."""
        # Mock result rows
        mock_row = MagicMock()
        mock_row.chunk_id = str(uuid.uuid4())
        mock_row.document_id = "doc-001"
        mock_row.chunk_index = 0
        mock_row.page_number = 1
        mock_row.content = "Revenue increased by 15%."
        mock_row.similarity_score = 0.92

        mock_session.execute.return_value = [mock_row]

        vec = np.random.randn(384).astype(np.float32)
        results = store.search_similar(mock_session, vec, top_k=5)

        assert len(results) == 1
        assert isinstance(results[0], RetrievedChunkDTO)
        assert results[0].chunk_id == mock_row.chunk_id
        assert results[0].similarity_score == 0.92

    def test_search_with_2d_query(self, store, mock_session):
        """2D query (1, 384) should be flattened and work correctly."""
        mock_session.execute.return_value = []
        vec = np.zeros((1, 384), dtype=np.float32)
        results = store.search_similar(mock_session, vec, top_k=3)
        assert results == []

    def test_search_empty_result(self, store, mock_session):
        """Empty result set should return empty list."""
        mock_session.execute.return_value = []
        vec = np.zeros(384, dtype=np.float32)
        results = store.search_similar(mock_session, vec)
        assert results == []

    def test_search_with_document_filter(self, store, mock_session):
        """Search with document_id filter should pass doc_id parameter."""
        mock_session.execute.return_value = []
        vec = np.zeros(384, dtype=np.float32)
        store.search_similar(mock_session, vec, top_k=5, document_id="doc-filtered")
        # Verify execute was called with doc_id parameter
        call_args = mock_session.execute.call_args
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})
        assert params.get("doc_id") == "doc-filtered"

    def test_search_without_document_filter(self, store, mock_session):
        """Search without document_id should not include doc_id parameter."""
        mock_session.execute.return_value = []
        vec = np.zeros(384, dtype=np.float32)
        store.search_similar(mock_session, vec, top_k=5)
        call_args = mock_session.execute.call_args
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})
        assert "doc_id" not in params

    def test_search_db_error_raises(self, store, mock_session):
        """Database errors during search should raise PGVectorStorageError."""
        mock_session.execute.side_effect = RuntimeError("Query timeout")
        vec = np.zeros(384, dtype=np.float32)
        with pytest.raises(PGVectorStorageError, match="search operation failed"):
            store.search_similar(mock_session, vec)


# ---------------------------------------------------------------------------
# delete_document Tests
# ---------------------------------------------------------------------------

class TestDeleteDocument:
    """Tests for delete_document validation and functionality."""

    def test_empty_document_id_raises(self, store, mock_session):
        """Empty document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.delete_document(mock_session, "")

    def test_none_document_id_raises(self, store, mock_session):
        """None document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.delete_document(mock_session, None)

    def test_int_document_id_raises(self, store, mock_session):
        """Integer document_id should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            store.delete_document(mock_session, 42)

    def test_delete_returns_rowcount(self, store, mock_session):
        """Delete should return the number of rows deleted."""
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result
        result = store.delete_document(mock_session, "doc-001")
        assert result == 5

    def test_delete_flushes_session(self, store, mock_session):
        """Delete should flush session after execute."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        store.delete_document(mock_session, "doc-001")
        mock_session.flush.assert_called_once()

    def test_delete_db_error_raises(self, store, mock_session):
        """Database errors during delete should raise PGVectorStorageError."""
        mock_session.execute.side_effect = RuntimeError("FK constraint")
        with pytest.raises(PGVectorStorageError, match="Failed to delete"):
            store.delete_document(mock_session, "doc-001")

    def test_delete_db_error_triggers_rollback(self, store, mock_session):
        """Database errors during delete should trigger session rollback."""
        mock_session.execute.side_effect = RuntimeError("FK constraint")
        with pytest.raises(PGVectorStorageError):
            store.delete_document(mock_session, "doc-001")
        mock_session.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# get_chunk_count Tests
# ---------------------------------------------------------------------------

class TestGetChunkCount:
    """Tests for get_chunk_count with mocked session."""

    def test_count_all_chunks(self, store, mock_session):
        """Count without document filter should query all chunks."""
        mock_query = MagicMock()
        mock_query.count.return_value = 150
        mock_session.query.return_value = mock_query
        result = store.get_chunk_count(mock_session)
        assert result == 150

    def test_count_with_document_filter(self, store, mock_session):
        """Count with document filter should apply WHERE clause."""
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_filtered.count.return_value = 25
        mock_query.filter.return_value = mock_filtered
        mock_session.query.return_value = mock_query
        result = store.get_chunk_count(mock_session, document_id="doc-001")
        assert result == 25

    def test_count_db_error_raises(self, store, mock_session):
        """Database errors during count should raise PGVectorStorageError."""
        mock_session.query.side_effect = RuntimeError("Connection pool exhausted")
        with pytest.raises(PGVectorStorageError, match="Failed to count"):
            store.get_chunk_count(mock_session)
