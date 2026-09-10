"""Local Air-Gapped Ollama Fallback Engine (Module 4.4).

Responsible for:
1. Querying local Ollama REST API (http://localhost:11434/api/chat) with llama3/mistral
   for air-gapped, zero-network-egress inference.
2. Providing an Automatic Failover Switch: if OpenAI API fails or if AIR_GAPPED_MODE=True,
   routes requests to Ollama transparently.
"""

import os
from typing import Dict, List, Optional
import requests
from app.rag.llm_client import LLMGenerationResultDTO, LLMServiceError, OpenAIClientWrapper


class OllamaServiceError(Exception):
    """Raised when the local Ollama instance encounters an error or is unreachable."""

    def __init__(
        self,
        message: str = "RAG_005: Local Ollama service is unavailable or returned an error.",
        error_code: str = "RAG_005",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class OllamaClientWrapper:
    """Queries local Ollama REST instance for zero-network-egress air-gapped inference.

    Technical Tasks:
    1. Ollama REST Integration: Query local Ollama instance (http://localhost:11434/api/chat).
    2. Automatic Failover Switch: Integrates with failover routing.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3",
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ):
        """Initializes OllamaClientWrapper.

        Args:
            host: Base URL of the Ollama server (defaults to 'http://localhost:11434').
            model: Model identifier (defaults to 'llama3').
            timeout: Request timeout in seconds (defaults to 30.0).
            session: Optional custom requests Session instance (for testing/mocking).
        """
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.session = session or requests.Session()

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Queries local Ollama instance for zero-network-egress air-gapped inference.

        Args:
            messages: List of OpenAI-compatible role/content dictionaries.

        Returns:
            LLMGenerationResultDTO: Parsed response text and token statistics.

        Raises:
            TypeError: If messages is not a list of dictionaries.
            ValueError: If messages is empty.
            OllamaServiceError: If Ollama cannot be reached or returns HTTP error.
        """
        if not isinstance(messages, list):
            raise TypeError("messages must be a list of dictionaries.")

        if not messages:
            raise ValueError("messages list cannot be empty.")

        for i, m in enumerate(messages):
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise TypeError(
                    f"Element at index {i} must be a dict containing 'role' and 'content' keys."
                )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.95,
                "num_predict": 1024,
            },
        }

        endpoint = f"{self.host}/api/chat"

        try:
            response = self.session.post(endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            message_data = data.get("message", {})
            raw_answer = message_data.get("content", "")

            prompt_tokens = int(data.get("prompt_eval_count", 0))
            completion_tokens = int(data.get("eval_count", 0))
            model_name = data.get("model", self.model)

            return LLMGenerationResultDTO(
                raw_answer=raw_answer,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_name=model_name,
            )

        except requests.exceptions.RequestException as e:
            raise OllamaServiceError(
                f"RAG_005: Failed to communicate with local Ollama engine at {endpoint}: {e}"
            ) from e
        except Exception as e:
            raise OllamaServiceError(f"RAG_005: Ollama inference failed: {e}") from e


class HybridLLMDispatcher:
    """Manages automatic failover between primary cloud LLM (OpenAI) and local air-gapped Ollama.

    Technical Task 2 (Automatic Failover Switch):
    - If AIR_GAPPED_MODE is enabled (via constructor or env var), routes directly to Ollama.
    - Otherwise dispatches to OpenAI; if OpenAI fails, transparently fails over to Ollama.
    """

    def __init__(
        self,
        openai_client: Optional[OpenAIClientWrapper] = None,
        ollama_client: Optional[OllamaClientWrapper] = None,
        air_gapped_mode: Optional[bool] = None,
    ):
        """Initializes HybridLLMDispatcher.

        Args:
            openai_client: Configured OpenAIClientWrapper instance.
            ollama_client: Configured OllamaClientWrapper instance.
            air_gapped_mode: Boolean toggle. If None, checks env var AIR_GAPPED_MODE.
        """
        self.openai_client = openai_client or OpenAIClientWrapper()
        self.ollama_client = ollama_client or OllamaClientWrapper()

        if air_gapped_mode is not None:
            self.air_gapped_mode = air_gapped_mode
        else:
            env_val = os.getenv("AIR_GAPPED_MODE", "false").strip().lower()
            self.air_gapped_mode = env_val in ("1", "true", "yes")

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Executes LLM generation with transparent automatic failover.

        Args:
            messages: List of chat messages to process.

        Returns:
            LLMGenerationResultDTO: Output from OpenAI or Ollama fallback.
        """
        if self.air_gapped_mode:
            return self.ollama_client.generate(messages)

        try:
            return self.openai_client.generate(messages)
        except LLMServiceError:
            # Automatic Failover to Ollama
            return self.ollama_client.generate(messages)
