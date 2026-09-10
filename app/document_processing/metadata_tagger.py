import math
from typing import List, Tuple
import uuid
from pydantic import BaseModel, Field


class TextChunkDTO(BaseModel):
    """Data Transfer Object representing an enriched document text chunk with complete provenance."""

    chunk_id: str = Field(
        ...,
        description="Unique UUIDv4 identifying the text chunk.",
    )
    document_id: str = Field(
        ...,
        description="Identifier of the originating parent document.",
    )
    chunk_index: int = Field(
        ...,
        ge=0,
        description="0-based sequential index of the chunk across the document.",
    )
    page_number: int = Field(
        ...,
        ge=1,
        description="1-based page number from which the chunk originated.",
    )
    content: str = Field(
        ...,
        description="Text content of the chunk, including preserved markdown structures.",
    )
    token_estimate: int = Field(
        ...,
        ge=0,
        description="Estimated token count using the 4-characters-per-token heuristic.",
    )
    is_table_chunk: bool = Field(
        ...,
        description="Boolean flag indicating whether the chunk contains tabular markdown structures.",
    )


class MetadataTagger:
    """Tags raw document chunks with unique identifiers, page provenance, token counts, and structural flags.

    Technical Tasks:
    1. Provenance Metadata Assembly: Packages each chunk into TextChunkDTO with UUIDv4, document_id,
       sequential chunk_index, and validated page_number.
    2. Token Count Estimation & Table Tagging: Computes estimated token count via 4-character heuristic
       and flags markdown tabular blocks with is_table_chunk.
    """

    @staticmethod
    def _is_table_content(content: str) -> bool:
        """Determines if the chunk content contains markdown table syntax."""
        if "|" not in content:
            return False
        for line in content.splitlines():
            s = line.strip()
            if s.startswith("|") and s.endswith("|") and len(s) > 1:
                return True
        return False

    def tag_chunks(
        self,
        document_id: str,
        page_chunks: List[Tuple[int, str]],
    ) -> List[TextChunkDTO]:
        """Tags chunks with UUID, document ID, page provenance, and token estimates.

        Args:
            document_id: Unique identifier for the document being processed.
            page_chunks: List of tuples containing (page_number, chunk_text).

        Returns:
            List of fully tagged TextChunkDTO instances.

        Raises:
            ValueError: If document_id is empty or if any page_number is less than 1.
        """
        if not document_id or not document_id.strip():
            raise ValueError("document_id must be a non-empty string.")

        tagged_chunks: List[TextChunkDTO] = []

        for chunk_idx, (page_number, content) in enumerate(page_chunks):
            if page_number < 1:
                raise ValueError(
                    f"Invalid page_number {page_number} at index {chunk_idx}. Page numbers must be >= 1."
                )

            chunk_id = str(uuid.uuid4())
            token_est = (
                max(1, math.ceil(len(content) / 4.0)) if content and len(content.strip()) > 0 else 0
            )
            is_table = self._is_table_content(content)

            chunk_dto = TextChunkDTO(
                chunk_id=chunk_id,
                document_id=document_id.strip(),
                chunk_index=chunk_idx,
                page_number=page_number,
                content=content,
                token_estimate=token_est,
                is_table_chunk=is_table,
            )
            tagged_chunks.append(chunk_dto)

        return tagged_chunks
