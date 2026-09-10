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


class LLMGenerationResultDTO(BaseModel):
    """Data Transfer Object capturing normalized LLM completion output and token metrics."""

    raw_answer: str = Field(
        ...,
        description="Generated natural language response text.",
    )
    prompt_tokens: int = Field(
        ...,
        ge=0,
        description="Total tokens consumed in the prompt payload.",
    )
    completion_tokens: int = Field(
        ...,
        ge=0,
        description="Total tokens produced in the generation output.",
    )
    model_name: str = Field(
        ...,
        description="Exact model identifier utilized during generation.",
    )


class LLMServiceError(Exception):
    """Raised when an LLM service request fails permanently (RAG_005)."""

    def __init__(
        self,
        message: str = "RAG_005: The AI service is temporarily unavailable. Please try again in a moment.",
        error_code: str = "RAG_005",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class OpenAIClientWrapper:
    """Dispatches grounded prompts to OpenAI GPT-4o-mini with deterministic parameters and retries.

    Technical Tasks:
    1. Deterministic Inference Dispatch: Uses temperature=0.1, top_p=0.95, max_tokens=1024.
    2. Rate Limit & Exponential Retry: Retries on 429/503/connection drops with exponential backoff.
    """

    def __init__(
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

        if client is not None:
            self.client = client
        else:
            resolved_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key-for-local-init")
            self.client = OpenAI(api_key=resolved_key, timeout=self.timeout)

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
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
        if not isinstance(messages, list):
            raise TypeError("messages must be a list of dictionaries.")

        if not messages:
            raise ValueError("messages list cannot be empty.")

        for i, m in enumerate(messages):
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise TypeError(
                    f"Element at index {i} must be a dict containing 'role' and 'content' keys."
                )

        backoff = self.initial_backoff
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Task 1: Deterministic Inference Dispatch
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    top_p=0.95,
                    max_tokens=1024,
                )

                choice = response.choices[0]
                answer = choice.message.content or ""
                prompt_tokens = response.usage.prompt_tokens if response.usage else 0
                completion_tokens = response.usage.completion_tokens if response.usage else 0
                model_used = response.model or self.model

                return LLMGenerationResultDTO(
                    raw_answer=answer,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model_name=model_used,
                )

            except (RateLimitError, InternalServerError, APIConnectionError, APITimeoutError) as e:
                last_exception = e
                # Task 2: Rate Limit & Exponential Retry
                if attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    raise LLMServiceError(
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

            except Exception as e:
                raise LLMServiceError(f"RAG_005: Unexpected LLM failure: {e}") from e

        raise LLMServiceError(
            f"RAG_005: OpenAI inference failed after {self.max_retries} retries: {last_exception}"
        )
