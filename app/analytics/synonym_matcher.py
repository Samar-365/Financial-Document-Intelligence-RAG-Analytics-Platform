"""Accounting Synonym & Terminology Matcher for Financial Analytics Engine (Module 6.1).

Responsible for:
1. Mapping Indian (Ind AS / Indian GAAP) and Global (US GAAP / IFRS) accounting aliases
   to canonical financial metric keys (e.g., "Turnover", "Revenue from Operations" -> "revenue").
2. Classifying financial metrics into standard statement domains: P&L, Balance Sheet, or Cash Flow.
"""

import re
from typing import Dict, List, Optional


class StatementDomain:
    """Standardized financial statement classification domains."""

    P_AND_L: str = "P&L"
    BALANCE_SHEET: str = "Balance Sheet"
    CASH_FLOW: str = "Cash Flow"


class SynonymMatcher:
    """Matches raw accounting line items and labels to canonical metrics and statement domains.

    Technical Tasks:
    1. Standard Metric Synonym Registry: Build dictionary mapping Indian and global accounting aliases
       to 12+ canonical metric keys.
    2. Statement Classification Rules: Classify metric targets into P&L, Balance Sheet, or Cash Flow domains.
    """

    # Task 1: Comprehensive dictionary mapping canonical metric keys to Indian & Global aliases
    SYNONYM_REGISTRY: Dict[str, List[str]] = {
        "revenue": [
            "revenue",
            "revenues",
            "revenue from operations",
            "total revenue",
            "total revenues",
            "net revenue",
            "net revenues",
            "sales",
            "net sales",
            "gross sales",
            "turnover",
            "total turnover",
            "income from operations",
            "operating revenue",
            "gross turnover",
            "sales revenue",
            "total income",
        ],
        "gross_profit": [
            "gross profit",
            "gross income",
            "gross margin",
            "gross profit (loss)",
            "gross profit loss",
        ],
        "operating_income": [
            "operating income",
            "operating profit",
            "operating profit (loss)",
            "ebit",
            "earnings before interest and tax",
            "earnings before interest and taxes",
            "pbit",
            "profit before interest and tax",
            "profit before interest and taxes",
            "operating earnings",
            "profit from operations",
            "operating result",
            "operating profit before working capital changes",
        ],
        "ebitda": [
            "ebitda",
            "earnings before interest, tax, depreciation and amortization",
            "earnings before interest, taxes, depreciation and amortization",
            "operating profit before depreciation",
            "operating profit before depreciation and amortization",
            "operating cash profit",
            "pbdt",
            "profit before depreciation, interest and tax",
            "profit before depreciation",
        ],
        "net_income": [
            "net income",
            "net profit",
            "net profit after tax",
            "profit after tax",
            "pat",
            "profit for the year",
            "profit for the period",
            "net profit for the period",
            "net profit for the year",
            "net earnings",
            "net loss",
            "profit attributable to owners",
            "profit attributable to shareholders",
            "consolidated profit for the year",
            "bottom line",
        ],
        "eps": [
            "eps",
            "earnings per share",
            "diluted eps",
            "basic eps",
            "basic earnings per share",
            "diluted earnings per share",
            "earnings per equity share",
            "diluted earnings per equity share",
            "basic and diluted eps",
        ],
        "total_assets": [
            "total assets",
            "assets total",
            "total non-current and current assets",
            "total non-current assets and current assets",
            "total asset",
        ],
        "total_liabilities": [
            "total liabilities",
            "liabilities total",
            "total non-current and current liabilities",
            "total equity and liabilities",
            "total liability",
        ],
        "shareholder_equity": [
            "shareholders' equity",
            "shareholders equity",
            "shareholder equity",
            "total equity",
            "equity",
            "net worth",
            "equity share capital",
            "share capital and reserves",
            "total shareholder equity",
            "owners' equity",
            "owners equity",
            "book value",
        ],
        "total_debt": [
            "total debt",
            "total borrowings",
            "borrowings",
            "debt",
            "long-term and short-term debt",
            "long-term borrowings and short-term borrowings",
            "financial liabilities: borrowings",
            "financial liabilities borrowings",
            "aggregate debt",
            "total borrowings and debt",
        ],
        "cash": [
            "cash",
            "cash and cash equivalents",
            "cash & cash equivalents",
            "cash and bank balances",
            "bank balances",
            "liquid assets",
            "cash and balances with banks",
            "cash and cash balances",
        ],
        "operating_cash_flow": [
            "operating cash flow",
            "cash flow from operating activities",
            "cash flows from operating activities",
            "cash generated from operations",
            "net cash flow from operating activities",
            "net cash generated from operating activities",
            "cfo",
            "cash from operations",
        ],
        "free_cash_flow": [
            "free cash flow",
            "fcf",
            "free cash flow to firm",
            "free cashflow",
        ],
        "current_assets": [
            "current assets",
            "total current assets",
        ],
        "current_liabilities": [
            "current liabilities",
            "total current liabilities",
        ],
    }

    # Task 2: Domain classification rules
    METRIC_DOMAINS: Dict[str, str] = {
        "revenue": StatementDomain.P_AND_L,
        "gross_profit": StatementDomain.P_AND_L,
        "operating_income": StatementDomain.P_AND_L,
        "ebitda": StatementDomain.P_AND_L,
        "net_income": StatementDomain.P_AND_L,
        "eps": StatementDomain.P_AND_L,
        "total_assets": StatementDomain.BALANCE_SHEET,
        "total_liabilities": StatementDomain.BALANCE_SHEET,
        "shareholder_equity": StatementDomain.BALANCE_SHEET,
        "total_debt": StatementDomain.BALANCE_SHEET,
        "cash": StatementDomain.BALANCE_SHEET,
        "current_assets": StatementDomain.BALANCE_SHEET,
        "current_liabilities": StatementDomain.BALANCE_SHEET,
        "operating_cash_flow": StatementDomain.CASH_FLOW,
        "free_cash_flow": StatementDomain.CASH_FLOW,
    }

    # Pre-compiled inverted lookup table for fast O(1) resolution
    _INVERTED_LOOKUP: Dict[str, str] = {}

    @classmethod
    def _init_lookup(cls) -> None:
        """Populates the inverted alias lookup index with normalized variations."""
        if cls._INVERTED_LOOKUP:
            return

        for canonical_key, aliases in cls.SYNONYM_REGISTRY.items():
            cls._INVERTED_LOOKUP[canonical_key.lower()] = canonical_key
            for alias in aliases:
                normalized = cls.normalize_label(alias)
                if normalized:
                    cls._INVERTED_LOOKUP[normalized] = canonical_key

    @staticmethod
    def normalize_label(line_label: str) -> str:
        """Normalizes a raw text line label by stripping numbering, punctuation, and extra whitespace.

        Args:
            line_label: Raw accounting line label.

        Returns:
            str: Normalized lowercase line label.
        """
        if not isinstance(line_label, str):
            raise TypeError("line_label must be a string.")

        text = line_label.lower().strip()
        # Remove leading list enumeration e.g. "1.", "1.1", "a)", "(i)", "•", "-"
        text = re.sub(r"^(\d+(\.\d+)*|[a-z]\)|\([a-z0-9]+\)|[•\-\*])\s*", "", text)
        # Remove footnote markers like "(note 12)" or "[1]" or "*"
        text = re.sub(r"\((note\s*\d+|\d+)\)", "", text)
        text = re.sub(r"\[\d+\]", "", text)
        # Replace & with and
        text = text.replace("&", " and ")
        # Remove punctuation except letters, numbers, and spaces
        text = re.sub(r"[^\w\s]", " ", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def resolve_metric_name(cls, line_label: str) -> Optional[str]:
        """Matches raw text label against canonical financial metric keys.

        Args:
            line_label: Text string containing line-item name from financial statement.

        Returns:
            Optional[str]: Canonical metric key if matched, or None if unmapped.

        Raises:
            TypeError: If line_label is not a string.
        """
        if not isinstance(line_label, str):
            raise TypeError("line_label must be a string.")

        cls._init_lookup()

        normalized = cls.normalize_label(line_label)
        if not normalized:
            return None

        # 1. Exact match against normalized inverted lookup
        if normalized in cls._INVERTED_LOOKUP:
            return cls._INVERTED_LOOKUP[normalized]

        # 2. Match against raw lowercase label
        raw_lower = line_label.lower().strip()
        if raw_lower in cls._INVERTED_LOOKUP:
            return cls._INVERTED_LOOKUP[raw_lower]

        # 3. Handle specific compound variations (e.g. "revenue from operations (net)")
        for alias, canonical_key in cls._INVERTED_LOOKUP.items():
            if normalized == alias or normalized.startswith(f"{alias} ") or normalized.endswith(f" {alias}"):
                return canonical_key

        return None

    @classmethod
    def get_statement_domain(cls, metric_or_label: str) -> Optional[str]:
        """Returns the financial statement domain (P&L, Balance Sheet, Cash Flow) for a metric or label.

        Args:
            metric_or_label: Either a canonical metric key or a raw accounting line label.

        Returns:
            Optional[str]: Statement domain string ("P&L", "Balance Sheet", "Cash Flow"), or None.

        Raises:
            TypeError: If metric_or_label is not a string.
        """
        if not isinstance(metric_or_label, str):
            raise TypeError("metric_or_label must be a string.")

        # Check if already a canonical key
        canonical = metric_or_label.lower().strip()
        if canonical in cls.METRIC_DOMAINS:
            return cls.METRIC_DOMAINS[canonical]

        # Try to resolve raw label to canonical key
        resolved = cls.resolve_metric_name(metric_or_label)
        if resolved and resolved in cls.METRIC_DOMAINS:
            return cls.METRIC_DOMAINS[resolved]

        return None

    @classmethod
    def get_all_aliases(cls, metric_name: str) -> List[str]:
        """Returns list of registered aliases for a canonical metric key.

        Args:
            metric_name: Canonical metric key (e.g. "revenue").

        Returns:
            List[str]: List of known accounting aliases.
        """
        canonical = metric_name.lower().strip()
        return cls.SYNONYM_REGISTRY.get(canonical, [])
