import re
import unicodedata
from typing import Dict

# Map of standard Unicode typographic ligatures to ASCII decompositions
LIGATURE_MAP: Dict[str, str] = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "ft",
    "\ufb06": "st",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
}

# Various Unicode dashes to standardize to standard ASCII hyphen
DASH_MAP: Dict[str, str] = {
    "\u2012": "-",  # figure dash
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2015": "-",  # horizontal bar
    "\u2212": "-",  # minus sign
}

# Non-standard spaces to convert to regular ASCII space
SPACE_MAP: Dict[str, str] = {
    "\u00a0": " ",  # non-breaking space
    "\u2000": " ",  # en quad
    "\u2001": " ",  # em quad
    "\u2002": " ",  # en space
    "\u2003": " ",  # em space
    "\u2004": " ",  # three-per-em space
    "\u2005": " ",  # four-per-em space
    "\u2006": " ",  # six-per-em space
    "\u2007": " ",  # figure space
    "\u2008": " ",  # punctuation space
    "\u2009": " ",  # thin space
    "\u200a": " ",  # hair space
    "\u202f": " ",  # narrow no-break space
    "\u205f": " ",  # medium mathematical space
    "\u3000": " ",  # ideographic space
    "\u200b": "",   # zero-width space
    "\ufeff": "",   # zero-width no-break space (BOM)
}

# Regex patterns for running headers and footers
PAGE_NUMBER_ONLY_REGEX = re.compile(
    r"^\s*(?:[-–—]\s*)?(?:Page\s+)?\d+(?:\s+(?:of|/)\s+\d+)?(?:\s*[-–—])?\s*$",
    re.IGNORECASE,
)
PAGE_BAR_HEADER_REGEX = re.compile(
    r"^\s*(?:Page\s+\d+\s*[\|\-•]\s*.*|.*?\s*[\|\-•]\s*Page\s+\d+)\s*$",
    re.IGNORECASE,
)
RUNNING_REPORT_HEADER_REGEX = re.compile(
    r"^\s*(?:(?:\w+[\s\.\,\-]+){1,6})?(?:Annual Report|Quarterly Report|10-K|10-Q|Financial Statements)\s*(?:\d{4}|\d{2})?\s*$",
    re.IGNORECASE,
)
HYPHENATED_WORD_BREAK_REGEX = re.compile(r"([a-zA-Z]+)-\n([a-zA-Z]+)")


class TextCleaner:
    """Cleaner responsible for normalizing Unicode characters and stripping running headers/footers."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Normalizes Unicode ligatures, cleans whitespace, and removes running headers/footers.

        Technical Tasks Performed:
        1. Ligature & Character Normalization: Expands typographical ligatures (e.g., fi, fl, ffi),
           standardizes irregular Unicode spaces and dashes, removes line-break hyphenation while
           strictly preserving financial notation (negative parentheses, decimals, commas).
        2. Header & Footer Stripping: Inspects line structures to eliminate isolated page numbers,
           running report headers, and divider bars that contaminate semantic vector chunks.

        Args:
            raw_text: Unprocessed text string extracted from PDF pages.

        Returns:
            str: Normalized, sanitized financial text string.
        """
        if not raw_text:
            return ""

        text = raw_text

        # Task 1: Ligature normalization
        for lig, repl in LIGATURE_MAP.items():
            text = text.replace(lig, repl)

        # Standardize dashes and spaces
        for dash, repl in DASH_MAP.items():
            text = text.replace(dash, repl)

        for space_char, repl in SPACE_MAP.items():
            text = text.replace(space_char, repl)

        # Curly quotes to straight quotes
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")

        # De-hyphenate words broken by newlines (e.g., "per-\ncentage" -> "percentage")
        # Preserves numbers, arithmetic signs, and financial brackets
        text = HYPHENATED_WORD_BREAK_REGEX.sub(r"\1\2", text)

        # Task 2: Header & Footer stripping line-by-line
        lines = text.splitlines()
        retained_lines = []

        for line in lines:
            stripped_line = line.strip()

            # Skip empty lines during line checks (preserve blank line spacing later)
            if not stripped_line:
                retained_lines.append("")
                continue

            # Strip standalone page numbering (e.g. "Page 42", "42 of 150", "- 12 -", "12")
            if PAGE_NUMBER_ONLY_REGEX.match(stripped_line):
                continue

            # Strip header bar patterns with page numbers (e.g. "Page 12 | Management Discussion")
            if PAGE_BAR_HEADER_REGEX.match(stripped_line):
                continue

            # Strip isolated recurring corporate annual report banner lines
            if len(stripped_line) < 80 and RUNNING_REPORT_HEADER_REGEX.match(stripped_line):
                continue

            retained_lines.append(line)

        # Recombine lines
        reconstructed = "\n".join(retained_lines)

        # Normalize excessive horizontal whitespace on lines
        # Collapse multiple spaces/tabs into a single space, but maintain newlines
        reconstructed = re.sub(r"[ \t]+", " ", reconstructed)

        # Normalize excessive vertical spacing (max 2 consecutive newlines)
        reconstructed = re.sub(r"\n{3,}", "\n\n", reconstructed)

        return reconstructed.strip()
