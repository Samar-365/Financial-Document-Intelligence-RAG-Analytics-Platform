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


class VectorStorageError(Exception): #Custom exception raised when vector indexing or storage fails (PROC_004)
    """Raised when vector indexing or storage fails (PROC_004)."""

    def __init__(
        self,
        message: str = "PROC_004: Document processing encountered an error during indexing.",
        error_code: str = "PROC_004",
    ):
        super().__init__(message) #Pass error message to parent Exception class
        self.error_code = error_code #Store standardized error code for system tracking
        self.message = message


class FAISSVectorStore: #In-memory vector database using FAISS IndexFlatIP for fast cosine similarity search
    """In-memory FAISS vector index using IndexFlatIP for cosine similarity retrieval.

    Technical Tasks:
    1. Index Construction: Initialize FAISS IndexFlatIP with 384 dimensions and add
       normalized chunk embeddings.
    2. ID Mapping Dictionary: Build an in-memory dictionary mapping FAISS integer indices
       (0, 1, 2...) to chunk UUIDs and metadata for lookup.
    """

    def __init__(self, dimension: int = 384): #Initialize vector store with expected vector size (384 for all-MiniLM-L6-v2)
        """Initializes the FAISS vector store with the given embedding dimensionality.

        Args:
            dimension: Dimensionality of embedding vectors (default 384 for all-MiniLM-L6-v2).

        Raises:
            ValueError: If dimension is less than or equal to 0.
        """
        if not isinstance(dimension, int) or dimension <= 0: #Validate that dimension is a positive integer
            raise ValueError("dimension must be a positive integer.")

        self._dimension = dimension
        try:
            # IndexFlatIP computes exact Inner Product (dot product = cosine similarity on normalized vectors)
            self._index = faiss.IndexFlatIP(self._dimension) #Creates the in-memory FAISS index
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: Failed to initialize FAISS IndexFlatIP: {e}"
            ) from e

        # In-memory mapping stores to link FAISS numeric positions with rich chunk metadata
        self._index_to_chunk: Dict[int, TextChunkDTO] = {} #Maps FAISS integer index (0, 1, 2...) -> Chunk metadata DTO
        self._chunk_id_to_index: Dict[str, int] = {} #Maps chunk UUID string -> FAISS integer index
        self._doc_to_indices: Dict[str, List[int]] = {} #Maps document ID -> list of all FAISS indices belonging to it

    @property
    def dimension(self) -> int: #Exposes index vector dimension
        """Returns the vector dimensionality configured for this index."""
        return self._dimension

    @property
    def total_vectors(self) -> int: #Returns how many vectors are stored in the index
        """Returns the total number of vectors stored in the FAISS index."""
        return self._index.ntotal

    def __len__(self) -> int: #Allows using len(store) to get total count
        """Returns total vectors stored."""
        return self.total_vectors

    def add_vectors( #Main method: adds embeddings to FAISS and maps them to chunk metadata
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
        if not document_id or not isinstance(document_id, str): #Validates document ID is a non-empty string
            raise ValueError("document_id must be a non-empty string.")

        if not isinstance(chunks, list): #Checks that chunks are passed as a list
            raise TypeError("chunks must be a list of TextChunkDTO instances.")

        if not isinstance(embeddings, np.ndarray): #Checks that embeddings are passed as a NumPy array
            raise TypeError("embeddings must be a numpy ndarray.")

        # Handle empty addition gracefully
        if len(chunks) == 0 and embeddings.size == 0: #If there is nothing to add, return 0
            return 0

        if embeddings.ndim != 2: #Embeddings must be a 2D table (rows = vectors, cols = dimensions)
            raise ValueError(
                f"embeddings must be a 2D array, got ndim={embeddings.ndim}."
            )

        num_vectors, vector_dim = embeddings.shape
        if vector_dim != self._dimension: #Checks if embedding dimension matches index dimension (384)
            raise ValueError(
                f"Embedding dimension {vector_dim} does not match index dimension {self._dimension}."
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

        try:
            # Ensure contiguous float32 memory layout for FAISS C++ library
            contiguous_embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
            start_index = self._index.ntotal #Starting FAISS integer index for this new batch

            # Task 1: Add vectors to FAISS IndexFlatIP
            self._index.add(contiguous_embeddings) #Inserts raw vectors into the FAISS index

            # Task 2: Build in-memory ID mapping dictionaries
            if document_id not in self._doc_to_indices: #Initialize list if this is the first time seeing this document
                self._doc_to_indices[document_id] = []

            for i, chunk in enumerate(chunks): #Map each chunk to its corresponding FAISS integer position
                current_idx = start_index + i
                self._index_to_chunk[current_idx] = chunk #Store chunk metadata at index
                self._chunk_id_to_index[chunk.chunk_id] = current_idx #Store chunk UUID mapping
                self._doc_to_indices[document_id].append(current_idx) #Group chunk under parent document ID

            return num_vectors #Returns the count of successfully indexed vectors
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise VectorStorageError(
                f"PROC_004: Failed to add vectors to FAISS index: {e}"
            ) from e

    def get_chunk_by_index(self, index: int) -> Optional[TextChunkDTO]: #Look up chunk metadata using FAISS integer index (0, 1, 2...)
        """Retrieves chunk metadata by FAISS integer index.

        Args:
            index: Sequential integer index in FAISS (0, 1, 2...).

        Returns:
            Optional[TextChunkDTO]: Chunk metadata DTO or None if not found.
        """
        return self._index_to_chunk.get(index)

    def get_chunk_by_id(self, chunk_id: str) -> Optional[TextChunkDTO]: #Look up chunk metadata using chunk UUID string
        """Retrieves chunk metadata by chunk UUID.

        Args:
            chunk_id: String UUID of the chunk.

        Returns:
            Optional[TextChunkDTO]: Chunk metadata DTO or None if not found.
        """
        index = self._chunk_id_to_index.get(chunk_id) #Find the FAISS index for this UUID
        if index is not None:
            return self._index_to_chunk.get(index) #Return the matching chunk metadata
        return None

    def get_chunks_by_document(self, document_id: str) -> List[TextChunkDTO]: #Retrieve all chunks belonging to a document
        """Retrieves all chunks associated with a specific document ID.

        Args:
            document_id: Identifier of the document.

        Returns:
            List[TextChunkDTO]: List of chunk DTOs in sequential order.
        """
        indices = self._doc_to_indices.get(document_id, []) #Get all indices associated with this document
        return [self._index_to_chunk[idx] for idx in indices if idx in self._index_to_chunk]

    def search( #Performs nearest neighbor search to find most relevant chunks
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
        if top_k <= 0: #top_k must be at least 1
            raise ValueError("top_k must be a positive integer.")

        if not isinstance(query_vector, np.ndarray): #Query must be a numpy ndarray
            raise TypeError("query_vector must be a numpy ndarray.")

        if query_vector.ndim == 1: #If query is 1D (384,), reshape to 2D (1, 384)
            query_vector = query_vector.reshape(1, -1)

        if query_vector.shape[1] != self._dimension: #Query vector dimension must match 384
            raise ValueError(
                f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self._dimension}."
            )

        if self.total_vectors == 0: #If no vectors are stored in the index, return empty results
            empty_scores = np.empty((query_vector.shape[0], 0), dtype=np.float32)
            empty_indices = np.empty((query_vector.shape[0], 0), dtype=np.int64)
            return empty_scores, empty_indices

        actual_k = min(top_k, self.total_vectors) #Cannot retrieve more neighbors than vectors available in index
        try:
            # Prepare contiguous memory layout for FAISS search
            contiguous_query = np.ascontiguousarray(query_vector, dtype=np.float32)
            scores, indices = self._index.search(contiguous_query, actual_k) #Executes the FAISS search returning scores and index positions
            return scores, indices #Returns similarity scores and matching integer indices
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: FAISS search operation failed: {e}"
            ) from e

    def reset(self) -> None: #Clears index and metadata (used when wiping or re-indexing)
        """Resets the FAISS index and clears all in-memory metadata mappings."""
        try:
            self._index.reset() #Clears all vectors from FAISS C++ index
            self._index_to_chunk.clear() #Empties integer-to-chunk dictionary
            self._chunk_id_to_index.clear() #Empties UUID-to-integer dictionary
            self._doc_to_indices.clear() #Empties document-to-indices dictionary
        except Exception as e:
            raise VectorStorageError(
                f"PROC_004: Failed to reset FAISS index: {e}"
            ) from e
