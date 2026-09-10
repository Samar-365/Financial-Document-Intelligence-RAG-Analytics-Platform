from unittest.mock import MagicMock
import pytest
import requests
from app.rag.llm_client import LLMGenerationResultDTO, LLMServiceError
from app.rag.ollama_client import (
    HybridLLMDispatcher,
    OllamaClientWrapper,
    OllamaServiceError,
)


def test_ollama_initialization_defaults():
    """Verifies default parameters for OllamaClientWrapper."""
    client = OllamaClientWrapper()
    assert client.host == "http://localhost:11434"
    assert client.model == "llama3"
    assert client.timeout == 30.0


def test_ollama_rest_integration_dod():
    """Verifies Task 1: Queries local Ollama instance (/api/chat) for inference."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3",
        "message": {"role": "assistant", "content": "Free cash flow for Q4 was $850M."},
        "prompt_eval_count": 95,
        "eval_count": 22,
    }
    mock_session.post.return_value = mock_response

    client = OllamaClientWrapper(host="http://localhost:11434", model="llama3", session=mock_session)
    messages = [{"role": "user", "content": "What was the free cash flow?"}]

    result = client.generate(messages)

    # Verify REST endpoint and payload
    mock_session.post.assert_called_once_with(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3",
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.95,
                "num_predict": 1024,
            },
        },
        timeout=30.0,
    )

    assert isinstance(result, LLMGenerationResultDTO)
    assert result.raw_answer == "Free cash flow for Q4 was $850M."
    assert result.prompt_tokens == 95
    assert result.completion_tokens == 22
    assert result.model_name == "llama3"


def test_ollama_connection_error_raises_service_error():
    """Verifies connection failure to local Ollama daemon raises OllamaServiceError."""
    mock_session = MagicMock()
    mock_session.post.side_effect = requests.exceptions.ConnectionError("Connection refused")

    client = OllamaClientWrapper(session=mock_session)
    with pytest.raises(OllamaServiceError, match="RAG_005"):
        client.generate([{"role": "user", "content": "Hello"}])


def test_automatic_failover_switch_dod():
    """Verifies Task 2 & Definition of Done (DoD):

    System returns complete answers when internet access is disabled / OpenAI fails.
    """
    mock_openai = MagicMock()
    # OpenAI fails permanently with service error (simulating network down / no internet)
    mock_openai.generate.side_effect = LLMServiceError("RAG_005: Internet access disabled")

    mock_ollama = MagicMock()
    mock_ollama.generate.return_value = LLMGenerationResultDTO(
        raw_answer="Fallback answer from local Ollama model.",
        prompt_tokens=110,
        completion_tokens=18,
        model_name="llama3",
    )

    dispatcher = HybridLLMDispatcher(
        openai_client=mock_openai,
        ollama_client=mock_ollama,
        air_gapped_mode=False,
    )

    messages = [{"role": "user", "content": "Analyze debt ratios."}]
    result = dispatcher.generate(messages)

    # Both clients called: primary failed, fallback succeeded
    mock_openai.generate.assert_called_once_with(messages)
    mock_ollama.generate.assert_called_once_with(messages)

    assert result.raw_answer == "Fallback answer from local Ollama model."
    assert result.model_name == "llama3"


def test_hybrid_dispatcher_air_gapped_mode_bypass():
    """Verifies that AIR_GAPPED_MODE routes directly to Ollama without attempting OpenAI."""
    mock_openai = MagicMock()
    mock_ollama = MagicMock()
    mock_ollama.generate.return_value = LLMGenerationResultDTO(
        raw_answer="Air-gapped response.",
        prompt_tokens=50,
        completion_tokens=10,
        model_name="mistral",
    )

    dispatcher = HybridLLMDispatcher(
        openai_client=mock_openai,
        ollama_client=mock_ollama,
        air_gapped_mode=True,
    )

    messages = [{"role": "user", "content": "Classified financial query."}]
    result = dispatcher.generate(messages)

    # OpenAI must NOT have been called
    mock_openai.generate.assert_not_called()
    mock_ollama.generate.assert_called_once_with(messages)
    assert result.raw_answer == "Air-gapped response."


def test_ollama_input_validation():
    """Verifies parameter validation for Ollama generate()."""
    client = OllamaClientWrapper(session=MagicMock())

    with pytest.raises(TypeError, match="messages must be a list"):
        client.generate("invalid string")

    with pytest.raises(ValueError, match="messages list cannot be empty"):
        client.generate([])

    with pytest.raises(TypeError, match="must be a dict containing 'role' and 'content'"):
        client.generate([{"role": "user"}])
