"""In-Memory FAISS Vector Index (Module 3.2).

Responsible for:
1. Constructing and managing an in-memory FAISS IndexFlatIP (Inner Product) index.
2. Adding dense embeddings and associating them with chunk metadata.
3. Building and maintaining an ID mapping dictionary linking integer indices to chunk DTOs.
"""

from typing import Dict, List, Optional, Tuple
import faiss
import numpy as np

from app.document_processing.metadata_tagger import TextChunkDTO


class VectorStorageError(Exception):
    """Raised when vector indexing or storage fails (PROC_004)."""

    def __init__(
        self,
        message: str = "PROC_004: Document processing encountered an error during indexing.",
        error_code: str = "PROC_004",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class FAISSVectorStore:
    """In-memory FAISS vector index using IndexFlatIP for cosine similarity retrieval.

    Technical Tasks:
    1. Index Construction: Initialize FAISS IndexFlatIP with 384 dimensions and add
       normalized chunk embeddings.
    2. ID Mapping Dictionary: Build an in-memory dictionary mapping FAISS integer indices
       (0, 1, 2...) to chunk UUIDs and metadata for lookup.
    """

    def __init__(self, dimension: int = 384):
        """Initializes the FAISS vector store with the given embedding dimensionality.

        Args:
            dimension: Dimensionality of embedding vectors (default 384 for all-MiniLM-L6-v2).

        Raises:
            ValueError: If dimension is less than or equal to 0.
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("dimension must be a positive integer.")

        self._dimension = dimension
        try:
            self._index = faiss.IndexFlatIP(self._dimension)
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: Failed to initialize FAISS IndexFlatIP: {e}"
            ) from e

        # In-memory mapping stores
        self._index_to_chunk: Dict[int, TextChunkDTO] = {}
        self._chunk_id_to_index: Dict[str, int] = {}
        self._doc_to_indices: Dict[str, List[int]] = {}

    @property
    def dimension(self) -> int:
        """Returns the vector dimensionality configured for this index."""
        return self._dimension

    @property
    def total_vectors(self) -> int:
        """Returns the total number of vectors stored in the FAISS index."""
        return self._index.ntotal

    def __len__(self) -> int:
        """Returns total vectors stored."""
        return self.total_vectors

    def add_vectors(
        self,
        document_id: str,
        embeddings: np.ndarray,
        chunks: List[TextChunkDTO],
    ) -> int:
        """Populates FAISS index and stores chunk metadata mappings.

        Args:
            document_id: Unique identifier for the parent document.
            embeddings: 2D numpy array of shape (N, dimension) containing float32 vectors.
            chunks: List of TextChunkDTO metadata objects matching the embeddings.

        Returns:
            int: Number of vectors added in this operation.

        Raises:
            ValueError: If inputs are invalid or dimensions/counts mismatch.
            TypeError: If input types are incorrect.
            VectorStorageError: If FAISS fails during vector addition.
        """
        if not document_id or not isinstance(document_id, str):
            raise ValueError("document_id must be a non-empty string.")

        if not isinstance(chunks, list):
            raise TypeError("chunks must be a list of TextChunkDTO instances.")

        if not isinstance(embeddings, np.ndarray):
            raise TypeError("embeddings must be a numpy ndarray.")

        # Handle empty addition
        if len(chunks) == 0 and embeddings.size == 0:
            return 0

        if embeddings.ndim != 2:
            raise ValueError(
                f"embeddings must be a 2D array, got ndim={embeddings.ndim}."
            )

        num_vectors, vector_dim = embeddings.shape
        if vector_dim != self._dimension:
            raise ValueError(
                f"Embedding dimension {vector_dim} does not match index dimension {self._dimension}."
            )

        if num_vectors != len(chunks):
            raise ValueError(
                f"Number of embeddings ({num_vectors}) does not match number of chunks ({len(chunks)})."
            )

        for i, chunk in enumerate(chunks):
            if not isinstance(chunk, TextChunkDTO):
                raise TypeError(
                    f"Element at index {i} in chunks is {type(chunk).__name__}, expected TextChunkDTO."
                )

        try:
            # Ensure contiguous float32 for FAISS
            contiguous_embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
            start_index = self._index.ntotal

            # Task 1: Add vectors to FAISS IndexFlatIP
            self._index.add(contiguous_embeddings)

            # Task 2: Build in-memory ID mapping dictionaries
            if document_id not in self._doc_to_indices:
                self._doc_to_indices[document_id] = []

            for i, chunk in enumerate(chunks):
                current_idx = start_index + i
                self._index_to_chunk[current_idx] = chunk
                self._chunk_id_to_index[chunk.chunk_id] = current_idx
                self._doc_to_indices[document_id].append(current_idx)

            return num_vectors
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise VectorStorageError(
                f"PROC_004: Failed to add vectors to FAISS index: {e}"
            ) from e

    def get_chunk_by_index(self, index: int) -> Optional[TextChunkDTO]:
        """Retrieves chunk metadata by FAISS integer index.

        Args:
            index: Sequential integer index in FAISS (0, 1, 2...).

        Returns:
            Optional[TextChunkDTO]: Chunk metadata DTO or None if not found.
        """
        return self._index_to_chunk.get(index)

    def get_chunk_by_id(self, chunk_id: str) -> Optional[TextChunkDTO]:
        """Retrieves chunk metadata by chunk UUID.

        Args:
            chunk_id: String UUID of the chunk.

        Returns:
            Optional[TextChunkDTO]: Chunk metadata DTO or None if not found.
        """
        index = self._chunk_id_to_index.get(chunk_id)
        if index is not None:
            return self._index_to_chunk.get(index)
        return None

    def get_chunks_by_document(self, document_id: str) -> List[TextChunkDTO]:
        """Retrieves all chunks associated with a specific document ID.

        Args:
            document_id: Identifier of the document.

        Returns:
            List[TextChunkDTO]: List of chunk DTOs in sequential order.
        """
        indices = self._doc_to_indices.get(document_id, [])
        return [self._index_to_chunk[idx] for idx in indices if idx in self._index_to_chunk]

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Performs inner product (cosine similarity) nearest neighbor search.

        Args:
            query_vector: 2D numpy array of shape (1, dimension) or (num_queries, dimension).
            top_k: Number of nearest neighbors to retrieve.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (scores, indices) arrays of shape (num_queries, top_k).

        Raises:
            ValueError: If query vector dimensions mismatch or top_k <= 0.
            VectorStorageError: If search execution fails.
        """
        if top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        if not isinstance(query_vector, np.ndarray):
            raise TypeError("query_vector must be a numpy ndarray.")

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        if query_vector.shape[1] != self._dimension:
            raise ValueError(
                f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self._dimension}."
            )

        if self.total_vectors == 0:
            empty_scores = np.empty((query_vector.shape[0], 0), dtype=np.float32)
            empty_indices = np.empty((query_vector.shape[0], 0), dtype=np.int64)
            return empty_scores, empty_indices

        actual_k = min(top_k, self.total_vectors)
        try:
            contiguous_query = np.ascontiguousarray(query_vector, dtype=np.float32)
            scores, indices = self._index.search(contiguous_query, actual_k)
            return scores, indices
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: FAISS search operation failed: {e}"
            ) from e

    def reset(self) -> None:
        """Resets the FAISS index and clears all in-memory metadata mappings."""
        try:
            self._index.reset()
            self._index_to_chunk.clear()
            self._chunk_id_to_index.clear()
            self._doc_to_indices.clear()
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: Failed to reset FAISS index: {e}"
            ) from e
