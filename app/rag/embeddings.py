"""Dense Vector Embedding Generator for RAG pipeline (Module 3.1).

Responsible for:
1. Loading pre-trained transformer model (all-MiniLM-L6-v2) onto CPU / target device.
2. Generating 384-dimensional dense vectors in configurable batches (default 32).
3. Applying L2 unit normalization so that dot products directly compute cosine similarity.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingError(Exception): #Custom exception raised when embedding generation or model loading fails (PROC_003)
    """Raised when embedding generation fails during inference or batch processing (PROC_003)."""

    def __init__(
        self,
        message: str = "PROC_003: Document processing encountered an error during embedding generation.",
        error_code: str = "PROC_003",
    ):
        super().__init__(message) #Pass error message up to the parent Exception class
        self.error_code = error_code #Store the standardized error code for system tracking
        self.message = message


class EmbeddingGenerator: #Main class responsible for converting text chunks into dense vector embeddings
    """Generates L2-normalized dense vector embeddings using SentenceTransformers.

    Technical Tasks:
    1. Model Initialization & Batch Inference: Load all-MiniLM-L6-v2 onto CPU and
       generate 384-dimensional dense vectors in batches of 32 chunks.
    2. L2 Unit Normalization: Normalize all embedding vectors to unit length
       (v_hat = v / ||v||_2) so dot products equal cosine similarity.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = "cpu",
        batch_size: int = 32,
    ):
        """Initializes the EmbeddingGenerator with model, target device, and batch size.

        Args:
            model_name: HuggingFace model card identifier (defaults to 'all-MiniLM-L6-v2').
            device: Target execution device, defaults to 'cpu'.
            batch_size: Number of chunks per batch during inference (defaults to 32).
        """
        if not model_name or not isinstance(model_name, str): #Validates that model_name is a non-empty string
            raise ValueError("model_name must be a non-empty string.")
        if not isinstance(batch_size, int) or batch_size <= 0: #Validates that batch size is a positive integer
            raise ValueError("batch_size must be a positive integer.")

        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size

        try:
            # Load the HuggingFace transformer model into memory on the target device
            self.model = SentenceTransformer(self.model_name, device=self.device) #Downloads and loads the embedding model
        except Exception as e: #Catches any model download or initialization failures
            raise EmbeddingError(
                f"PROC_003: Failed to load embedding model '{self.model_name}': {e}"
            ) from e

        # Determine the vector dimension produced by this model
        if hasattr(self.model, "get_embedding_dimension"):
            dim = self.model.get_embedding_dimension() #Gets the output vector dimension (384 for all-MiniLM-L6-v2)
        elif hasattr(self.model, "get_sentence_embedding_dimension"):
            dim = self.model.get_sentence_embedding_dimension()
        else:
            dim = 384
        self._dimension = int(dim) if dim is not None else 384 #Store vector dimension as an integer

    @property
    def dimension(self) -> int: #Getter property to safely expose vector dimension
        """Returns the vector dimensionality of the embedding model (e.g. 384)."""
        return self._dimension

    def generate_embeddings(self, texts: List[str]) -> np.ndarray: #Main function: converts list of text chunks into normalized vectors
        """Returns L2-normalized numpy array of shape (N, 384).

        Args:
            texts: List of text chunks or queries to encode.

        Returns:
            np.ndarray: L2-normalized floating-point array of shape (N, 384).

        Raises:
            TypeError: If texts is not a list or contains non-string items.
            EmbeddingError: If model inference fails.
        """
        if not isinstance(texts, list): #Check that the input is provided as a list
            raise TypeError("texts must be a list of strings.")

        if not texts: #If the list is empty, return an empty 2D numpy array with shape (0, 384)
            return np.empty((0, self._dimension), dtype=np.float32)

        for i, text in enumerate(texts): #Loop through each text item to ensure all entries are valid strings
            if not isinstance(text, str):
                raise TypeError(
                    f"All elements in texts must be strings. Element at index {i} is {type(text).__name__}."
                )

        try:
            # Batch inference using SentenceTransformer: process chunks in batches of 32
            raw_embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size, #Processes in chunks of 32 for optimal CPU memory usage
                show_progress_bar=False,
                convert_to_numpy=True, #Converts output tensors directly into numpy array
                normalize_embeddings=False, #We handle explicit normalization ourselves below
            )

            # Ensure 2D float32 numpy array format
            raw_embeddings = np.asarray(raw_embeddings, dtype=np.float32)
            if raw_embeddings.ndim == 1: #If single text vector is 1D (384,), reshape to 2D (1, 384)
                raw_embeddings = raw_embeddings.reshape(1, -1)

            # Task 2: Explicit L2 Unit Normalization (v_hat = v / ||v||_2)
            # Calculate Euclidean norm (vector length) along each row
            norms = np.linalg.norm(raw_embeddings, ord=2, axis=1, keepdims=True) #Calculates the length of each vector
            # Guard against division by zero if a vector is all zeros
            norms = np.where(norms == 0.0, 1.0, norms) #Replaces 0 length with 1 to avoid dividing by zero
            normalized_embeddings = raw_embeddings / norms #Scales vectors to unit length (length = 1.0) so dot product equals cosine similarity

            return normalized_embeddings #Returns the final 2D array of normalized vectors
        except Exception as e:
            if isinstance(e, TypeError):
                raise
            raise EmbeddingError(f"PROC_003: Embedding generation failed: {e}") from e
