"""PostgreSQL pgvector Storage & HNSW Index (Module 10.1).

Responsible for:
1. Persisting 384-dimensional chunk embeddings into PostgreSQL document_chunks table
   using the pgvector Vector(384) column type.
2. Executing HNSW cosine nearest-neighbor search with sub-50ms latency across 50,000+ vectors.
"""

import uuid
from typing import List, Optional

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text, delete

from app.document_processing.metadata_tagger import TextChunkDTO
from app.models.document_chunk import DocumentChunk
from app.rag.retriever import RetrievedChunkDTO


class PGVectorStorageError(Exception): #Custom exception raised when pgvector storage or search operations fail (PROC_010)
    """Raised when pgvector storage or search operations fail (PROC_010)."""

    def __init__(
        self,
        message: str = "PROC_010: pgvector storage operation encountered an error.",
        error_code: str = "PROC_010",
    ):
        super().__init__(message) #Pass error message to parent Exception class
        self.error_code = error_code #Store standardized error code for system tracking
        self.message = message


class PGVectorStore: #Persistent vector database using PostgreSQL pgvector for cosine similarity search
    """Persistent PostgreSQL vector store using pgvector for HNSW cosine similarity retrieval.

    Technical Tasks:
    1. pgvector Table Persistence: Migrate chunk embeddings from in-memory FAISS into
       PostgreSQL document_chunks table using Vector(384) column.
    2. HNSW Index & Latency Benchmark: Configure HNSW cosine index (vector_cosine_ops)
       and benchmark sub-50ms query execution across 50,000 vectors.
    """

    def __init__(self, dimension: int = 384): #Initialize vector store with expected vector size (384 for all-MiniLM-L6-v2)
        """Initializes the PGVectorStore with the given embedding dimensionality.

        Args:
            dimension: Dimensionality of embedding vectors (default 384 for all-MiniLM-L6-v2).

        Raises:
            ValueError: If dimension is less than or equal to 0.
        """
        if not isinstance(dimension, int) or dimension <= 0: #Validate that dimension is a positive integer
            raise ValueError("dimension must be a positive integer.")

        self._dimension = dimension

    @property
    def dimension(self) -> int: #Exposes index vector dimension
        """Returns the vector dimensionality configured for this store."""
        return self._dimension

    def store_embeddings( #Main method: persists chunk embeddings into PostgreSQL document_chunks table
        self,
        session: Session,
        document_id: str,
        chunks: List[TextChunkDTO],
        embeddings: np.ndarray,
    ) -> int:
        """Persists 384-dim embeddings into PostgreSQL document_chunks table.

        Args:
            session: Active SQLAlchemy session for the database transaction.
            document_id: Unique identifier for the parent document.
            embeddings: 2D numpy array of shape (N, dimension) containing float32 vectors.
            chunks: List of TextChunkDTO metadata objects matching the embeddings.

        Returns:
            int: Number of chunk rows inserted.

        Raises:
            ValueError: If inputs are invalid or dimensions/counts mismatch.
            TypeError: If input types are incorrect.
            PGVectorStorageError: If database insertion fails.
        """
        # --- Input validation (same rigor as FAISSVectorStore.add_vectors) ---
        if not document_id or not isinstance(document_id, str): #Validates document ID is a non-empty string
            raise ValueError("document_id must be a non-empty string.")

        if not isinstance(chunks, list): #Checks that chunks are passed as a list
            raise TypeError("chunks must be a list of TextChunkDTO instances.")

        if not isinstance(embeddings, np.ndarray): #Checks that embeddings are passed as a NumPy array
            raise TypeError("embeddings must be a numpy ndarray.")

        # Handle empty insertion gracefully
        if len(chunks) == 0 and embeddings.size == 0: #If there is nothing to store, return 0
            return 0

        if embeddings.ndim != 2: #Embeddings must be a 2D table (rows = vectors, cols = dimensions)
            raise ValueError(
                f"embeddings must be a 2D array, got ndim={embeddings.ndim}."
            )

        num_vectors, vector_dim = embeddings.shape
        if vector_dim != self._dimension: #Checks if embedding dimension matches expected dimension (384)
            raise ValueError(
                f"Embedding dimension {vector_dim} does not match store dimension {self._dimension}."
            )

        if num_vectors != len(chunks): #Checks that every vector has a corresponding chunk metadata object
            raise ValueError(
                f"Number of embeddings ({num_vectors}) does not match number of chunks ({len(chunks)})."
            )

        for i, chunk in enumerate(chunks): #Validate each element is indeed a TextChunkDTO instance
            if not isinstance(chunk, TextChunkDTO):
                raise TypeError(
                    f"Element at index {i} in chunks is {type(chunk).__name__}, expected TextChunkDTO."
                )

        # --- Task 1: Bulk insert chunk rows with Vector(384) embeddings ---
        try:
            rows = []
            for i, chunk in enumerate(chunks): #Build ORM row objects for each chunk-embedding pair
                embedding_vector = embeddings[i].astype(np.float32).tolist() #Convert numpy row to Python list for pgvector

                row = DocumentChunk(
                    id=str(uuid.uuid4()), #Generate new UUID for the database row primary key
                    document_id=document_id,
                    chunk_id=chunk.chunk_id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    token_estimate=chunk.token_estimate,
                    is_table_chunk=chunk.is_table_chunk,
                    embedding=embedding_vector, #Store 384-dim vector via pgvector column type
                )
                rows.append(row)

            session.add_all(rows) #Batch-add all ORM objects to the session
            session.flush() #Emit INSERT SQL to database without committing — caller controls commit

            return len(rows) #Returns the count of successfully persisted chunk rows
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            session.rollback() #Rollback the transaction to avoid leaving partial data
            raise PGVectorStorageError(
                f"PROC_010: Failed to store embeddings in pgvector: {e}"
            ) from e

    def search_similar( #Performs nearest neighbor search using pgvector cosine distance operator
        self,
        session: Session,
        query_vector: np.ndarray,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[RetrievedChunkDTO]:
        """Executes HNSW nearest-neighbor cosine search in PostgreSQL.

        Args:
            session: Active SQLAlchemy session for the query.
            query_vector: 1D or 2D numpy array containing 384-dimensional query embedding.
            top_k: Number of nearest neighbors to retrieve (default 5).
            document_id: Optional document ID filter. If provided, only searches
                         chunks belonging to that document.

        Returns:
            List[RetrievedChunkDTO]: List of candidate chunks sorted by descending
            cosine similarity (highest similarity first).

        Raises:
            ValueError: If query vector dimensions mismatch or top_k <= 0.
            TypeError: If query_vector is not a numpy ndarray.
            PGVectorStorageError: If search execution fails.
        """
        if top_k <= 0: #top_k must be at least 1
            raise ValueError("top_k must be a positive integer.")

        if not isinstance(query_vector, np.ndarray): #Query must be a numpy ndarray
            raise TypeError("query_vector must be a numpy ndarray.")

        if query_vector.ndim == 2: #If 2D array (1, 384), flatten to 1D (384,)
            query_vector = query_vector.flatten()

        if query_vector.ndim != 1: #After flattening, must be 1D
            raise ValueError(
                f"query_vector must be a 1D or 2D array, got ndim={query_vector.ndim}."
            )

        if query_vector.shape[0] != self._dimension: #Query vector dimension must match 384
            raise ValueError(
                f"Query vector dimension {query_vector.shape[0]} does not match "
                f"store dimension {self._dimension}."
            )

        try:
            # Convert query to Python list for pgvector SQL operator
            query_list = query_vector.astype(np.float32).tolist()
            query_vector_str = str(query_list) #pgvector expects '[0.1, 0.2, ...]' string format

            # Task 2: Execute HNSW cosine distance search using <=> operator
            # Cosine distance: 0.0 = identical, 2.0 = opposite
            # We convert to similarity: similarity = 1.0 - cosine_distance
            if document_id: #Filter by specific document if requested
                sql = text(
                    "SELECT chunk_id, document_id, chunk_index, page_number, content, "
                    "1.0 - (embedding <=> :query_vec) AS similarity_score "
                    "FROM document_chunks "
                    "WHERE document_id = :doc_id "
                    "ORDER BY embedding <=> :query_vec "
                    "LIMIT :top_k"
                )
                result = session.execute(
                    sql,
                    {"query_vec": query_vector_str, "doc_id": document_id, "top_k": top_k},
                )
            else: #Search across all documents
                sql = text(
                    "SELECT chunk_id, document_id, chunk_index, page_number, content, "
                    "1.0 - (embedding <=> :query_vec) AS similarity_score "
                    "FROM document_chunks "
                    "ORDER BY embedding <=> :query_vec "
                    "LIMIT :top_k"
                )
                result = session.execute(
                    sql,
                    {"query_vec": query_vector_str, "top_k": top_k},
                )

            # Convert raw SQL rows to RetrievedChunkDTO objects
            retrieved_chunks: List[RetrievedChunkDTO] = []
            for row in result: #Iterate through SQL result rows
                dto = RetrievedChunkDTO(
                    chunk_id=row.chunk_id,
                    document_id=row.document_id,
                    chunk_index=row.chunk_index,
                    page_number=row.page_number,
                    content=row.content,
                    similarity_score=round(float(row.similarity_score), 6), #Clamp to 6 decimal places for consistency
                )
                retrieved_chunks.append(dto)

            return retrieved_chunks #Returns the top-K relevant chunks sorted by similarity
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise PGVectorStorageError(
                f"PROC_010: pgvector search operation failed: {e}"
            ) from e

    def delete_document( #Removes all chunks belonging to a document for re-ingestion cleanup
        self,
        session: Session,
        document_id: str,
    ) -> int:
        """Deletes all chunk rows for a given document ID.

        Args:
            session: Active SQLAlchemy session.
            document_id: Identifier of the document whose chunks should be removed.

        Returns:
            int: Number of rows deleted.

        Raises:
            ValueError: If document_id is empty or invalid.
            PGVectorStorageError: If deletion fails.
        """
        if not document_id or not isinstance(document_id, str): #Validates document ID is a non-empty string
            raise ValueError("document_id must be a non-empty string.")

        try:
            stmt = delete(DocumentChunk).where( #Build DELETE statement filtering by document_id
                DocumentChunk.document_id == document_id
            )
            result = session.execute(stmt)
            session.flush() #Emit DELETE SQL without committing — caller controls commit
            return result.rowcount #Returns count of deleted rows
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            session.rollback()
            raise PGVectorStorageError(
                f"PROC_010: Failed to delete document chunks: {e}"
            ) from e

    def get_chunk_count( #Returns total number of chunks stored in the database
        self,
        session: Session,
        document_id: Optional[str] = None,
    ) -> int:
        """Returns the count of chunks in the store, optionally filtered by document.

        Args:
            session: Active SQLAlchemy session.
            document_id: Optional filter to count chunks for a specific document.

        Returns:
            int: Number of chunk rows.
        """
        try:
            query = session.query(DocumentChunk)
            if document_id: #Optionally filter by document
                query = query.filter(DocumentChunk.document_id == document_id)
            return query.count()
        except Exception as e:
            raise PGVectorStorageError(
                f"PROC_010: Failed to count chunks: {e}"
            ) from e
