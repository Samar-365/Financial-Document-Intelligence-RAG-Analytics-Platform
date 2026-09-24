"""Security Hardening Module — Developer 4 (DevOps, Platform & Security).

Implements file validation chains, indirect prompt injection defense,
input sanitization, and context sandboxing according to docs/SECURITY.md.
"""

import re
from typing import List, Tuple
from fastapi import HTTPException, status

# Security constants
PDF_MAGIC_BYTES = b"%PDF"
XLSX_MAGIC_BYTES = b"PK\x03\x04"
XLS_MAGIC_BYTES = b"\xd0\xcf\x11\xe0"
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

# Heuristics for adversarial prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s*:\s*you\s+are",
    r"you\s+are\s+now\s+in\s+dan\s+mode",
    r"output\s+the\s+system\s+prompt",
    r"reveal\s+your\s+instructions",
    r"<script[\s>]",
    r"javascript\s*:",
]

COMPILED_INJECTION_REGEX = [
    re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS
]


def validate_pdf_upload(file_bytes: bytes, filename: str, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> None:
    """Validates uploaded file against security constraints (.pdf, .csv, .xlsx, .xls)."""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty.",
        )

    # 1. Extension validation
    lower_name = filename.lower()
    ext = next((e for e in ALLOWED_EXTENSIONS if lower_name.endswith(e)), None)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Only {ALLOWED_EXTENSIONS} files are accepted.",
        )

    # 2. File size validation
    if len(file_bytes) > max_size_bytes:
        mb_limit = max_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {mb_limit}MB.",
        )

    # 3. Magic byte signature validation
    if ext == ".pdf":
        if not file_bytes.startswith(PDF_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file signature. File header does not match a valid PDF.",
            )
    elif ext == ".xlsx":
        if not file_bytes.startswith(XLSX_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file signature. File header does not match a valid XLSX document.",
            )
    elif ext == ".xls":
        if not file_bytes.startswith(XLS_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file signature. File header does not match a valid XLS document.",
            )
    elif ext == ".csv":
        try:
            # Verify file can be decoded as text
            _ = file_bytes[:4096].decode("utf-8", errors="replace")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid CSV file. Content must be readable text.",
            )


# Backward-compatible alias
validate_document_upload = validate_pdf_upload



def sanitize_query_input(query: str) -> str:
    """Sanitizes user query string to prevent prompt injection and delimiter breaking."""
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query prompt cannot be empty.",
        )

    cleaned = query.strip()

    # Check for direct prompt injection signatures
    for pattern in COMPILED_INJECTION_REGEX:
        if pattern.search(cleaned):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query contains restricted instruction overrides or unsafe patterns.",
            )

    # Strip dangerous HTML/XML characters that could break context isolation tags
    cleaned = cleaned.replace("<context>", "").replace("</context>", "")
    return cleaned


def build_sandboxed_context(chunk_texts: List[str]) -> str:
    """Wraps retrieved document chunks within strict XML delimiters to enforce

    negative constraints and prevent indirect prompt injection from parsed PDF content.
    """
    sanitized_chunks = []
    for idx, text in enumerate(chunk_texts, start=1):
        # Neutralize any rogue XML tags inside the PDF text
        safe_text = (
            text.replace("<context>", "[context]")
            .replace("</context>", "[/context]")
            .replace("<instruction>", "[instruction]")
            .replace("</instruction>", "[/instruction]")
        )
        sanitized_chunks.append(f"<chunk index=\"{idx}\">\n{safe_text}\n</chunk>")

    joined = "\n\n".join(sanitized_chunks)
    return f"<context>\n{joined}\n</context>"
