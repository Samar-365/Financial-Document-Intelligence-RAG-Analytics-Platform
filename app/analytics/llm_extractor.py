"""Structured LLM JSON Fallback Extractor for Financial Analytics Engine (Module 6.4).

Responsible for:
1. Identifying financial metrics missed by regex table extraction and prompting LLM in structured JSON mode.
2. Assigning audit metadata (is_calculated, confidence, source) for transparency and downstream auditing.
3. Returning standardized ExtractedFinancialMetricsDTO with Decimal metric values.
"""

from decimal import Decimal
import json
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.analytics.unit_normalizer import FinancialUnitNormalizer
from app.rag.llm_client import OpenAIClientWrapper


class MetricAuditMetadata(BaseModel):
    """Audit trail metadata tracking extraction provenance and confidence."""

    is_calculated: bool = Field(
        default=False,
        description="True if metric was derived or computed, False if directly extracted.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0.",
    )
    source: str = Field(
        default="regex",
        description="Extraction source: 'regex', 'llm', or 'unextracted'.",
    )


class ExtractedFinancialMetricsDTO(BaseModel):
    """Data Transfer Object encapsulating canonical financial line items and audit metadata."""

    document_id: str = Field(..., description="Source document identifier.")
    fiscal_year: str = Field(..., description="Target fiscal year (e.g., 'FY25', '2025').")
    currency: str = Field(default="INR", description="Reporting currency (default INR).")

    # Canonical 12 metrics
    revenue: Optional[Decimal] = None
    operating_income: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    shareholder_equity: Optional[Decimal] = None
    current_assets: Optional[Decimal] = None
    current_liabilities: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    operating_cash_flow: Optional[Decimal] = None
    free_cash_flow: Optional[Decimal] = None

    # Task 2: Audit metadata per metric
    audit_metadata: Dict[str, MetricAuditMetadata] = Field(default_factory=dict)


class LLMMetricExtractor:
    """Extracts missing financial line items using structured LLM JSON output.

    Technical Tasks:
    1. Constrained JSON Schema Extraction: For line items missed by regex, prompt GPT-4o-mini
       using Pydantic JSON mode on financial statement pages.
    2. Audit Metadata Assignment: Mark extracted values with is_calculated and confidence metadata.
    """

    CANONICAL_METRICS: List[str] = [
        "revenue",
        "operating_income",
        "net_income",
        "ebitda",
        "total_assets",
        "total_liabilities",
        "shareholder_equity",
        "current_assets",
        "current_liabilities",
        "total_debt",
        "operating_cash_flow",
        "free_cash_flow",
    ]

    def __init__(self, llm_client: Optional[OpenAIClientWrapper] = None) -> None:
        """Initializes the LLM extractor with an OpenAI client wrapper.

        Args:
            llm_client: Optional OpenAIClientWrapper instance. If None, initialized lazily.
        """
        self._llm_client = llm_client

    @property
    def llm_client(self) -> OpenAIClientWrapper:
        """Lazily instantiates OpenAIClientWrapper if not provided."""
        if self._llm_client is None:
            self._llm_client = OpenAIClientWrapper()
        return self._llm_client

    def _build_extraction_prompt(
        self,
        statement_text: str,
        missing_keys: List[str],
        fiscal_year: str,
    ) -> List[Dict[str, str]]:
        """Constructs system and user messages for structured JSON extraction."""
        system_instruction = (
            "You are a precise Financial Extraction Assistant. Extract numerical financial values "
            "strictly from the provided statement text for the target fiscal year.\n"
            "CRITICAL RULES:\n"
            "1. Output ONLY a valid JSON object matching the requested keys.\n"
            "2. If a metric is not mentioned or cannot be determined with certainty, set its value to null.\n"
            "3. Do not speculate or invent numbers.\n"
            "4. Return values either as raw numbers or with standard scale units (e.g., '1250 Cr', '45.2 M')."
        )

        keys_schema = {key: "number or null" for key in missing_keys}
        user_prompt = (
            f"Target Fiscal Year: {fiscal_year}\n"
            f"Extract the following missing metrics:\n{json.dumps(keys_schema, indent=2)}\n\n"
            f"Statement Text:\n{statement_text}\n\n"
            "Return JSON object only:"
        )

        return [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ]

    def extract_missing_metrics(
        self,
        statement_text: str,
        current_metrics: Dict[str, Decimal],
        document_id: str = "doc",
        fiscal_year: str = "FY25",
        currency: str = "INR",
    ) -> ExtractedFinancialMetricsDTO:
        """Extracts missing line items using structured LLM JSON schema mode.

        Args:
            statement_text: Narrative or tabular financial statement context.
            current_metrics: Metrics previously extracted (e.g. by regex).
            document_id: Source document identifier.
            fiscal_year: Target fiscal year.
            currency: Reporting currency.

        Returns:
            ExtractedFinancialMetricsDTO: Completed metrics DTO with audit metadata.

        Raises:
            TypeError: If statement_text is not a string or current_metrics is not a dict.
        """
        if not isinstance(statement_text, str):
            raise TypeError("statement_text must be a string.")

        if not isinstance(current_metrics, dict):
            raise TypeError("current_metrics must be a dict.")

        final_metrics: Dict[str, Any] = {
            "document_id": document_id,
            "fiscal_year": fiscal_year,
            "currency": currency,
        }
        audit_metadata: Dict[str, MetricAuditMetadata] = {}

        # 1. Populate existing metrics from regex
        for key in self.CANONICAL_METRICS:
            if key in current_metrics and current_metrics[key] is not None:
                final_metrics[key] = current_metrics[key]
                audit_metadata[key] = MetricAuditMetadata(
                    is_calculated=False,
                    confidence=1.0,
                    source="regex",
                )

        # 2. Identify missing metrics
        missing_keys = [
            key
            for key in self.CANONICAL_METRICS
            if key not in current_metrics or current_metrics[key] is None
        ]

        # If no missing metrics, return immediately
        if not missing_keys or not statement_text.strip():
            for key in missing_keys:
                final_metrics[key] = None
                audit_metadata[key] = MetricAuditMetadata(
                    is_calculated=False,
                    confidence=0.0,
                    source="unextracted",
                )
            return ExtractedFinancialMetricsDTO(
                **final_metrics,
                audit_metadata=audit_metadata,
            )

        # 3. Task 1: Prompt LLM in JSON mode for missing metrics
        messages = self._build_extraction_prompt(
            statement_text=statement_text,
            missing_keys=missing_keys,
            fiscal_year=fiscal_year,
        )

        extracted_json: Dict[str, Any] = {}
        try:
            result = self.llm_client.generate(messages)
            raw_answer = result.raw_answer.strip()
            # Clean JSON markdown fences if present
            if raw_answer.startswith("```"):
                raw_answer = re.sub(r"^```(?:json)?\s*", "", raw_answer)
                raw_answer = re.sub(r"\s*```$", "", raw_answer)
            extracted_json = json.loads(raw_answer)
        except Exception:
            extracted_json = {}

        # 4. Task 2: Process LLM results and assign audit metadata
        for key in missing_keys:
            raw_val = extracted_json.get(key)
            if raw_val is not None:
                try:
                    norm_val = FinancialUnitNormalizer.normalize_value(str(raw_val))
                    final_metrics[key] = norm_val
                    audit_metadata[key] = MetricAuditMetadata(
                        is_calculated=False,
                        confidence=0.85,
                        source="llm",
                    )
                except Exception:
                    final_metrics[key] = None
                    audit_metadata[key] = MetricAuditMetadata(
                        is_calculated=False,
                        confidence=0.0,
                        source="unextracted",
                    )
            else:
                final_metrics[key] = None
                audit_metadata[key] = MetricAuditMetadata(
                    is_calculated=False,
                    confidence=0.0,
                    source="unextracted",
                )

        return ExtractedFinancialMetricsDTO(
            **final_metrics,
            audit_metadata=audit_metadata,
        )
