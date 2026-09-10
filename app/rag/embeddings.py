"""Dense Vector Embedding Generator for RAG pipeline (Module 3.1).

Responsible for:
1. Loading pre-trained transformer model (all-MiniLM-L6-v2) onto CPU / target device.
2. Generating 384-dimensional dense vectors in configurable batches (default 32).
3. Applying L2 unit normalization so that dot products directly compute cosine similarity.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingError(Exception):
    """Raised when embedding generation fails during inference or batch processing (PROC_003)."""

    def __init__(
        self,
        message: str = "PROC_003: Document processing encountered an error during embedding generation.",
        error_code: str = "PROC_003",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class EmbeddingGenerator:
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
        if not model_name or not isinstance(model_name, str):
            raise ValueError("model_name must be a non-empty string.")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size

        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            raise EmbeddingError(
                f"PROC_003: Failed to load embedding model '{self.model_name}': {e}"
            ) from e

        if hasattr(self.model, "get_embedding_dimension"):
            dim = self.model.get_embedding_dimension()
        elif hasattr(self.model, "get_sentence_embedding_dimension"):
            dim = self.model.get_sentence_embedding_dimension()
        else:
            dim = 384
        self._dimension = int(dim) if dim is not None else 384

    @property
    def dimension(self) -> int:
        """Returns the vector dimensionality of the embedding model (e.g. 384)."""
        return self._dimension

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Returns L2-normalized numpy array of shape (N, 384).

        Args:
            texts: List of text chunks or queries to encode.

        Returns:
            np.ndarray: L2-normalized floating-point array of shape (N, 384).

        Raises:
            TypeError: If texts is not a list or contains non-string items.
            EmbeddingError: If model inference fails.
        """
        if not isinstance(texts, list):
            raise TypeError("texts must be a list of strings.")

        if not texts:
            return np.empty((0, self._dimension), dtype=np.float32)

        for i, text in enumerate(texts):
            if not isinstance(text, str):
                raise TypeError(
                    f"All elements in texts must be strings. Element at index {i} is {type(text).__name__}."
                )

        try:
            # Batch inference using SentenceTransformer
            raw_embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=False,
            )

            # Ensure 2D float32 numpy array
            raw_embeddings = np.asarray(raw_embeddings, dtype=np.float32)
            if raw_embeddings.ndim == 1:
                raw_embeddings = raw_embeddings.reshape(1, -1)

            # Task 2: Explicit L2 Unit Normalization (v_hat = v / ||v||_2)
            norms = np.linalg.norm(raw_embeddings, ord=2, axis=1, keepdims=True)
            # Guard against division by zero
            norms = np.where(norms == 0.0, 1.0, norms)
            normalized_embeddings = raw_embeddings / norms

            return normalized_embeddings
        except Exception as e:
            if isinstance(e, TypeError):
                raise
            raise EmbeddingError(f"PROC_003: Embedding generation failed: {e}") from e
