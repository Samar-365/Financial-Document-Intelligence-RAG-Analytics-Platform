import os
from unittest.mock import patch
import pytest
import pypdf
from app.document_processing.validator import PDFValidator, MAX_FILE_SIZE_BYTES


@pytest.fixture
def valid_pdf_file(tmp_path) -> str:
    """Fixture to generate a standard unencrypted valid PDF file."""
    pdf_path = str(tmp_path / "valid_sample.pdf")
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path


@pytest.fixture
def encrypted_pdf_file(tmp_path) -> str:
    """Fixture to generate an encrypted, password-protected PDF file."""
    pdf_path = str(tmp_path / "encrypted_sample.pdf")
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt(user_password="secret_password", owner_password="owner_password")
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path


@pytest.fixture
def spoofed_exe_file(tmp_path) -> str:
    """Fixture to generate a spoofed executable binary named with a .pdf extension."""
    exe_path = str(tmp_path / "malicious.pdf")
    with open(exe_path, "wb") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00")
    return exe_path


@pytest.fixture
def corrupted_pdf_file(tmp_path) -> str:
    """Fixture to generate a corrupted PDF file with valid header but unparseable stream."""
    corrupted_path = str(tmp_path / "corrupted.pdf")
    with open(corrupted_path, "wb") as f:
        f.write(b"%PDF-1.4\nInvalid broken body without trailer or catalog\n")
    return corrupted_path


@pytest.fixture
def empty_file(tmp_path) -> str:
    """Fixture to generate an empty 0-byte file."""
    empty_path = str(tmp_path / "empty.pdf")
    with open(empty_path, "wb") as f:
        pass
    return empty_path


def test_validate_valid_pdf(valid_pdf_file):
    """Verifies that a well-formed digital PDF passes validation with version and size."""
    result = PDFValidator.validate_file(valid_pdf_file)
    assert result.is_valid is True
    assert result.file_size_bytes > 0
    assert result.pdf_version != ""
    assert result.error_code is None
    assert result.error_message is None


def test_validate_spoofed_file(spoofed_exe_file):
    """Verifies that non-PDF binaries spoofed with a .pdf extension are rejected with DOC_001."""
    result = PDFValidator.validate_file(spoofed_exe_file)
    assert result.is_valid is False
    assert result.error_code == "DOC_001"
    assert "magic-byte" in result.error_message.lower()


def test_validate_empty_file(empty_file):
    """Verifies that empty 0-byte files are rejected with DOC_001."""
    result = PDFValidator.validate_file(empty_file)
    assert result.is_valid is False
    assert result.error_code == "DOC_001"
    assert "0 bytes" in result.error_message.lower()


def test_validate_encrypted_pdf(encrypted_pdf_file):
    """Verifies that encrypted or password-protected PDFs are rejected with DOC_002."""
    result = PDFValidator.validate_file(encrypted_pdf_file)
    assert result.is_valid is False
    assert result.error_code == "DOC_002"
    assert "encrypted" in result.error_message.lower()


def test_validate_corrupted_pdf(corrupted_pdf_file):
    """Verifies that structurally broken PDFs are detected and rejected with DOC_001."""
    result = PDFValidator.validate_file(corrupted_pdf_file)
    assert result.is_valid is False
    assert result.error_code == "DOC_001"
    assert "corrupted" in result.error_message.lower()


def test_validate_oversized_file(valid_pdf_file):
    """Verifies that files exceeding 50 MB boundary are rejected with DOC_003."""
    with patch("os.path.getsize", return_value=MAX_FILE_SIZE_BYTES + 1024):
        result = PDFValidator.validate_file(valid_pdf_file)
        assert result.is_valid is False
        assert result.error_code == "DOC_003"
        assert "exceeds maximum allowed limit" in result.error_message.lower()


def test_validate_nonexistent_file(tmp_path):
    """Verifies that non-existent file paths return DOC_000 error."""
    nonexistent = str(tmp_path / "ghost_file.pdf")
    result = PDFValidator.validate_file(nonexistent)
    assert result.is_valid is False
    assert result.error_code == "DOC_000"
    assert "not found" in result.error_message.lower()
