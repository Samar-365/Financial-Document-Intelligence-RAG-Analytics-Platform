import os
import re
from typing import Optional
from pydantic import BaseModel, Field
import pypdf

# Maximum permissible document size: 50 Megabytes (50 * 1024 * 1024 bytes)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

# Regular expression pattern to validate and extract PDF specification version
PDF_HEADER_PATTERN = re.compile(r"^%PDF-(\d+\.\d+)")


class ValidationResultDTO(BaseModel):
    """Data Transfer Object representing the outcome of document pre-flight validation."""

    is_valid: bool = Field(
        ...,
        description="Indicates whether the document satisfies all integrity and security rules.",
    )
    file_size_bytes: int = Field(
        ...,
        ge=0,
        description="Total size of the verified file in bytes.",
    )
    pdf_version: str = Field(
        default="",
        description="Extracted PDF specification version (e.g., '1.4', '1.7'). Empty string if invalid.",
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Standardized error code (e.g., DOC_000, DOC_001, DOC_002, DOC_003) if validation failed.",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of the validation failure.",
    )


class PDFValidator:
    """Validator responsible for pre-flight boundary, magic byte, and encryption checks on incoming PDFs."""

    @staticmethod
    def validate_file(file_path: str) -> ValidationResultDTO:
        """Validates PDF magic bytes, file size, corruption, and encryption status.

        Technical Tasks Performed:
        1. Magic-Byte Inspection: Inspects the initial bytes to confirm %PDF-1.x / %PDF-2.x header signature.
           Rejects spoofed or non-PDF files with error DOC_001.
        2. Size & Encryption Check: Enforces a strict 50 MB limit (DOC_003) and detects password protection
           or encryption (DOC_002).

        Args:
            file_path: Absolute or relative system path to the target PDF file.

        Returns:
            ValidationResultDTO: Structured result containing validity flag, size, version, and error details.
        """
        # Step 0: Verify file existence and accessibility
        if not os.path.exists(file_path):
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=0,
                pdf_version="",
                error_code="DOC_000",
                error_message=f"File not found: '{file_path}' does not exist on disk.",
            )

        if not os.path.isfile(file_path):
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=0,
                pdf_version="",
                error_code="DOC_000",
                error_message=f"Invalid target: '{file_path}' is not a regular file.",
            )

        # Step 1: File size boundary check
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=file_size,
                pdf_version="",
                error_code="DOC_003",
                error_message=(
                    f"File size limit exceeded: {file_size} bytes exceeds maximum allowed "
                    f"limit of {MAX_FILE_SIZE_BYTES} bytes (50 MB)."
                ),
            )

        if file_size == 0:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=0,
                pdf_version="",
                error_code="DOC_001",
                error_message="Invalid file format: File is empty (0 bytes).",
            )

        # Step 2: Magic-Byte inspection (first 1024 bytes to locate %PDF header)
        try:
            with open(file_path, "rb") as f:
                header_bytes = f.read(1024)
        except (IOError, PermissionError) as exc:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=file_size,
                pdf_version="",
                error_code="DOC_000",
                error_message=f"File access error: Unable to read file header ({exc}).",
            )

        # PDF header signature check: %PDF-x.y
        # According to PDF specifications, the %PDF- header usually starts at byte 0, but can appear within the first 1024 bytes.
        header_text = header_bytes.decode("latin1", errors="ignore")
        match = re.search(r"%PDF-(\d+\.\d+)", header_text)

        if not match:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=file_size,
                pdf_version="",
                error_code="DOC_001",
                error_message="Invalid file format: Header does not match PDF magic-byte specification (%PDF-1.x).",
            )

        pdf_version = match.group(1)

        # Step 3: Encryption and structural integrity inspection
        try:
            reader = pypdf.PdfReader(file_path)
            if reader.is_encrypted:
                return ValidationResultDTO(
                    is_valid=False,
                    file_size_bytes=file_size,
                    pdf_version=pdf_version,
                    error_code="DOC_002",
                    error_message="Encrypted document: Password-protected or encrypted PDFs are not supported.",
                )

            # Access page count to verify document structure is intact and uncorrupted
            _ = len(reader.pages)

        except pypdf.errors.PdfReadError as exc:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=file_size,
                pdf_version=pdf_version,
                error_code="DOC_001",
                error_message=f"Corrupted PDF structure: Unable to parse document stream ({exc}).",
            )
        except Exception as exc:
            return ValidationResultDTO(
                is_valid=False,
                file_size_bytes=file_size,
                pdf_version=pdf_version,
                error_code="DOC_001",
                error_message=f"Unrecognized PDF error: Structural parse failure ({exc}).",
            )

        # Validation success
        return ValidationResultDTO(
            is_valid=True,
            file_size_bytes=file_size,
            pdf_version=pdf_version,
            error_code=None,
            error_message=None,
        )
