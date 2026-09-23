"""Unit tests for GeminiClientWrapper."""
from unittest.mock import MagicMock
import pytest
from app.rag.gemini_client import (
    GeminiClientWrapper,
    LLMGenerationResultDTO,
    LLMServiceError,
)


def test_gemini_initialization_defaults():
    """Verifies default parameters for GeminiClientWrapper."""
    wrapper = GeminiClientWrapper(api_key="test-gemini-key")
    assert wrapper.model in ("gemini-2.5-flash", "gemini-1.5-flash")
    assert wrapper.temperature == 0.1
    assert wrapper.top_p == 0.95
    assert wrapper.max_tokens == 1024
    assert wrapper.max_retries == 3


def test_gemini_input_validation():
    """Verifies validation errors on invalid inputs."""
    wrapper = GeminiClientWrapper(api_key="test-key", client=MagicMock())

    with pytest.raises(TypeError, match="messages must be a list"):
        wrapper.generate("not a list")

    with pytest.raises(ValueError, match="messages list cannot be empty"):
        wrapper.generate([])

    with pytest.raises(TypeError, match="must be a dict"):
        wrapper.generate(["not a dict"])

    with pytest.raises(TypeError, match="containing 'role' and 'content'"):
        wrapper.generate([{"role": "user"}])


def test_gemini_mock_client_inference():
    """Verifies generation with injected mock client."""
    mock_client = MagicMock()
    mock_client.generate.return_value = LLMGenerationResultDTO(
        raw_answer="Revenue grew by 15% to $12.4B.",
        prompt_tokens=120,
        completion_tokens=30,
        model_name="gemini-2.5-flash",
    )

    wrapper = GeminiClientWrapper(api_key="test-key", client=mock_client)
    messages = [
        {"role": "system", "content": "You are a financial analyst."},
        {"role": "user", "content": "What was the revenue growth?"},
    ]

    result = wrapper.generate(messages)
    assert isinstance(result, LLMGenerationResultDTO)
    assert result.raw_answer == "Revenue grew by 15% to $12.4B."
    assert result.prompt_tokens == 120
    assert result.completion_tokens == 30
    assert result.model_name == "gemini-2.5-flash"


def test_gemini_missing_api_key_raises_error():
    """Verifies that missing GEMINI_API_KEY raises a clean LLMServiceError."""
    # Ensure no env var
    import os
    old_key = os.environ.pop("GEMINI_API_KEY", None)
    old_gkey = os.environ.pop("GOOGLE_API_KEY", None)
    try:
        wrapper = GeminiClientWrapper(api_key="")
        with pytest.raises(LLMServiceError, match="GEMINI_API_KEY is not configured"):
            wrapper.generate([{"role": "user", "content": "Test"}])
    finally:
        if old_key:
            os.environ["GEMINI_API_KEY"] = old_key
        if old_gkey:
            os.environ["GOOGLE_API_KEY"] = old_gkey
