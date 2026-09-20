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


class OllamaServiceError(Exception): #Custom exception raised when local Ollama instance is unreachable or fails (RAG_005)
    """Raised when the local Ollama instance encounters an error or is unreachable."""

    def __init__(
        self,
        message: str = "RAG_005: Local Ollama service is unavailable or returned an error.",
        error_code: str = "RAG_005",
    ):
        super().__init__(message) #Pass error message to parent Exception class
        self.error_code = error_code #Store standardized error code for system tracking
        self.message = message


class OllamaClientWrapper: #Client wrapper for local air-gapped LLM inference via Ollama HTTP REST API
    """Queries local Ollama REST instance for zero-network-egress air-gapped inference.

    Technical Tasks:
    1. Ollama REST Integration: Query local Ollama instance (http://localhost:11434/api/chat).
    2. Automatic Failover Switch: Integrates with failover routing.
    """

    def __init__( #Initialize Ollama client with host, model name, timeout, and HTTP session
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
        self.host = host.rstrip("/") #Clean host URL by stripping trailing slash
        self.model = model
        self.timeout = timeout
        self.session = session or requests.Session() #Reuse persistent HTTP session for efficiency or testing

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO: #Sends prompt messages to local Ollama /api/chat endpoint
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
        if not isinstance(messages, list): #Validates that messages is a list
            raise TypeError("messages must be a list of dictionaries.")

        if not messages: #Checks that messages list is not empty
            raise ValueError("messages list cannot be empty.")

        for i, m in enumerate(messages): #Validate each message dictionary structure
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise TypeError(
                    f"Element at index {i} must be a dict containing 'role' and 'content' keys."
                )

        payload = { #Construct Ollama REST request body with deterministic temperature=0.1
            "model": self.model,
            "messages": messages,
            "stream": False, #Get complete response at once rather than streaming chunks
            "options": {
                "temperature": 0.1, #Low temperature ensures factual, deterministic answers
                "top_p": 0.95, #Nucleus sampling cutoff
                "num_predict": 1024, #Maximum tokens to generate
            },
        }

        endpoint = f"{self.host}/api/chat" #Ollama chat completions endpoint URL

        try:
            response = self.session.post(endpoint, json=payload, timeout=self.timeout) #Send HTTP POST request to Ollama
            response.raise_for_status() #Raise HTTPError if status code is 4xx or 5xx
            data = response.json() #Parse JSON response body

            message_data = data.get("message", {}) #Extract message dictionary from response
            raw_answer = message_data.get("content", "") #Extract generated response text

            prompt_tokens = int(data.get("prompt_eval_count", 0)) #Extract prompt evaluation token count
            completion_tokens = int(data.get("eval_count", 0)) #Extract completion evaluation token count
            model_name = data.get("model", self.model) #Extract model name used for generation

            return LLMGenerationResultDTO( #Package response and token metrics into result DTO
                raw_answer=raw_answer,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_name=model_name,
            )

        except requests.exceptions.RequestException as e: #Handle connection errors, timeouts, or unreachable daemon
            raise OllamaServiceError(
                f"RAG_005: Failed to communicate with local Ollama engine at {endpoint}: {e}"
            ) from e
        except Exception as e: #Handle any unexpected parsing or runtime errors
            raise OllamaServiceError(f"RAG_005: Ollama inference failed: {e}") from e


class HybridLLMDispatcher: #Orchestrator that handles automatic failover between OpenAI and local air-gapped Ollama
    """Manages automatic failover between primary cloud LLM (OpenAI) and local air-gapped Ollama.

    Technical Task 2 (Automatic Failover Switch):
    - If AIR_GAPPED_MODE is enabled (via constructor or env var), routes directly to Ollama.
    - Otherwise dispatches to OpenAI; if OpenAI fails, transparently fails over to Ollama.
    """

    def __init__( #Initialize dispatcher with primary OpenAI client, fallback Ollama client, and air-gapped mode toggle
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
        self.openai_client = openai_client or OpenAIClientWrapper() #Primary cloud LLM client
        self.ollama_client = ollama_client or OllamaClientWrapper() #Fallback local LLM client

        if air_gapped_mode is not None:
            self.air_gapped_mode = air_gapped_mode
        else: #Read air-gapped mode toggle from environment variable
            env_val = os.getenv("AIR_GAPPED_MODE", "false").strip().lower()
            self.air_gapped_mode = env_val in ("1", "true", "yes")

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO: #Dispatches generation: routes to Ollama in air-gapped mode or fails over if OpenAI fails
        """Executes LLM generation with transparent automatic failover.

        Args:
            messages: List of chat messages to process.

        Returns:
            LLMGenerationResultDTO: Output from OpenAI or Ollama fallback.
        """
        if self.air_gapped_mode: #In air-gapped mode, strictly route to local Ollama (zero network egress)
            return self.ollama_client.generate(messages)

        try: #Attempt cloud generation with primary OpenAI model
            return self.openai_client.generate(messages)
        except LLMServiceError: #If OpenAI service fails after retries, automatically fail over to Ollama
            # Automatic Failover to Ollama
            return self.ollama_client.generate(messages)
