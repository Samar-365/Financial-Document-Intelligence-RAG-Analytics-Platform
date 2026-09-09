"""Document processing, text extraction, table extraction, and normalization package."""

from app.document_processing.validator import PDFValidator, ValidationResultDTO
from app.document_processing.text_extractor import (
    TextExtractor,
    ExtractedPageTextDTO,
    ScannedPDFError,
)

__all__ = [
    "PDFValidator",
    "ValidationResultDTO",
    "TextExtractor",
    "ExtractedPageTextDTO",
    "ScannedPDFError",
]
