"""Context Builder & Delimiter Sandboxing for RAG pipeline (Module 4.1).

Responsible for:
1. Wrapping retrieved chunks inside structural XML tags (<context>...</context>)
   to neutralize prompt injection instructions.
2. Formatting each chunk with its citation provenance tag: [Doc: {doc_id}, Page: {page_number}].
"""

from typing import List
from app.rag.retriever import RetrievedChunkDTO


class PromptBuilder: #Formats retrieved document chunks into delimited XML context blocks with citation markers
    """Formats retrieved document chunks into delimited XML context blocks with citation markers.

    Technical Tasks:
    1. XML Delimiter Isolation: Wrap retrieved chunks inside structural XML tags (<context>...</context>)
       to isolate retrieved data from system/user instructional prompts.
    2. Provenance Tag Formatting: Prepend each chunk with citation header [Doc: {document_id}, Page: {page_number}].
    """

    @staticmethod
    def build_context_block(chunks: List[RetrievedChunkDTO]) -> str: #Takes retrieved chunks and wraps them in delimited XML tags with citation provenance
        """Formats retrieved chunks into delimited XML context blocks with citation markers.

        Args:
            chunks: List of RetrievedChunkDTO objects returned by the retriever.

        Returns:
            str: XML-delimited context block containing formatted chunk excerpts.

        Raises:
            TypeError: If chunks is not a list or contains non-RetrievedChunkDTO objects.
        """
        if not isinstance(chunks, list): #Validates that chunks input is provided as a list
            raise TypeError("chunks must be a list of RetrievedChunkDTO objects.")

        if not chunks: #If no chunks were retrieved, return empty fallback context block
            return "<context>\nNo relevant context retrieved.\n</context>"

        formatted_chunks = [] #List to hold each individually formatted chunk
        for i, chunk in enumerate(chunks): #Iterate through each retrieved chunk
            if not isinstance(chunk, RetrievedChunkDTO): #Check that each item is a valid RetrievedChunkDTO
                raise TypeError(
                    f"Element at index {i} is {type(chunk).__name__}, expected RetrievedChunkDTO."
                )

            # Task 2: Provenance Tag Formatting
            header = f"[Doc: {chunk.document_id}, Page: {chunk.page_number}]" #Build citation tag: [Doc: name, Page: n]
            # Sanitize content to avoid escaping context tags
            cleaned_content = chunk.content.strip() #Strip unnecessary leading and trailing whitespace
            formatted_chunks.append(f"{header}\n{cleaned_content}") #Combine provenance tag with the chunk content

        # Task 1: XML Delimiter Isolation
        inner_content = "\n\n".join(formatted_chunks) #Separate multiple chunks with double newlines
        return f"<context>\n{inner_content}\n</context>" #Wrap the content inside <context> tags to sandbox against prompt injection
