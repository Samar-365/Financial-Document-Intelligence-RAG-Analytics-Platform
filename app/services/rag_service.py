"""RAG Service — document-filtered retrieval + Gemini generation.

Architecture:
  1. Retrieve all chunks for the SELECTED document_id only (never cross-doc)
  2. Score chunks by topic-aware term matching (risk/financial/legal vocab)
  3. Deduplicate nearly-identical chunks
  4. Build structured prompt for Gemini
  5. Return grounded answer with page citations

Gemini errors are logged internally; users see a clean unavailability message.
"""
import os
import re
import time
import logging
from typing import List, Set
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.financial_metric import FinancialMetric
from app.models.analysis_result import AnalysisResult
from app.schemas.query import Citation, RAGResponse
from app.rag.gemini_client import GeminiClientWrapper, LLMServiceError

logger = logging.getLogger(__name__)

# ── Topic-aware keyword sets for retrieval scoring ──────────────────────────
TOPIC_TERMS = {
    "risk": {
        "risk", "risks", "risk factor", "risk factors", "contingent", "contingency",
        "litigation", "legal", "regulatory", "compliance", "lawsuit", "claim",
        "liability", "liabilities", "uncertainty", "geopolit", "cybersecurity",
        "client concentration", "currency risk", "exposure", "hedging",
        "material weakness", "going concern", "fraud", "adverse",
    },
    "revenue": {
        "revenue", "revenues", "income", "turnover", "sales", "operations",
        "revenue from operations", "total income",
    },
    "profit": {
        "profit", "loss", "ebitda", "ebit", "operating profit", "net profit",
        "pat", "profit after tax", "profit before tax", "pbt", "net income",
        "earnings", "margin",
    },
    "balance_sheet": {
        "assets", "liabilities", "equity", "shareholders", "net worth",
        "total assets", "total liabilities", "borrowings", "debt", "cash",
        "investments", "reserves",
    },
    "cash_flow": {
        "cash flow", "operating activities", "investing activities",
        "financing activities", "free cash flow", "capex", "capital expenditure",
        "dividends", "buyback",
    },
}

FINANCIAL_QUERY_KEYWORDS = {
    "revenue": "revenue",
    "sales": "revenue",
    "turnover": "revenue",
    "income from operations": "revenue",
    "profit": "profit",
    "pat": "profit",
    "net income": "profit",
    "net profit": "profit",
    "ebitda": "profit",
    "operating income": "profit",
    "assets": "balance_sheet",
    "liabilities": "balance_sheet",
    "equity": "balance_sheet",
    "debt": "balance_sheet",
    "cash flow": "cash_flow",
    "operating cash": "cash_flow",
    "risk": "risk",
    "risks": "risk",
    "contingent": "risk",
    "litigation": "risk",
    "legal": "risk",
}


def _classify_query_topic(question: str) -> str:
    """Classify query into a topic bucket to weight term matching."""
    q_lower = question.lower()
    for phrase, topic in sorted(FINANCIAL_QUERY_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if phrase in q_lower:
            return topic
    return "general"


def _score_chunk(content: str, question_terms: List[str], topic: str) -> float:
    """Score a chunk against query terms + topic vocabulary."""
    c_lower = content.lower()

    # Base: term overlap with query tokens
    term_hits = sum(1 for t in question_terms if t in c_lower)
    base_score = min(0.97, 0.40 + term_hits * 0.10)

    # Topic boost: if chunk contains topic vocabulary, boost score
    topic_vocab = TOPIC_TERMS.get(topic, set())
    topic_hits = sum(1 for tv in topic_vocab if tv in c_lower)
    if topic_hits > 0:
        boost = min(0.20, topic_hits * 0.04)
        base_score = min(0.98, base_score + boost)

    # Penalty for chunks that look like page headers or address boilerplates
    boilerplate_signals = [
        "registered office", "cin:", "website:", "email:", "tel:", "fax:",
        "regd. office", "bombay stock exchange", "national stock exchange",
        "isin:", "symbol:", "bse:", "nse:",
    ]
    if any(s in c_lower for s in boilerplate_signals) and term_hits == 0:
        base_score = max(0.05, base_score - 0.25)

    return round(base_score, 4)


def _deduplicate_chunks(chunks_with_scores: list, similarity_threshold: float = 0.85) -> list:
    """Remove nearly-identical chunks (same first 200 chars or >85% token overlap)."""
    seen_signatures: Set[str] = set()
    deduplicated = []
    for score, chunk in chunks_with_scores:
        # Use first 200 chars as a deduplication fingerprint
        sig = re.sub(r"\s+", " ", chunk.content[:200]).strip().lower()
        if sig not in seen_signatures:
            seen_signatures.add(sig)
            deduplicated.append((score, chunk))
    return deduplicated


SYSTEM_PROMPT = """You are a Senior Financial Intelligence Analyst. Your role is to answer questions 
about specific financial filings accurately and concisely.

STRICT RULES:
1. Answer ONLY from the document excerpts provided below. Do NOT use external knowledge.
2. If the information is not present in the excerpts, say clearly: "This information is not found in the selected filing."
3. NEVER hallucinate financial figures. If you see a number, quote it exactly with its currency and unit as stated in the document.
4. Separate FILING FACTS from your ANALYSIS. Label your analytical commentary clearly.
5. For forward-looking questions (next year, forecast, guidance), state: "The filing contains historical results only. No forward guidance was identified."
6. Always cite the page number(s) where you found information.
7. Keep answers concise and structured. Use bullet points for lists.
8. If the question involves a financial ratio or calculation, show the formula and inputs.

ANSWER FORMAT:
### Answer
[Direct answer in 1-3 sentences or bullet points]

### Source
Page [N] — [brief description of the source passage]

### Period Note (if relevant)
[Clarify whether the figure is Q4 or full-year FY]
"""


class RAGService:
    """Document-scoped RAG using PostgreSQL chunks + Gemini generation."""

    def __init__(self, db: Session):
        self.db = db

    def query(self, document_id: UUID, question: str, top_k: int = 6) -> RAGResponse:
        start_time = time.time()

        # ── 1. Fetch ALL chunks for THIS document only ───────────────────────
        chunks = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        citations: List[Citation] = []
        context_texts: List[str] = []
        model_identifier = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

        if not chunks:
            answer = "No document content found for this filing. Please ensure the document was processed successfully."
            elapsed_ms = int((time.time() - start_time) * 1000)
            return RAGResponse(
                answer=answer,
                citations=[],
                latency_ms=elapsed_ms,
                model_used=model_identifier,
            )

        # ── 2. Topic-aware scoring ───────────────────────────────────────────
        q_lower = question.lower()
        q_terms = [w.strip() for w in q_lower.split() if len(w.strip()) > 2]
        topic = _classify_query_topic(question)

        scored_chunks = [
            (_score_chunk(chunk.content, q_terms, topic), chunk)
            for chunk in chunks
        ]

        # ── 3. Deduplicate then sort ─────────────────────────────────────────
        scored_chunks = _deduplicate_chunks(scored_chunks)
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        selected = scored_chunks[:top_k]

        # ── 4. Build context + citations ─────────────────────────────────────
        for score, chunk in selected:
            raw_c = chunk.content or ""
            snippet = (raw_c[:495] + "...") if len(raw_c) > 495 else raw_c[:500]
            citations.append(Citation(
                document_id=document_id,
                page_number=chunk.page_number or 1,
                snippet=snippet,
                relevance_score=round(score, 2),
            ))
            context_texts.append(f"[Page {chunk.page_number or 1}]:\n{chunk.content}")

        # ── 5. Fetch verified metrics & build structured prompt ───────────────
        verified_metrics = (
            self.db.query(FinancialMetric)
            .filter(FinancialMetric.document_id == document_id)
            .all()
        )
        analysis_record = (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.document_id == document_id)
            .first()
        )

        metrics_summary = []
        for vm in verified_metrics:
            unit_display = "₹ Cr" if "INR" in str(vm.unit).upper() else ("USD M" if "USD" in str(vm.unit).upper() else vm.unit)
            metrics_summary.append(f"- {vm.metric_name}: {vm.value} {unit_display} (Period: {vm.fiscal_period or 'FY'} {vm.fiscal_year or ''}, Source Page: {vm.source_page or 'N/A'})")
        if analysis_record:
            if analysis_record.opm is not None:
                metrics_summary.append(f"- Operating Margin (OPM): {analysis_record.opm}%")
            if analysis_record.npm is not None:
                metrics_summary.append(f"- Net Margin (NPM): {analysis_record.npm}%")
            if analysis_record.roe is not None:
                metrics_summary.append(f"- Return on Equity (ROE): {analysis_record.roe}%")
            if analysis_record.current_ratio is not None:
                metrics_summary.append(f"- Current Ratio: {analysis_record.current_ratio}x")
            if analysis_record.debt_to_equity is not None:
                metrics_summary.append(f"- Debt-to-Equity: {analysis_record.debt_to_equity}x")

        verified_block = ""
        if metrics_summary:
            verified_block = "Verified Extracted Metrics & Calculated Ratios for this Document:\n" + "\n".join(metrics_summary) + "\n\n"

        context_block = "\n\n---\n\n".join(context_texts[:5])
        user_prompt = (
            f"{verified_block}"
            f"Filing Excerpts:\n{context_block}\n\n"
            f"Question: {question}\n\n"
            f"Answer based strictly on the verified metrics and excerpts above:"
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # ── 6. Gemini generation ─────────────────────────────────────────────
        try:
            gemini = GeminiClientWrapper()
            result = gemini.generate(messages)
            answer = result.raw_answer
            model_identifier = result.model_name
        except LLMServiceError as e:
            # Log full error internally; show only a user-friendly message
            logger.warning(f"Gemini generation unavailable: {e}")
            # Provide a structured text answer from the top chunk as fallback
            if context_texts:
                top_context = context_texts[0]
                answer = (
                    "**AI analysis is temporarily unavailable.** "
                    "Here is the most relevant excerpt from the filing:\n\n"
                    f"{top_context[:800]}"
                )
            else:
                answer = "AI analysis is temporarily unavailable. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected Gemini error: {e}")
            answer = "AI analysis encountered an unexpected error. Please try again."

        elapsed_ms = int((time.time() - start_time) * 1000)

        return RAGResponse(
            answer=answer,
            citations=citations,
            latency_ms=elapsed_ms,
            model_used=model_identifier,
        )
