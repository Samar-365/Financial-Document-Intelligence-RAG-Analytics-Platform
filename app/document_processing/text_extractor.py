import os
from typing import List
from pydantic import BaseModel, Field
import pypdf


class ScannedPDFError(Exception):
    """Raised when an uploaded document contains no extractable digital text stream (PROC_002)."""

    def __init__(
        self,
        message: str = "PROC_002: Scanned PDF requiring OCR. Zero extractable characters detected.",
        error_code: str = "PROC_002",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class ExtractedPageTextDTO(BaseModel):
    """Data Transfer Object capturing page-level extracted narrative text."""

    page_number: int = Field(
        ...,
        ge=1,
        description="1-based sequential page number within the source document.",
    )
    raw_text: str = Field(
        ...,
        description="Raw narrative and numeric character text extracted from the page.",
    )
    char_count: int = Field(
        ...,
        ge=0,
        description="Total number of characters extracted from the page.",
    )


class TextExtractor:
    """Extractor responsible for page-by-page digital text harvesting and scanned document detection."""

    def extract_text_by_page(self, file_path: str) -> List[ExtractedPageTextDTO]:
        """Extracts digital narrative text page by page with character density checks.

        Technical Tasks Performed:
        1. Page-by-Page Narrative Extraction: Iterates through each document page, extracts digital text
           stream using pypdf, and records sequential 1-indexed page metadata.
        2. Scanned Document Detection: Aggregates total document character count; if an entire document
           yields 0 extractable characters, aborts and raises ScannedPDFError (PROC_002).

        Args:
            file_path: Absolute or relative system path to the target PDF file.

        Returns:
            List[ExtractedPageTextDTO]: List of extracted pages with text, character counts, and page indices.

        Raises:
            FileNotFoundError: If the specified file path does not exist.
            ScannedPDFError: If the document contains zero extractable digital text (PROC_002).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        reader = pypdf.PdfReader(file_path)
        pages_output: List[ExtractedPageTextDTO] = []
        total_extracted_chars = 0

        for idx, page in enumerate(reader.pages, start=1):
            extracted = page.extract_text() or ""
            # Strip trailing/leading excess whitespace for accurate count
            cleaned_text = extracted.strip()
            char_count = len(cleaned_text)
            total_extracted_chars += char_count

            pages_output.append(
                ExtractedPageTextDTO(
                    page_number=idx,
                    raw_text=extracted,
                    char_count=char_count,
                )
            )

        # Task 2: Scanned Document Detection - Check if entire document has 0 extractable characters
        if total_extracted_chars == 0:
            raise ScannedPDFError(
                message=f"PROC_002: Scanned PDF requiring OCR. Document '{os.path.basename(file_path)}' contains {len(reader.pages)} page(s) with 0 extractable text characters."
            )

        return pages_output
