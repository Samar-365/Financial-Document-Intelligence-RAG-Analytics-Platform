"""Retrieval-Augmented Generation (RAG) pipeline components: embeddings, vector search, retrieval, prompts, LLM clients."""

from app.rag.embeddings import EmbeddingGenerator, EmbeddingError
from app.rag.faiss_store import FAISSVectorStore, VectorStorageError
from app.rag.retriever import VectorRetriever, RetrievedChunkDTO
from app.rag.prompt_builder import PromptBuilder
from app.rag.system_prompts import FinancialSystemPrompts
from app.rag.llm_client import (
    OpenAIClientWrapper,
    LLMGenerationResultDTO,
    LLMServiceError,
)
from app.rag.ollama_client import (
    OllamaClientWrapper,
    OllamaServiceError,
    HybridLLMDispatcher,
)
from app.rag.citation_parser import (
    RawCitationToken,
    CitationParser,
)

__all__ = [
    "EmbeddingGenerator",
    "EmbeddingError",
    "FAISSVectorStore",
    "VectorStorageError",
    "VectorRetriever",
    "RetrievedChunkDTO",
    "PromptBuilder",
    "FinancialSystemPrompts",
    "OpenAIClientWrapper",
    "LLMGenerationResultDTO",
    "LLMServiceError",
    "OllamaClientWrapper",
    "OllamaServiceError",
    "HybridLLMDispatcher",
    "RawCitationToken",
    "CitationParser",
]

