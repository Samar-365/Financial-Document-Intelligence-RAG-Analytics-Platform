"""Context Builder & Delimiter Sandboxing for RAG pipeline (Module 4.1).

Responsible for:
1. Wrapping retrieved chunks inside structural XML tags (<context>...</context>)
   to neutralize prompt injection instructions.
2. Formatting each chunk with its citation provenance tag: [Doc: {doc_id}, Page: {page_number}].
"""

from typing import List
from app.rag.retriever import RetrievedChunkDTO


class PromptBuilder:
    """Formats retrieved document chunks into delimited XML context blocks with citation markers.

    Technical Tasks:
    1. XML Delimiter Isolation: Wrap retrieved chunks inside structural XML tags (<context>...</context>)
       to isolate retrieved data from system/user instructional prompts.
    2. Provenance Tag Formatting: Prepend each chunk with citation header [Doc: {document_id}, Page: {page_number}].
    """

    @staticmethod
    def build_context_block(chunks: List[RetrievedChunkDTO]) -> str:
        """Formats retrieved chunks into delimited XML context blocks with citation markers.

        Args:
            chunks: List of RetrievedChunkDTO objects returned by the retriever.

        Returns:
            str: XML-delimited context block containing formatted chunk excerpts.

        Raises:
            TypeError: If chunks is not a list or contains non-RetrievedChunkDTO objects.
        """
        if not isinstance(chunks, list):
            raise TypeError("chunks must be a list of RetrievedChunkDTO objects.")

        if not chunks:
            return "<context>\nNo relevant context retrieved.\n</context>"

        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            if not isinstance(chunk, RetrievedChunkDTO):
                raise TypeError(
                    f"Element at index {i} is {type(chunk).__name__}, expected RetrievedChunkDTO."
                )

            # Task 2: Provenance Tag Formatting
            header = f"[Doc: {chunk.document_id}, Page: {chunk.page_number}]"
            # Sanitize content to avoid escaping context tags
            cleaned_content = chunk.content.strip()
            formatted_chunks.append(f"{header}\n{cleaned_content}")

        # Task 1: XML Delimiter Isolation
        inner_content = "\n\n".join(formatted_chunks)
        return f"<context>\n{inner_content}\n</context>"
