"""Google Gemini API Client Wrapper for RAG and Financial Analytics.

Responsible for:
1. Deterministic inference dispatch to Google Gemini models (default: gemini-2.5-flash / gemini-1.5-flash)
   with temperature=0.1, top_p=0.95, and max_output_tokens=1024.
2. Handling rate limits (HTTP 429) & transient Google service errors with exponential backoff.
3. Converting OpenAI-compatible chat message payloads to Google Gemini system instructions and contents.
4. Packaging responses and token telemetry into LLMGenerationResultDTO.
"""

import os
import time
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


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


class GeminiClientWrapper:
    """Dispatches grounded prompts to Google Gemini API with deterministic parameters and retries."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.1,
        top_p: float = 0.95,
        max_output_tokens: int = 1024,
        max_retries: int = 3,
        initial_backoff: float = 0.5,
        timeout: float = 30.0,
        client: Optional[object] = None,
    ):
        """Initializes Gemini API client wrapper.

        Args:
            api_key: Google Gemini API key. Defaults to GEMINI_API_KEY or GOOGLE_API_KEY env vars.
            model: Gemini model identifier (default: 'gemini-2.5-flash').
            temperature: Deterministic sampling temperature (default: 0.1).
            top_p: Nucleus sampling parameter (default: 0.95).
            max_output_tokens: Max generated tokens (default: 1024).
            max_retries: Maximum exponential retry attempts (default: 3).
            initial_backoff: Initial seconds before retry backoff (default: 0.5s).
            timeout: Network timeout seconds.
            client: Optional injected mock client for unit testing.
        """
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or ""
        )
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_output_tokens
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.timeout = timeout
        self.client = client

        # Initialize official Google GenAI client if not mock-injected
        if self.client is None and self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self._sdk_type = "google-genai"
            except Exception:
                try:
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=self.api_key)
                    self.client = legacy_genai.GenerativeModel(model_name=self.model)
                    self._sdk_type = "google-generativeai"
                except Exception as exc:
                    logger.warning(f"Could not initialize Google GenAI SDK: {exc}")
                    self.client = None
                    self._sdk_type = "none"
        elif self.client is not None:
            self._sdk_type = "injected"
        else:
            self._sdk_type = "unconfigured"

    def _convert_messages(self, messages: List[Dict[str, str]]):
        """Converts OpenAI-style message dictionaries to Gemini format."""
        system_instruction = None
        user_parts = []

        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "")
            if role == "system":
                system_instruction = content
            elif role in ("user", "assistant"):
                user_parts.append(f"{role.upper()}: {content}")
            else:
                user_parts.append(content)

        combined_prompt = "\n\n".join(user_parts)
        return system_instruction, combined_prompt

    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Executes generation against Gemini API with retry handling and token calculation.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.

        Returns:
            LLMGenerationResultDTO: Raw completion text and token telemetry.
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

        if not self.api_key and self._sdk_type != "injected":
            raise LLMServiceError(
                "RAG_005: GEMINI_API_KEY is not configured in .env. "
                "Please configure GEMINI_API_KEY to enable Google Gemini AI features."
            )

        system_instruction, prompt_text = self._convert_messages(messages)
        backoff = self.initial_backoff
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # 1. Custom Injected Mock Support
                if self._sdk_type == "injected":
                    if hasattr(self.client, "generate"):
                        return self.client.generate(messages)
                    if hasattr(self.client, "chat") and hasattr(self.client.chat, "completions"):
                        # Injected OpenAI mock compatibility
                        resp = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            temperature=self.temperature,
                            top_p=self.top_p,
                            max_tokens=self.max_tokens,
                        )
                        return LLMGenerationResultDTO(
                            raw_answer=resp.choices[0].message.content or "",
                            prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
                            completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
                            model_name=self.model,
                        )

                # 2. google-genai (Official New SDK)
                if self._sdk_type == "google-genai":
                    from google.genai import types

                    config = types.GenerateContentConfig(
                        temperature=self.temperature,
                        top_p=self.top_p,
                        max_output_tokens=self.max_tokens,
                        system_instruction=system_instruction,
                    )
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt_text,
                        config=config,
                    )
                    text_answer = response.text or ""
                    prompt_tokens = 0
                    completion_tokens = 0
                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                        completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                    else:
                        prompt_tokens = len(prompt_text) // 4
                        completion_tokens = len(text_answer) // 4

                    return LLMGenerationResultDTO(
                        raw_answer=text_answer,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        model_name=self.model,
                    )

                # 3. google-generativeai (Legacy Fallback SDK)
                if self._sdk_type == "google-generativeai":
                    import google.generativeai as legacy_genai

                    model_instance = legacy_genai.GenerativeModel(
                        model_name=self.model,
                        system_instruction=system_instruction,
                    )
                    gen_config = {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "max_output_tokens": self.max_tokens,
                    }
                    response = model_instance.generate_content(
                        contents=prompt_text,
                        generation_config=gen_config,
                    )
                    text_answer = response.text or ""
                    prompt_tokens = len(prompt_text) // 4
                    completion_tokens = len(text_answer) // 4

                    return LLMGenerationResultDTO(
                        raw_answer=text_answer,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        model_name=self.model,
                    )

                raise LLMServiceError("RAG_005: Google GenAI client not initialized.")

            except Exception as e:
                last_exception = e
                # Transient error check (429, ResourceExhausted, 503, Connection error)
                err_str = str(e).lower()
                is_transient = any(
                    code in err_str
                    for code in ("429", "resource_exhausted", "quota", "503", "unavailable", "timeout")
                )

                if is_transient and attempt < self.max_retries:
                    logger.warning(
                        f"Transient Gemini API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    raise LLMServiceError(
                        f"RAG_005: Gemini API inference error: {e}"
                    ) from e

        raise LLMServiceError(
            f"RAG_005: Gemini inference failed after {self.max_retries} retries: {last_exception}"
        )
