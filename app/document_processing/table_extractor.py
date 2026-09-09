import os
from typing import List, Optional
import pdfplumber
from pydantic import BaseModel, Field


class ExtractedTableDTO(BaseModel):
    """Data Transfer Object capturing extracted tabular financial structures serialized into markdown."""

    page_number: int = Field(
        ...,
        ge=1,
        description="1-based page number where the table was detected.",
    )
    table_index: int = Field(
        ...,
        ge=0,
        description="0-based sequential index of the table within the page.",
    )
    markdown_table: str = Field(
        ...,
        description="Standardized GitHub-flavored pipe-delimited markdown representation of the table.",
    )
    row_count: int = Field(
        ...,
        ge=0,
        description="Total number of rows in the extracted table, including header.",
    )
    col_count: int = Field(
        ...,
        ge=0,
        description="Maximum number of columns across all rows in the extracted table.",
    )


class TableExtractor:
    """Extractor responsible for detecting bounding borders and serializing tabular grids into markdown."""

    def extract_tables(self, file_path: str) -> List[ExtractedTableDTO]:
        """Detects tables and serializes them into markdown pipe-delimited text blocks.

        Technical Tasks Performed:
        1. Table Bounding Box Detection: Inspects page graphics, explicit cell borders, and whitespace
           delimiters using pdfplumber to locate tabular grids.
        2. Markdown Table Serialization: Cleans newline artifacts within cells, aligns column counts,
           and serializes rows into standard pipe-delimited markdown tables.

        Args:
            file_path: System file path to the PDF document.

        Returns:
            List[ExtractedTableDTO]: Extracted tables containing page numbers, dimensions, and markdown text.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: '{file_path}'")

        extracted_tables: List[ExtractedTableDTO] = []

        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                raw_tables = page.extract_tables()
                if not raw_tables:
                    continue

                for table_idx, raw_table in enumerate(raw_tables):
                    if not raw_table or len(raw_table) == 0:
                        continue

                    # Filter out purely blank tables where all cells in all rows are empty or None
                    has_content = any(
                        any(cell is not None and str(cell).strip() != "" for cell in row)
                        for row in raw_table
                    )
                    if not has_content:
                        continue

                    markdown_str, row_count, col_count = self._serialize_to_markdown(raw_table)
                    if row_count > 0 and col_count > 0:
                        extracted_tables.append(
                            ExtractedTableDTO(
                                page_number=page_idx,
                                table_index=table_idx,
                                markdown_table=markdown_str,
                                row_count=row_count,
                                col_count=col_count,
                            )
                        )

        return extracted_tables

    @staticmethod
    def _serialize_to_markdown(raw_table: List[List[Optional[str]]]) -> tuple[str, int, int]:
        """Converts a 2D raw table structure into aligned pipe-delimited markdown text.

        Args:
            raw_table: 2D list of extracted string cells.

        Returns:
            tuple of (markdown_string, row_count, col_count)
        """
        if not raw_table:
            return "", 0, 0

        # Determine max column width across all rows to pad ragged rows
        max_cols = max((len(row) for row in raw_table), default=0)
        if max_cols == 0:
            return "", 0, 0

        cleaned_rows: List[List[str]] = []
        for row in raw_table:
            cleaned_row: List[str] = []
            for cell in row:
                if cell is None:
                    cleaned_cell = ""
                else:
                    # Strip leading/trailing whitespaces, replace embedded newlines with spaces, escape pipes
                    cleaned_cell = str(cell).replace("\r\n", " ").replace("\n", " ").replace("|", "\\|").strip()
                cleaned_row.append(cleaned_cell)

            # Pad ragged row if shorter than max_cols
            if len(cleaned_row) < max_cols:
                cleaned_row.extend([""] * (max_cols - len(cleaned_row)))
            cleaned_rows.append(cleaned_row)

        # Build markdown lines
        lines: List[str] = []

        # Header row (Row 0)
        header_line = "| " + " | ".join(cleaned_rows[0]) + " |"
        delimiter_line = "| " + " | ".join([":---"] * max_cols) + " |"
        lines.append(header_line)
        lines.append(delimiter_line)

        # Subsequent data rows (Row 1 to N)
        for row in cleaned_rows[1:]:
            line = "| " + " | ".join(row) + " |"
            lines.append(line)

        markdown_table = "\n".join(lines)
        return markdown_table, len(cleaned_rows), max_cols
