import pytest
from app.document_processing.cleaner import TextCleaner


def test_clean_ligatures():
    """Verifies that Unicode ligatures (fi, fl, ffi, ffl) are unpacked to standard ASCII characters."""
    raw = "The ﬁnancial ﬂow was eﬃcient and completely oﬄine."
    cleaned = TextCleaner.clean_text(raw)
    assert cleaned == "The financial flow was efficient and completely offline."


def test_clean_dashes_and_non_breaking_spaces():
    """Verifies normalization of en-dashes, em-dashes, and non-breaking spaces."""
    raw = "Revenue\u2013Growth\u2014Ratio was\u00a0high."
    cleaned = TextCleaner.clean_text(raw)
    assert cleaned == "Revenue-Growth-Ratio was high."


def test_dehyphenate_broken_words():
    """Verifies that words split across line breaks by hyphens are rejoined correctly."""
    raw = "The oper-\nating income for the fourth quarter was positive."
    cleaned = TextCleaner.clean_text(raw)
    assert "operating income" in cleaned
    assert "oper-" not in cleaned


def test_preserve_financial_numbers_and_brackets():
    """Verifies that negative parentheses, decimals, commas, and percentages are preserved without distortion."""
    raw = (
        "Operating Loss: (120.50) million.\n"
        "Net Margin: -14.2%.\n"
        "Consolidated Revenue: $1,250,400,000.75."
    )
    cleaned = TextCleaner.clean_text(raw)
    assert "(120.50)" in cleaned
    assert "-14.2%" in cleaned
    assert "$1,250,400,000.75" in cleaned


def test_strip_running_headers_and_footers():
    """Verifies that isolated page numbers, running banners, and header bars are stripped."""
    raw = (
        "ABC Technologies Annual Report 2025\n"
        "Revenue increased by 18.5% year-over-year.\n"
        "Page 42 of 150\n"
        "Gross margins expanded to 35.2%.\n"
        "- 43 -\n"
        "Page 44 | Financial Statements\n"
        "Cash and cash equivalents stood at $450 million.\n"
        "45"
    )
    cleaned = TextCleaner.clean_text(raw)

    # Confirm narrative contents are intact
    assert "Revenue increased by 18.5% year-over-year." in cleaned
    assert "Gross margins expanded to 35.2%." in cleaned
    assert "Cash and cash equivalents stood at $450 million." in cleaned

    # Confirm headers/footers were removed
    assert "ABC Technologies Annual Report 2025" not in cleaned
    assert "Page 42 of 150" not in cleaned
    assert "- 43 -" not in cleaned
    assert "Page 44 | Financial Statements" not in cleaned
    # Ensure line with just 45 is stripped
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
    assert "45" not in lines


def test_clean_empty_or_whitespace_text():
    """Verifies safe handling of empty or blank string inputs."""
    assert TextCleaner.clean_text("") == ""
    assert TextCleaner.clean_text("   \n\t  ") == ""
