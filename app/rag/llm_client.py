"""LLM Client Adapter & Wrappers (Google Gemini & OpenAI).

Primary Provider: Google Gemini API (gemini-2.5-flash)
Fallback / Secondary: OpenAI & Local Ollama
"""

import os
import time
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.rag.gemini_client import (
    GeminiClientWrapper,
    LLMGenerationResultDTO,
    LLMServiceError,
)

logger = logging.getLogger(__name__)

# Expose primary client
PrimaryLLMClient = GeminiClientWrapper


class OpenAIClientWrapper:
    """OpenAI GPT client wrapper with seamless Gemini failover/dispatch capability."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        initial_backoff: float = 0.5,
        timeout: float = 30.0,
        client: Optional[object] = None,
    ):
        self.model = model
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.timeout = timeout
        self.client = client
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

        # Check if Google Gemini should be used as the preferred or fallback provider
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._use_gemini = bool(self.gemini_key and (not self.api_key or self.api_key == "dummy-key-for-local-init"))
        
        if self._use_gemini and self.client is None:
            self._gemini_client = GeminiClientWrapper(
                api_key=self.gemini_key,
                max_retries=max_retries,
                initial_backoff=initial_backoff,
                timeout=timeout,
            )
        else:
            self._gemini_client = None

        if self.client is None and not self._use_gemini:
            try:
                from openai import OpenAI
                resolved_key = self.api_key or "dummy-key-for-local-init"
                self.client = OpenAI(api_key=resolved_key, timeout=self.timeout)
            except Exception as e:
                logger.warning(f"OpenAI SDK initialization note: {e}")
                self.client = None

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Dispatches chat prompt, routing to Gemini or OpenAI."""
        if not isinstance(messages, list):
            raise TypeError("messages must be a list of dictionaries.")
        if not messages:
            raise ValueError("messages list cannot be empty.")
        for i, m in enumerate(messages):
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise TypeError(
                    f"Element at index {i} must be a dict containing 'role' and 'content' keys."
                )

        # Route to Gemini if active
        if self._use_gemini and self._gemini_client:
            return self._gemini_client.generate(messages)

        if self.client is None:
            # Fall back to Gemini if available
            if self.gemini_key:
                gemini = GeminiClientWrapper(api_key=self.gemini_key)
                return gemini.generate(messages)
            raise LLMServiceError("RAG_005: Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured.")

        # Dispatches to OpenAI
        backoff = self.initial_backoff
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
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
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    # Attempt Gemini fallback on permanent OpenAI failure
                    if self.gemini_key:
                        try:
                            gemini = GeminiClientWrapper(api_key=self.gemini_key)
                            return gemini.generate(messages)
                        except Exception:
                            pass
                    raise LLMServiceError(
                        f"RAG_005: LLM service error after {self.max_retries} retries: {e}"
                    ) from e

        raise LLMServiceError(f"RAG_005: LLM inference failed: {last_exception}")
