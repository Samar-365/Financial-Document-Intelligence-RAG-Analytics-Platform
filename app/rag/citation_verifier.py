"""Provenance Verification & Snippet Mapper for RAG pipeline (Module 5.2).

Responsible for:
1. Cross-referencing cited page numbers and document names against Top-K retrieved chunks.
2. Flagging phantom citations (citations referencing nonexistent or unretrieved pages/documents).
3. Extracting exact verifiable sentence snippets from source chunks for UI citation cards.
"""

import re
import uuid
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from app.rag.citation_parser import CitationParser, RawCitationToken
from app.rag.retriever import RetrievedChunkDTO


class VerifiedCitationDTO(BaseModel):
    """Data Transfer Object representing a verified document citation with evidence snippet."""

    citation_id: str = Field(
        ...,
        description="Unique identifier for this citation instance.",
    )
    document_name: str = Field(
        ...,
        description="Name or identifier of the cited document.",
    )
    page_number: int = Field(
        ...,
        ge=1,
        description="Cited page number.",
    )
    source_snippet: str = Field(
        default="",
        description="Verifiable evidence sentence extracted from the source chunk.",
    )
    is_verified: bool = Field(
        ...,
        description="True if cited page and document exist in retrieved chunks; False if phantom.",
    )


class CitationVerifier:
    """Validates citations against retrieved chunks and extracts text evidence snippets.

    Technical Tasks:
    1. Retrieved Chunk Cross-Referencing: Verify that cited page numbers exist in Top-K retrieved chunks.
       Flag phantom citations with is_verified=False.
    2. Evidence Snippet Extraction: Extract the exact sentence from the source chunk to serve
       as verifiable proof in UI citation cards.
    """

    @staticmethod
    def _extract_evidence_snippet(
        chunks: List[RetrievedChunkDTO],
        claim_context: Optional[str] = None,
    ) -> str:
        """Extracts the most relevant evidence sentence from candidate matching chunks.

        Args:
            chunks: List of retrieved chunks matching the cited document and page.
            claim_context: Optional surrounding claim or answer text to align evidence.

        Returns:
            str: Cleaned sentence or excerpt representing verifiable evidence.
        """
        if not chunks:
            return ""

        # Gather candidate sentences/rows across all matching chunks
        candidates: List[str] = []
        for chunk in chunks:
            content = chunk.content.strip()
            if not content:
                continue

            # If the chunk is primarily a markdown table, extract relevant table rows
            if "|" in content and content.count("\n") > 0:
                rows = [
                    row.strip()
                    for row in content.splitlines()
                    if row.strip().startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", row.strip())
                ]
                # Filter out header separator row and add table rows
                candidates.extend(rows)

            # Split narrative content into sentences
            sentences = re.split(r"(?<=[.!?])\s+", content)
            for sent in sentences:
                cleaned = sent.strip()
                if len(cleaned) >= 15:  # Ignore trivial fragments
                    candidates.append(cleaned)

        if not candidates:
            # Fallback to trimmed chunk content
            return chunks[0].content.strip()[:200]

        # If claim_context is provided, rank candidates by token overlap
        if claim_context and claim_context.strip():
            claim_tokens: Set[str] = set(
                re.findall(r"[A-Za-z0-9]+", claim_context.lower())
            )
            # Remove common stopwords to focus on factual terms
            stopwords = {"the", "a", "an", "is", "in", "and", "of", "to", "for", "with", "that", "this", "it", "was"}
            claim_keywords = claim_tokens - stopwords

            best_candidate = candidates[0]
            max_overlap = -1

            for candidate in candidates:
                cand_tokens = set(re.findall(r"[A-Za-z0-9]+", candidate.lower()))
                overlap = len(cand_tokens & claim_keywords)
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_candidate = candidate

            if max_overlap > 0:
                return best_candidate

        # Default to first complete candidate sentence
        return candidates[0]

    def verify_citations(
        self,
        tokens: List[RawCitationToken],
        retrieved_chunks: List[RetrievedChunkDTO],
        claim_context: Optional[str] = None,
    ) -> List[VerifiedCitationDTO]:
        """Cross-references citations against retrieved chunks and extracts text evidence.

        Args:
            tokens: List of RawCitationToken objects extracted from LLM response.
            retrieved_chunks: List of RetrievedChunkDTO objects retrieved for the query.
            claim_context: Optional claim text to align relevant evidence snippet.

        Returns:
            List[VerifiedCitationDTO]: Verified and flagged citation records.

        Raises:
            TypeError: If tokens or retrieved_chunks are not lists of expected DTOs.
        """
        if not isinstance(tokens, list):
            raise TypeError("tokens must be a list of RawCitationToken objects.")

        if not isinstance(retrieved_chunks, list):
            raise TypeError("retrieved_chunks must be a list of RetrievedChunkDTO objects.")

        for i, token in enumerate(tokens):
            if not isinstance(token, RawCitationToken):
                raise TypeError(
                    f"Element at tokens[{i}] is {type(token).__name__}, expected RawCitationToken."
                )

        for i, chunk in enumerate(retrieved_chunks):
            if not isinstance(chunk, RetrievedChunkDTO):
                raise TypeError(
                    f"Element at retrieved_chunks[{i}] is {type(chunk).__name__}, expected RetrievedChunkDTO."
                )

        if not tokens:
            return []

        # Build index mapping (document_name_lower, page_number) -> list of chunks
        chunk_index: Dict[Tuple[str, int], List[RetrievedChunkDTO]] = {}
        for chunk in retrieved_chunks:
            key = (chunk.document_id.strip().lower(), chunk.page_number)
            chunk_index.setdefault(key, []).append(chunk)

        verified_results: List[VerifiedCitationDTO] = []

        for token in tokens:
            lookup_key = (token.document_name.strip().lower(), token.page_number)
            matching_chunks = chunk_index.get(lookup_key, [])

            cid = f"cite-{uuid.uuid4().hex[:8]}"

            if matching_chunks:
                # Task 2: Extract verifiable evidence snippet from source chunk
                snippet = self._extract_evidence_snippet(
                    matching_chunks,
                    claim_context=claim_context,
                )
                verified_results.append(
                    VerifiedCitationDTO(
                        citation_id=cid,
                        document_name=token.document_name,
                        page_number=token.page_number,
                        source_snippet=snippet,
                        is_verified=True,
                    )
                )
            else:
                # Task 1: Flag phantom citation (no matching chunk retrieved)
                verified_results.append(
                    VerifiedCitationDTO(
                        citation_id=cid,
                        document_name=token.document_name,
                        page_number=token.page_number,
                        source_snippet="",
                        is_verified=False,
                    )
                )

        return verified_results

    def verify_answer(
        self,
        generated_text: str,
        retrieved_chunks: List[RetrievedChunkDTO],
    ) -> List[VerifiedCitationDTO]:
        """Convenience method: parses citations from generated text and verifies them against retrieved chunks.

        Args:
            generated_text: LLM-generated response containing inline citation markers.
            retrieved_chunks: Top-K retrieved chunks passed as context.

        Returns:
            List[VerifiedCitationDTO]: Verified and flagged citation records.
        """
        if not isinstance(generated_text, str):
            raise TypeError("generated_text must be a string.")

        tokens = CitationParser.parse_citations(generated_text)
        return self.verify_citations(
            tokens=tokens,
            retrieved_chunks=retrieved_chunks,
            claim_context=generated_text,
        )
