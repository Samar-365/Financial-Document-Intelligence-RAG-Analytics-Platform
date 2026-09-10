import pytest
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import RetrievedChunkDTO
from app.rag.system_prompts import FinancialSystemPrompts


def test_standardized_fallback_string_dod():
    """Verifies Task 2: Exact standardized fallback token string."""
    expected_fallback = (
        "The provided document does not contain sufficient information to answer this query."
    )
    assert FinancialSystemPrompts.FALLBACK_RESPONSE == expected_fallback
    assert expected_fallback in FinancialSystemPrompts.RAG_SYSTEM_PROMPT


def test_system_prompt_strict_compliance_audit_dod():
    """Verifies the Definition of Done (DoD):

    Prompt passes audit for strict compliance, instructing model never to extrapolate or fabricate.
    """
    prompt = FinancialSystemPrompts.RAG_SYSTEM_PROMPT

    # Negative constraints audit
    assert "SOLELY" in prompt
    assert "EXCLUSIVELY" in prompt
    assert "Do NOT extrapolate" in prompt
    assert "Do NOT attempt to partially guess" in prompt
    assert "<context>" in prompt
    assert "page number" in prompt


def test_get_grounded_prompt_structure():
    """Verifies Task 1: Returns OpenAI-compatible messages list with system instructions and user context."""
    user_query = "What was the total revenue in fiscal year 2025?"
    context_block = "<context>\n[Doc: 10K, Page: 5]\nRevenue was $12B.\n</context>"

    messages = FinancialSystemPrompts.get_grounded_prompt(user_query, context_block)

    assert isinstance(messages, list)
    assert len(messages) == 2

    # Check system message
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == FinancialSystemPrompts.RAG_SYSTEM_PROMPT

    # Check user message
    assert messages[1]["role"] == "user"
    assert context_block in messages[1]["content"]
    assert f"Question: {user_query}" in messages[1]["content"]


def test_input_validation_errors():
    """Verifies parameter validation for get_grounded_prompt."""
    valid_context = "<context>sample</context>"

    with pytest.raises(ValueError, match="user_query cannot be empty or whitespace"):
        FinancialSystemPrompts.get_grounded_prompt("", valid_context)

    with pytest.raises(ValueError, match="user_query cannot be empty or whitespace"):
        FinancialSystemPrompts.get_grounded_prompt("   ", valid_context)

    with pytest.raises(TypeError, match="user_query must be a string"):
        FinancialSystemPrompts.get_grounded_prompt(12345, valid_context)

    with pytest.raises(TypeError, match="context_block must be a string"):
        FinancialSystemPrompts.get_grounded_prompt("Valid question", None)


def test_end_to_end_prompt_pipeline():
    """Verifies complete integration between PromptBuilder (4.1) and FinancialSystemPrompts (4.2)."""
    chunk1 = RetrievedChunkDTO(
        chunk_id="c-001",
        document_id="GOOGL-2025",
        chunk_index=0,
        page_number=12,
        content="Google Cloud revenue grew 29% to $11.4 billion.",
        similarity_score=0.88,
    )
    chunk2 = RetrievedChunkDTO(
        chunk_id="c-002",
        document_id="GOOGL-2025",
        chunk_index=1,
        page_number=14,
        content="Capital expenditures were $13 billion driven by technical infrastructure investments.",
        similarity_score=0.76,
    )

    # 1. Build context block
    context_block = PromptBuilder.build_context_block([chunk1, chunk2])

    # 2. Assemble grounded prompt payload
    query = "How much did Google Cloud revenue grow in 2025?"
    messages = FinancialSystemPrompts.get_grounded_prompt(query, context_block)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    user_prompt = messages[1]["content"]
    assert "<context>" in user_prompt
    assert "</context>" in user_prompt
    assert "[Doc: GOOGL-2025, Page: 12]" in user_prompt
    assert "Google Cloud revenue grew 29%" in user_prompt
    assert "[Doc: GOOGL-2025, Page: 14]" in user_prompt
    assert f"Question: {query}" in user_prompt
