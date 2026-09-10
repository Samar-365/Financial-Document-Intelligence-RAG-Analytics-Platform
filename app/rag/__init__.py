"""Retrieval-Augmented Generation (RAG) pipeline components: embeddings, vector search, retrieval, prompts."""

from app.rag.embeddings import EmbeddingGenerator, EmbeddingError
from app.rag.faiss_store import FAISSVectorStore, VectorStorageError
from app.rag.retriever import VectorRetriever, RetrievedChunkDTO
from app.rag.prompt_builder import PromptBuilder
from app.rag.system_prompts import FinancialSystemPrompts

__all__ = [
    "EmbeddingGenerator",
    "EmbeddingError",
    "FAISSVectorStore",
    "VectorStorageError",
    "VectorRetriever",
    "RetrievedChunkDTO",
    "PromptBuilder",
    "FinancialSystemPrompts",
]
