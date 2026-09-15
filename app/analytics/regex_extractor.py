"""Regex Tabular Line-Item Extractor for Financial Analytics Engine (Module 6.3).

Responsible for:
1. Scanning markdown tables for canonical metric aliases and extracting figures in the active fiscal year column.
2. Detecting fiscal year column headers (e.g., FY24, FY25, 2024, 2025, 31-Mar-2025) to align columns correctly.
3. Detecting table-level scaling units (e.g. "₹ in Crores", "in Millions") and converting figures to exact Decimals.
"""

from decimal import Decimal
import re
from typing import Dict, List, Optional, Tuple

from app.analytics.synonym_matcher import SynonymMatcher
from app.analytics.unit_normalizer import FinancialUnitNormalizer


class RegexMetricExtractor: #Scans and extracts canonical financial metrics from pipe-delimited markdown tables
    """Scans and extracts canonical financial metrics from pipe-delimited markdown tables.

    Technical Tasks:
    1. Markdown Table Line Matching: Scan markdown tables for canonical metric aliases and extract figures.
    2. Multi-Year Column Alignment: Detect fiscal year column headers to extract the correct column value.
    """

    @staticmethod
    def _detect_table_unit(table_text: str) -> str: #Inspects table text to detect unit magnitude e.g. Crores, Millions, Lakhs
        """Inspects table header lines or title for unit annotations (e.g. '₹ in Crores', 'in Millions').

        Args:
            table_text: Full raw text of the markdown table.

        Returns:
            str: Unit identifier string (e.g. 'crore', 'million', 'lakh', or 'base').
        """
        # Look for explicit parenthetical statements e.g. "(₹ in Crores)", "(in Millions)", "(Rs. Lakhs)"
        explicit_unit_pattern = re.compile( #Matches explicit currency unit statements e.g. (₹ in Crores)
            r"\((?:[₹$€£¥]|(?:inr|rs\.?|usd|eur|gbp))\s*in\s*(crores?|cr|lakhs?|lacs?|millions?|mn|billions?|bn|thousands?|k)\)",
            re.IGNORECASE,
        )
        match = explicit_unit_pattern.search(table_text)
        if match:
            return match.group(1).lower()

        # Look for simpler pattern e.g. "(in Crores)", "(in Millions)"
        simple_unit_pattern = re.compile( #Matches simpler unit statements e.g. (in Millions)
            r"\(in\s+(crores?|cr|lakhs?|lacs?|millions?|mn|billions?|bn|thousands?|k)\)",
            re.IGNORECASE,
        )
        match = simple_unit_pattern.search(table_text)
        if match:
            return match.group(1).lower()

        # Look for standalone mention of units in the first 3 lines
        first_lines = "\n".join(table_text.splitlines()[:3]) #Inspect top 3 lines of table
        general_unit_pattern = re.compile( #Searches for standalone unit keywords near top of table
            r"\b(crores?|lakhs?|lacs?|millions?|billions?)\b",
            re.IGNORECASE,
        )
        match = general_unit_pattern.search(first_lines)
        if match:
            return match.group(1).lower()

        return "base" #Defaults to base units (multiplier = 1) if no unit statement found

    @staticmethod
    def _match_year_column(header_cells: List[str], target_year: str) -> Optional[int]: #Identifies which column index corresponds to the requested fiscal year
        """Identifies the 0-indexed column matching target_year from table header row.

        Args:
            header_cells: List of cell contents in the header row.
            target_year: Target fiscal year string (e.g., 'FY25', '2025', 'FY 2025', '25').

        Returns:
            Optional[int]: Column index matching the target year, or None.
        """
        # Extract 2-digit and 4-digit representations of the target year
        year_digits = re.findall(r"\d+", target_year) #Extracts numeric digits from year string (e.g. "FY24" -> "24")
        if not year_digits:
            return None

        # Build candidate year patterns
        target_patterns = [] #List of regex patterns to match various header date formats
        for digit_seq in year_digits:
            if len(digit_seq) == 4: #4-digit year like "2024"
                two_digit = digit_seq[-2:]
                target_patterns.extend([
                    rf"\b20{two_digit}\b",
                    rf"\bfy\s*{two_digit}\b",
                    rf"\bfy\s*20{two_digit}\b",
                    rf"\b31[-/\s]*(?:mar|march|03)[-/\s]*20{two_digit}\b",
                    rf"\b31[-/\s]*(?:mar|march|03)[-/\s]*{two_digit}\b",
                    rf"\b{two_digit}\b",
                ])
            elif len(digit_seq) == 2: #2-digit year like "24"
                two_digit = digit_seq
                target_patterns.extend([
                    rf"\bfy\s*{two_digit}\b",
                    rf"\bfy\s*20{two_digit}\b",
                    rf"\b20{two_digit}\b",
                    rf"\b31[-/\s]*(?:mar|march|03)[-/\s]*20{two_digit}\b",
                    rf"\b{two_digit}\b",
                ])

        # Scan each header cell
        for idx, cell in enumerate(header_cells): #Check each column header cell
            cleaned_cell = cell.lower().strip()
            for pat in target_patterns:
                if re.search(pat, cleaned_cell): #If column header matches target fiscal year pattern
                    return idx #Return the 0-based column index

        return None #No matching year column found

    @staticmethod
    def _parse_row_cells(line: str) -> List[str]: #Splits a pipe-delimited markdown row into individual cell texts
        """Splits a markdown table line into stripped cell strings."""
        if not line.strip().startswith("|") or not line.strip().endswith("|"): #Must start and end with '|'
            return []
        # Split by pipe and remove the outer leading/trailing empty cells
        cells = [c.strip() for c in line.split("|")] #Break row into individual cells
        if cells and cells[0] == "": #Remove empty leading cell from outer pipe
            cells.pop(0)
        if cells and cells[-1] == "": #Remove empty trailing cell from outer pipe
            cells.pop()
        return cells

    def extract_from_tables( #Main extraction function: extracts metrics for the target fiscal year from markdown tables
        self,
        markdown_tables: List[str],
        target_year: str,
    ) -> Dict[str, Decimal]:
        """Scans tables for financial metrics matching the target fiscal year column.

        Args:
            markdown_tables: List of markdown pipe-delimited table text strings.
            target_year: Target fiscal year string (e.g. "FY25", "2025", "FY 2024").

        Returns:
            Dict[str, Decimal]: Dictionary of canonical metric keys to extracted Decimal values.

        Raises:
            TypeError: If markdown_tables is not a list or target_year is not a string.
            ValueError: If target_year is empty or whitespace.
        """
        if not isinstance(markdown_tables, list): #Validate that markdown_tables is a list
            raise TypeError("markdown_tables must be a list of markdown table strings.")

        if not isinstance(target_year, str): #Validate target_year is a string
            raise TypeError("target_year must be a string.")

        if not target_year.strip(): #Validate target_year is not empty
            raise ValueError("target_year cannot be empty or whitespace.")

        for i, tbl in enumerate(markdown_tables): #Validate every table entry is a string
            if not isinstance(tbl, str):
                raise TypeError(f"Element at index {i} in markdown_tables is not a string.")

        extracted_metrics: Dict[str, Decimal] = {} #Stores extracted metrics: metric_name -> Decimal value

        for table_text in markdown_tables: #Process each markdown table
            lines = [l.strip() for l in table_text.splitlines() if l.strip()] #Split into non-empty lines
            if len(lines) < 2: #Table must have at least a header and one row
                continue

            # Detect table-level scaling unit
            table_unit = self._detect_table_unit(table_text) #Detects if numbers are in Crores, Millions, etc.

            # Locate header row and target column index
            target_col_idx: Optional[int] = None #Column number where target year numbers reside
            header_row_line_idx: Optional[int] = None

            for line_idx, line in enumerate(lines): #Find the table header row
                cells = self._parse_row_cells(line)
                if not cells:
                    continue
                # Skip separator lines (e.g., |:---|:---|)
                if re.match(r"^\|[\s\-:|]+\|$", line): #Skip markdown table delimiter row
                    continue

                col_idx = self._match_year_column(cells, target_year) #Check if header row contains our year
                if col_idx is not None:
                    target_col_idx = col_idx #Found target year column index
                    header_row_line_idx = line_idx
                    break

            if target_col_idx is None or header_row_line_idx is None: #If no matching year column was found in this table, skip it
                continue

            # Process data rows after the header
            for line in lines[header_row_line_idx + 1 :]: #Loop through rows underneath header
                # Skip separator lines
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    continue

                cells = self._parse_row_cells(line) #Parse cells in this row
                if not cells or len(cells) <= target_col_idx:
                    continue

                # The line label is the first cell
                line_label = cells[0].strip() #Get the accounting item description (e.g. "Revenue from Operations")
                if not line_label:
                    continue

                # Task 1: Resolve line item label to canonical metric key
                canonical_metric = SynonymMatcher.resolve_metric_name(line_label) #Match description to canonical metric name
                if not canonical_metric: #If not a metric we track, ignore
                    continue

                # Extract target year cell value
                cell_value_str = cells[target_col_idx].strip() #Get the number from the target year's column
                if not cell_value_str:
                    continue

                try:
                    normalized_decimal = FinancialUnitNormalizer.normalize_value( #Convert raw string e.g. "1,500.5" and unit scale into base Decimal
                        raw_string=cell_value_str,
                        document_unit=table_unit,
                    )
                    # Store if not previously found or update
                    extracted_metrics[canonical_metric] = normalized_decimal #Store canonical metric value
                except (ValueError, TypeError): #Ignore unparseable values
                    continue

        return extracted_metrics #Return all extracted metrics from the tables
