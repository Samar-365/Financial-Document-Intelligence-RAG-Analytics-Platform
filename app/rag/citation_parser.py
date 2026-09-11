"""Inline Citation Regex Parser for RAG pipeline (Module 5.1).

Responsible for:
1. Parsing inline bracketed citation markers using regex: r"\\[Doc:\\s*([^,]+),\\s*Page:\\s*(\\d+)\\]".
2. Deduplicating multiple identical page citations while strictly preserving first-occurrence order.
3. Packaging structured citation references into RawCitationToken DTOs.
"""

import re
from typing import List
from pydantic import BaseModel, Field


class RawCitationToken(BaseModel):
    """Data Transfer Object representing a raw inline document citation."""

    document_name: str = Field(
        ...,
        description="Name or identifier of the cited document.",
    )
    page_number: int = Field(
        ...,
        ge=1,
        description="Originating PDF page number (1-based integer).",
    )


class CitationParser:
    """Extracts and deduplicates inline citation markers from LLM-generated answers.

    Technical Tasks:
    1. Citation Token Extraction: Parse inline bracketed citation markers using regex.
    2. Citation Deduplication: Deduplicate multiple identical page citations, preserving first-occurrence order.
    """

    CITATION_PATTERN: re.Pattern = re.compile(
        r"\[Doc:\s*([^,]+?)\s*,\s*Page:\s*(\d+)\s*\]",
        re.IGNORECASE,
    )

    @staticmethod
    def parse_citations(text: str) -> List[RawCitationToken]:
        """Extracts unique [Doc: X, Page: Y] tokens from generated text.

        Preserves first-occurrence order of duplicate citations.

        Args:
            text: LLM-generated response string containing citation markers.

        Returns:
            List[RawCitationToken]: Ordered list of unique citation tokens.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string.")

        if not text.strip():
            return []

        tokens: List[RawCitationToken] = []
        seen = set()

        for match in CitationParser.CITATION_PATTERN.finditer(text):
            doc_name = match.group(1).strip()
            page_str = match.group(2).strip()

            try:
                page_number = int(page_str)
            except ValueError:
                continue

            dedup_key = (doc_name, page_number)
            if dedup_key not in seen:
                seen.add(dedup_key)
                tokens.append(
                    RawCitationToken(
                        document_name=doc_name,
                        page_number=page_number,
                    )
                )

        return tokens

    @staticmethod
    def strip_citations(text: str) -> str:
        """Removes inline [Doc: X, Page: Y] citation markers from text.

        Args:
            text: Text containing citation markers.

        Returns:
            str: Cleaned text without citation markers.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string.")

        cleaned = CitationParser.CITATION_PATTERN.sub("", text)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
        return cleaned.strip()
