"""OpenAI GPT-4o-mini Client Wrapper (Module 4.3).

Responsible for:
1. Deterministic inference dispatch to OpenAI GPT-4o-mini (temperature=0.1, top_p=0.95, max_tokens=1024).
2. Rate limit (HTTP 429) & service unavailable (HTTP 503) retry logic with exponential backoff.
3. Packaging completions and token usage into LLMGenerationResultDTO.
"""

import os
import time
from typing import Dict, List, Optional
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel, Field


class LLMGenerationResultDTO(BaseModel): #DTO capturing normalized LLM completion output and token metrics
    """Data Transfer Object capturing normalized LLM completion output and token metrics."""

    raw_answer: str = Field( #Generated natural language response text
        ...,
        description="Generated natural language response text.",
    )
    prompt_tokens: int = Field( #Total tokens consumed by the prompt input (must be >= 0)
        ...,
        ge=0,
        description="Total tokens consumed in the prompt payload.",
    )
    completion_tokens: int = Field( #Total tokens produced in the generation output (must be >= 0)
        ...,
        ge=0,
        description="Total tokens produced in the generation output.",
    )
    model_name: str = Field( #Exact model identifier used during generation
        ...,
        description="Exact model identifier utilized during generation.",
    )


class LLMServiceError(Exception): #Raised when LLM API request fails permanently after retries (RAG_005)
    """Raised when an LLM service request fails permanently (RAG_005)."""

    def __init__(
        self,
        message: str = "RAG_005: The AI service is temporarily unavailable. Please try again in a moment.",
        error_code: str = "RAG_005",
    ):
        super().__init__(message) #Pass error message to parent Exception class
        self.error_code = error_code #Store standardized error code for system tracking
        self.message = message


class OpenAIClientWrapper: #Dispatches prompts to OpenAI GPT-4o-mini with deterministic parameters and exponential backoff
    """Dispatches grounded prompts to OpenAI GPT-4o-mini with deterministic parameters and retries.

    Technical Tasks:
    1. Deterministic Inference Dispatch: Uses temperature=0.1, top_p=0.95, max_tokens=1024.
    2. Rate Limit & Exponential Retry: Retries on 429/503/connection drops with exponential backoff.
    """

    def __init__( #Initializes client with model name, retries, timeout, and backoff settings
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        initial_backoff: float = 0.5,
        timeout: float = 30.0,
        client: Optional[OpenAI] = None,
    ):
        """Initializes OpenAI client wrapper.

        Args:
            api_key: OpenAI API key. If omitted, resolved via OPENAI_API_KEY env var.
            model: Model identifier (defaults to 'gpt-4o-mini').
            max_retries: Maximum number of retries for transient failures (default 3).
            initial_backoff: Initial seconds for exponential backoff (default 0.5s).
            timeout: Request timeout in seconds (default 30s).
            client: Optional injected OpenAI client instance (for testing/mocking).
        """
        self.model = model
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.timeout = timeout

        if client is not None: #Allows injecting mock client for unit testing
            self.client = client
        else: #Resolves API key from parameter or environment variable
            resolved_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key-for-local-init")
            self.client = OpenAI(api_key=resolved_key, timeout=self.timeout) #Initializes official OpenAI client

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO: #Calls OpenAI chat completions API with retry logic
        """Calls GPT-4o-mini with deterministic parameters and retry handling.

        Args:
            messages: OpenAI-compatible list of message dicts (role, content).

        Returns:
            LLMGenerationResultDTO: Response text and token metrics.

        Raises:
            TypeError: If messages is not a list of dictionaries.
            ValueError: If messages is empty.
            LLMServiceError: If the request fails after exhausting all retries (RAG_005).
        """
        if not isinstance(messages, list): #Validates that messages is a list
            raise TypeError("messages must be a list of dictionaries.")

        if not messages: #Checks that messages list is not empty
            raise ValueError("messages list cannot be empty.")

        for i, m in enumerate(messages): #Validates each message has role and content keys
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise TypeError(
                    f"Element at index {i} must be a dict containing 'role' and 'content' keys."
                )

        backoff = self.initial_backoff #Initial sleep duration before retry (starts at 0.5s)
        last_exception = None

        for attempt in range(self.max_retries + 1): #Try initial attempt + up to max_retries
            try:
                # Task 1: Deterministic Inference Dispatch (low temperature to prevent hallucination)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1, #Low temperature ensures factual, deterministic answers
                    top_p=0.95, #Nucleus sampling cutoff
                    max_tokens=1024, #Cap response length to prevent runaway generation
                )

                choice = response.choices[0] #Get first completion candidate
                answer = choice.message.content or "" #Extract text response
                prompt_tokens = response.usage.prompt_tokens if response.usage else 0 #Extract prompt tokens used
                completion_tokens = response.usage.completion_tokens if response.usage else 0 #Extract generated tokens count
                model_used = response.model or self.model #Capture exact model returned by API

                return LLMGenerationResultDTO( #Return normalized result DTO
                    raw_answer=answer,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model_name=model_used,
                )

            except (RateLimitError, InternalServerError, APIConnectionError, APITimeoutError) as e:
                last_exception = e #Record exception for logging
                # Task 2: Rate Limit & Exponential Retry (handles 429 rate limit, 500/503 server errors)
                if attempt < self.max_retries:
                    time.sleep(backoff) #Pause execution before retrying
                    backoff *= 2.0 #Double wait time exponentially (0.5s -> 1.0s -> 2.0s)
                else:
                    raise LLMServiceError( #All retries exhausted
                        f"RAG_005: OpenAI service error after {self.max_retries} retries: {e}"
                    ) from e

            except APIError as e:
                # Handle generic 429/503 status codes if wrapped in generic APIError
                status_code = getattr(e, "status_code", None)
                if status_code in (429, 503) and attempt < self.max_retries:
                    last_exception = e
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    raise LLMServiceError(f"RAG_005: OpenAI API error: {e}") from e

            except Exception as e: #Catch any unexpected non-API errors
                raise LLMServiceError(f"RAG_005: Unexpected LLM failure: {e}") from e

        raise LLMServiceError( #Final fallback error if loop completes without returning
            f"RAG_005: OpenAI inference failed after {self.max_retries} retries: {last_exception}"
        )
