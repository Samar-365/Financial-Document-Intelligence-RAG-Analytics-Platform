from unittest.mock import MagicMock
import pytest
from openai import APIConnectionError, RateLimitError
import httpx
from app.rag.llm_client import LLMGenerationResultDTO, LLMServiceError, OpenAIClientWrapper


def _make_mock_response(content: str = "Test answer", prompt_tokens: int = 150, completion_tokens: int = 40):
    mock_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = prompt_tokens
    mock_resp.usage.completion_tokens = completion_tokens
    mock_resp.model = "gpt-4o-mini"
    return mock_resp


def test_openai_initialization_defaults():
    """Verifies default parameters for OpenAIClientWrapper."""
    wrapper = OpenAIClientWrapper(api_key="test-key")
    assert wrapper.model == "gpt-4o-mini"
    assert wrapper.max_retries == 3
    assert wrapper.timeout == 30.0


def test_openai_deterministic_inference_dispatch_dod():
    """Verifies Task 1: Dispatches prompt to OpenAI GPT-4o-mini with deterministic parameters."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response(
        content="Fiscal 2025 revenue was $14.2B.",
        prompt_tokens=180,
        completion_tokens=25,
    )

    wrapper = OpenAIClientWrapper(client=mock_client, model="gpt-4o-mini")
    messages = [
        {"role": "system", "content": "You are a financial analyst."},
        {"role": "user", "content": "What was the revenue?"},
    ]

    result = wrapper.generate(messages)

    # Verify deterministic call arguments
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1,
        top_p=0.95,
        max_tokens=1024,
    )

    # Verify DTO structure
    assert isinstance(result, LLMGenerationResultDTO)
    assert result.raw_answer == "Fiscal 2025 revenue was $14.2B."
    assert result.prompt_tokens == 180
    assert result.completion_tokens == 25
    assert result.model_name == "gpt-4o-mini"


def test_openai_rate_limit_and_exponential_retry_dod():
    """Verifies Task 2 & Definition of Done (DoD):

    Retries up to 3 times on transient network/rate limit drops with backoff.
    """
    mock_client = MagicMock()
    mock_request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    mock_response_429 = httpx.Response(429, request=mock_request)

    rate_limit_err = RateLimitError(
        message="Rate limit exceeded",
        response=mock_response_429,
        body={"error": {"message": "Rate limit exceeded"}},
    )

    successful_resp = _make_mock_response(content="Recovered after retry.")

    # Fails twice with RateLimitError, then succeeds on 3rd attempt
    mock_client.chat.completions.create.side_effect = [
        rate_limit_err,
        rate_limit_err,
        successful_resp,
    ]

    wrapper = OpenAIClientWrapper(
        client=mock_client,
        max_retries=3,
        initial_backoff=0.01,  # Fast backoff for testing
    )

    messages = [{"role": "user", "content": "Test prompt"}]
    result = wrapper.generate(messages)

    assert result.raw_answer == "Recovered after retry."
    assert mock_client.chat.completions.create.call_count == 3


def test_openai_exhausted_retries_raises_llm_service_error():
    """Verifies that exceeding max_retries raises LLMServiceError (RAG_005)."""
    mock_client = MagicMock()
    conn_err = APIConnectionError(request=MagicMock())

    # Fails 4 times (1 initial + 3 retries)
    mock_client.chat.completions.create.side_effect = conn_err

    wrapper = OpenAIClientWrapper(
        client=mock_client,
        max_retries=3,
        initial_backoff=0.01,
    )

    messages = [{"role": "user", "content": "Test prompt"}]
    with pytest.raises(LLMServiceError, match="RAG_005"):
        wrapper.generate(messages)

    assert mock_client.chat.completions.create.call_count == 4


def test_openai_input_validation_errors():
    """Verifies parameter validation for generate()."""
    wrapper = OpenAIClientWrapper(client=MagicMock())

    with pytest.raises(TypeError, match="messages must be a list"):
        wrapper.generate("not a list")

    with pytest.raises(ValueError, match="messages list cannot be empty"):
        wrapper.generate([])

    with pytest.raises(TypeError, match="must be a dict containing 'role' and 'content'"):
        wrapper.generate([{"role": "user"}])  # missing content
