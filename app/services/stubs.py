"""Temporary stubs until Dev 1's real services land in Sprint 2."""
from typing import Any, Dict


def rag_query_stub(document_id: str, question: str) -> Dict[str, Any]:
    return {
        "answer": f"[STUB] Answer for: {question[:80]}",
        "citations": [],
        "latency_ms": 0,
        "model_used": "stub",
    }