"""Financial Currency & Unit Normalizer for Financial Analytics Engine (Module 6.2).

Responsible for:
1. Scaling Indian unit multipliers (Crore / Cr = 10^7, Lakh / Lac = 10^5) to base numbers.
2. Scaling Western unit multipliers (Million / M = 10^6, Billion / B = 10^9, Thousand / K = 10^3, Trillion / T = 10^12).
3. Parsing accounting negative parentheses (e.g., "(1,250)" -> -1250.00) and stripping currency symbols.
4. Returning standardized Decimal values quantized to two decimal places.
"""

import re
from decimal import Decimal
from typing import Dict


class FinancialUnitNormalizer: #Parses raw financial numerical strings into exact base-currency Decimal representations
    """Parses raw financial numerical strings into exact base-currency Decimal representations.

    Technical Tasks:
    1. Indian Unit Scaling: Detect Crore (Cr) and Lakh multipliers, converting to base numbers.
    2. Western Unit Scaling & Parentheses: Convert Million (M) and Billion (B), and parse accounting
       negative parentheses (1,250) to -1250.
    """

    UNIT_MULTIPLIERS: Dict[str, Decimal] = { #Dictionary mapping financial unit names/abbreviations to their numerical multipliers
        # Base
        "base": Decimal("1"),
        "": Decimal("1"),
        "unit": Decimal("1"),
        "units": Decimal("1"),
        # Indian multipliers
        "crore": Decimal("10000000"), #1 Crore = 10 Million = 10^7
        "crores": Decimal("10000000"),
        "cr": Decimal("10000000"), #Standard Indian accounting abbreviation for Crore
        "cr.": Decimal("10000000"),
        "lakh": Decimal("100000"), #1 Lakh = 100 Thousand = 10^5
        "lakhs": Decimal("100000"),
        "lac": Decimal("100000"),
        "lacs": Decimal("100000"),
        "l": Decimal("100000"),
        "l.": Decimal("100000"),
        # Western multipliers
        "thousand": Decimal("1000"), #1 Thousand = 10^3
        "thousands": Decimal("1000"),
        "k": Decimal("1000"),
        "million": Decimal("1000000"), #1 Million = 10^6
        "millions": Decimal("1000000"),
        "m": Decimal("1000000"),
        "mn": Decimal("1000000"),
        "mn.": Decimal("1000000"),
        "billion": Decimal("1000000000"), #1 Billion = 10^9
        "billions": Decimal("1000000000"),
        "b": Decimal("1000000000"),
        "bn": Decimal("1000000000"),
        "bn.": Decimal("1000000000"),
        "trillion": Decimal("1000000000000"), #1 Trillion = 10^12
        "trillions": Decimal("1000000000000"),
        "t": Decimal("1000000000000"),
        "tn": Decimal("1000000000000"),
        "tn.": Decimal("1000000000000"),
    }

    # Zero / Nil indicator tokens common in corporate disclosures
    NIL_TOKENS = {"-", "—", "–", "nil", "nil.", "n/a", "na", "null", "none"} #Tokens that represent zero or not applicable in financial tables

    @classmethod
    def get_unit_multiplier(cls, unit_str: str) -> Decimal: #Helper method to lookup decimal power multiplier
        """Looks up decimal multiplier for a given unit string.

        Args:
            unit_str: Unit name or abbreviation.

        Returns:
            Decimal: Multiplier power. Defaults to 1 if unknown.
        """
        cleaned = unit_str.lower().strip() #Lowercases and strips whitespace
        return cls.UNIT_MULTIPLIERS.get(cleaned, Decimal("1")) #Returns matched multiplier or defaults to 1

    @staticmethod
    def normalize_value(raw_string: str, document_unit: str = "base") -> Decimal: #Main function: converts raw currency string into base Decimal
        """Parses currency strings into exact Decimal base currency representations.

        Args:
            raw_string: Text string containing numeric figure, currency symbols, parentheses, or unit abbreviations.
            document_unit: Default fallback scale multiplier if not specified inline in raw_string.

        Returns:
            Decimal: Normalized value in base currency units, quantized to 2 decimal places.

        Raises:
            TypeError: If raw_string or document_unit are not strings.
            ValueError: If raw_string contains no extractable numeric figure or is empty.
        """
        if not isinstance(raw_string, str): #Validates that input is a string
            raise TypeError("raw_string must be a string.")

        if not isinstance(document_unit, str): #Validates that document_unit fallback is a string
            raise TypeError("document_unit must be a string.")

        cleaned = raw_string.strip() #Removes surrounding whitespace
        if not cleaned: #Empty input string validation
            raise ValueError("Cannot normalize empty or whitespace-only string.")

        # Check for financial nil / dash / zero tokens
        if cleaned.lower() in FinancialUnitNormalizer.NIL_TOKENS: #If the table cell is a dash or 'nil', it represents 0
            return Decimal("0.00")

        # Task 2: Detect accounting negative parentheses "(1,250)" or negative sign "-1,250"
        is_negative = False
        if "(" in cleaned and ")" in cleaned: #In financial reporting, numbers in brackets e.g. (500) mean -500
            is_negative = True
            cleaned = cleaned.replace("(", " ").replace(")", " ") #Strip parentheses to extract raw number
        elif cleaned.startswith("-") or cleaned.endswith("-"): #Handles leading or trailing minus signs
            is_negative = True
            cleaned = cleaned.replace("-", " ")

        # Task 1 & 2: Search for inline unit abbreviations
        # Match unit keywords as independent tokens or suffixes
        unit_pattern = re.compile( #Regex to detect inline unit terms (cr, lakh, mn, bn, etc.)
            r"\b(crores?|cr\.?|lakhs?|lacs?|billions?|bn\.?|millions?|mn\.?|thousands?|trillions?|tn\.?|[mbktl])\b",
            re.IGNORECASE,
        )

        inline_match = unit_pattern.search(cleaned) #Check if a unit was written directly next to the number
        if inline_match: #Unit found inline (e.g. "150 Cr" -> multiplier = 10,000,000)
            unit_str = inline_match.group(1).lower()
            multiplier = FinancialUnitNormalizer.get_unit_multiplier(unit_str)
            # Remove the detected unit token from string to prevent interference with numeric parsing
            cleaned = (
                cleaned[: inline_match.start()] + " " + cleaned[inline_match.end() :]
            )
        else: #No inline unit found, fallback to document-level unit (e.g. document reported in "millions")
            # Fallback to document_unit
            multiplier = FinancialUnitNormalizer.get_unit_multiplier(document_unit)

        # Strip currency symbols and common currency tags
        currency_pattern = re.compile( #Regex to strip currency symbols ($, ₹, €, £) and currency codes (USD, INR)
            r"[₹$€£¥]|(?:\b(inr|rs\.?|usd|eur|gbp)\b)",
            re.IGNORECASE,
        )
        cleaned = currency_pattern.sub(" ", cleaned) #Removes currency symbols

        # Remove commas, extra spaces, and redundant characters
        cleaned = cleaned.replace(",", "") #Removes thousands separator commas (e.g., "1,250" -> "1250")
        cleaned = cleaned.strip()

        # Extract the core numeric portion (e.g. "1250.50")
        num_match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned) #Finds the floating-point or integer digits
        if not num_match: #If no numbers are found, raise an error
            raise ValueError(f"Could not parse valid numerical figure from '{raw_string}'.")

        raw_num = Decimal(num_match.group(0)) #Parse the raw number into a high-precision Decimal
        final_value = raw_num * multiplier #Multiply by unit scale (e.g. 12.5 * 1,000,000 = 12,500,000)

        if is_negative: #Apply negative sign if accounting parentheses were detected
            final_value = -final_value

        return final_value.quantize(Decimal("0.01")) #Round to standard 2 decimal places for currency format
