"""Vector Similarity Retriever for RAG pipeline (Module 3.3).

Responsible for:
1. Top-K similarity retrieval against indexed FAISS vector embeddings.
2. Filtering out chunks with cosine similarity below confidence threshold (< 0.45).
3. Packaging retrieved candidate contexts into RetrievedChunkDTO models.
"""

from typing import List, Optional
import numpy as np
from pydantic import BaseModel, Field

from app.rag.faiss_store import FAISSVectorStore, VectorStorageError


class RetrievedChunkDTO(BaseModel):
    """Data Transfer Object representing a retrieved document chunk with similarity ranking."""

    chunk_id: str = Field(
        ...,
        description="Unique UUID identifying the retrieved text chunk.",
    )
    document_id: str = Field(
        ...,
        description="Identifier of the originating document.",
    )
    chunk_index: int = Field(
        ...,
        ge=0,
        description="0-based sequential chunk index within the document.",
    )
    page_number: int = Field(
        ...,
        ge=1,
        description="Originating PDF page number.",
    )
    content: str = Field(
        ...,
        description="Text content of the retrieved chunk.",
    )
    similarity_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Cosine similarity score between query vector and chunk embedding.",
    )


class VectorRetriever:
    """Retrieves top-scoring contextual chunks from FAISSVectorStore with threshold filtering.

    Technical Tasks:
    1. Top-K Similarity Retrieval: Given a 384-dim query vector, executes index search
       to retrieve Top-K nearest chunk candidates.
    2. Confidence Threshold Filtering: Filters out chunks with cosine similarity score
       below min_similarity_threshold (< 0.45 by default).
    """

    def __init__(
        self,
        vector_store: FAISSVectorStore,
        min_similarity_threshold: float = 0.45,
    ):
        """Initializes VectorRetriever.

        Args:
            vector_store: FAISSVectorStore instance containing indexed chunks.
            min_similarity_threshold: Minimum cosine similarity required to retain a chunk (default 0.45).

        Raises:
            TypeError: If vector_store is not an instance of FAISSVectorStore.
            ValueError: If min_similarity_threshold is not between -1.0 and 1.0.
        """
        if not isinstance(vector_store, FAISSVectorStore):
            raise TypeError("vector_store must be an instance of FAISSVectorStore.")

        if not (-1.0 <= min_similarity_threshold <= 1.0):
            raise ValueError("min_similarity_threshold must be between -1.0 and 1.0.")

        self.vector_store = vector_store
        self.min_similarity_threshold = min_similarity_threshold

    def retrieve(
        self,
        document_id: Optional[str],
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> List[RetrievedChunkDTO]:
        """Retrieves Top-K chunks filtered by similarity threshold and document ID.

        Args:
            document_id: Target document identifier to filter on. If None or empty or "*",
                         retrieval searches across all documents.
            query_vector: 1D or 2D numpy array containing 384-dimensional query embedding.
            top_k: Maximum number of relevant candidates to return (defaults to 5).

        Returns:
            List[RetrievedChunkDTO]: List of candidate chunks sorted by descending similarity score.

        Raises:
            ValueError: If top_k <= 0 or query_vector dimension mismatches store.
            TypeError: If query_vector is not a numpy ndarray.
        """
        if top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        if not isinstance(query_vector, np.ndarray):
            raise TypeError("query_vector must be a numpy ndarray.")

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        if query_vector.shape[1] != self.vector_store.dimension:
            raise ValueError(
                f"Query vector dimension {query_vector.shape[1]} does not match "
                f"index dimension {self.vector_store.dimension}."
            )

        if self.vector_store.total_vectors == 0:
            return []

        # Candidate search pool: search for enough candidates to satisfy top_k after filtering
        search_k = min(self.vector_store.total_vectors, max(top_k * 4, 20))
        scores, indices = self.vector_store.search(query_vector, top_k=search_k)

        if scores.size == 0 or indices.size == 0:
            return []

        query_scores = scores[0]
        query_indices = indices[0]

        filtered_results: List[RetrievedChunkDTO] = []
        filter_doc = bool(document_id and document_id != "*")

        for score, idx in zip(query_scores, query_indices):
            if idx < 0:
                continue

            raw_score = float(score)
            # Task 2: Confidence Threshold Filtering (< min_similarity_threshold discarded)
            if raw_score < self.min_similarity_threshold:
                continue

            chunk = self.vector_store.get_chunk_by_index(int(idx))
            if chunk is None:
                continue

            # Optional document_id isolation
            if filter_doc and chunk.document_id != document_id:
                continue

            # Clamp score defensively to [-1.0, 1.0]
            clamped_score = min(max(raw_score, -1.0), 1.0)

            dto = RetrievedChunkDTO(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                content=chunk.content,
                similarity_score=round(clamped_score, 6),
            )
            filtered_results.append(dto)

            if len(filtered_results) >= top_k:
                break

        return filtered_results
