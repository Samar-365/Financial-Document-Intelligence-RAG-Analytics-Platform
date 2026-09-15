"""Retrieval-Augmented Generation (RAG) pipeline components: embeddings, vector search, retrieval, prompts, LLM clients."""

# Module 3.1: Dense vector embeddings generation
from app.rag.embeddings import EmbeddingGenerator, EmbeddingError
# Module 3.2: In-memory FAISS vector indexing and metadata mappings
from app.rag.faiss_store import FAISSVectorStore, VectorStorageError
# Module 3.3: Top-K vector retrieval and similarity confidence filtering
from app.rag.retriever import VectorRetriever, RetrievedChunkDTO
# Module 4.1: Delimited XML context block construction with citation tags
from app.rag.prompt_builder import PromptBuilder
# Module 4.2: Strict negative-constraint system prompt formulation
from app.rag.system_prompts import FinancialSystemPrompts
# Module 4.3: OpenAI GPT-4o-mini client wrapper with deterministic parameters & retries
from app.rag.llm_client import (
    OpenAIClientWrapper,
    LLMGenerationResultDTO,
    LLMServiceError,
)
# Module 4.4: Local air-gapped Ollama engine and automatic failover switch
from app.rag.ollama_client import (
    OllamaClientWrapper,
    OllamaServiceError,
    HybridLLMDispatcher,
)
# Module 5.1: Inline bracketed citation parser and deduplicator
from app.rag.citation_parser import (
    RawCitationToken,
    CitationParser,
)
# Module 5.2: Citation verification against retrieved chunks and evidence snippet mapper
from app.rag.citation_verifier import (
    VerifiedCitationDTO,
    CitationVerifier,
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
    "VerifiedCitationDTO",
    "CitationVerifier",
]


