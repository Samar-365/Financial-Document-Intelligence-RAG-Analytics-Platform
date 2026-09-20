"""Qualitative 7-Domain Financial Risk Classifier and Severity Ranker (Module 9.2).

Responsible for:
1. Prompting LLM via constrained JSON schema to categorize financial risks into 7 canonical domains:
   Credit, Market, Liquidity, Operational, Regulatory, Strategic, and Macroeconomic.
2. Ranking risk severity into standardized tiers: High, Medium, Low.
3. Linking each classified risk to verbatim supporting quotes and originating page numbers.
"""

import json
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from app.document_processing.metadata_tagger import TextChunkDTO #TextChunkDTO carries chunk content and page provenance
from app.rag.llm_client import OpenAIClientWrapper #OpenAI client wrapper for structured LLM inference


class RiskItemDTO(BaseModel): #Data Transfer Object defining the contract of a single categorized qualitative risk
    """Data Transfer Object representing a single qualitative business risk disclosure with full provenance."""

    category: str = Field( #One of 7 canonical financial risk domains
        ...,
        description="One of the 7 canonical financial risk domains: Credit, Market, Liquidity, Operational, Regulatory, Strategic, Macroeconomic.",
    )
    severity: str = Field( #Standardized impact level: High, Medium, Low
        ...,
        description="Assigned severity ranking: High, Medium, or Low.",
    )
    title: str = Field( #Short descriptive title summarizing the risk threat
        ...,
        min_length=3,
        description="Short, concise title identifying the specific threat.",
    )
    description: str = Field( #Analytical description explaining the mechanism and potential impact of the risk
        ...,
        min_length=5,
        description="Explanatory narrative detailing how the risk could adversely impact the business.",
    )
    supporting_quote: str = Field( #Direct text evidence extracted verbatim from the filing chunk
        ...,
        min_length=5,
        description="Direct verbatim sentence or excerpt from the document establishing source provenance.",
    )
    page_number: int = Field( #1-based originating document page number
        ...,
        ge=1,
        description="Originating PDF page number (1-based integer).",
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str: #Validates and canonicalizes the risk domain into title case
        """Ensures the risk category belongs to one of the 7 predefined domains."""
        valid_categories = { #Strict set of allowable financial risk domains
            "credit": "Credit",
            "market": "Market",
            "liquidity": "Liquidity",
            "operational": "Operational",
            "regulatory": "Regulatory",
            "strategic": "Strategic",
            "macroeconomic": "Macroeconomic",
        }
        cleaned = value.strip().lower() #Normalize case and strip whitespace
        if cleaned not in valid_categories: #Check if category matches one of the 7 valid domains
            raise ValueError(
                f"Invalid risk category '{value}'. Must be one of: {list(valid_categories.values())}."
            )
        return valid_categories[cleaned] #Return canonical title-cased domain name

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str: #Validates and canonicalizes severity to High, Medium, or Low
        """Ensures severity is one of High, Medium, or Low."""
        valid_severities = { #Strict set of allowable severity tiers
            "high": "High",
            "medium": "Medium",
            "low": "Low",
        }
        cleaned = value.strip().lower() #Normalize case and strip whitespace
        if cleaned not in valid_severities: #Reject unknown severity strings
            raise ValueError(
                f"Invalid severity '{value}'. Must be one of: High, Medium, Low."
            )
        return valid_severities[cleaned] #Return canonical capitalized severity string


class RiskClassifier: #Engine that prompts LLM to categorize risk chunks into 7 domains with severity and quotes
    """Classifies risk text disclosures into 7 canonical financial domains with severity and source provenance.

    Technical Tasks:
    1. 7-Category Classification: Prompt LLM using constrained JSON schema to classify risks into
       Credit, Market, Liquidity, Operational, Regulatory, Strategic, or Macroeconomic domains.
    2. Severity & Source Provenance Tagging: Assign severity (High, Medium, Low) and link each risk to its
       source quote and page number.
    """

    VALID_DOMAINS: List[str] = [ #Canonical list of 7 financial risk domains
        "Credit",
        "Market",
        "Liquidity",
        "Operational",
        "Regulatory",
        "Strategic",
        "Macroeconomic",
    ]

    def __init__(self, llm_client: Optional[OpenAIClientWrapper] = None) -> None: #Initialize classifier with optional injected LLM client
        """Initializes the RiskClassifier.

        Args:
            llm_client: Optional OpenAIClientWrapper instance. If None, initialized lazily.
        """
        self._llm_client = llm_client #Store injected client or leave None for lazy load

    @property
    def llm_client(self) -> OpenAIClientWrapper: #Lazy instantiation property for OpenAI client
        """Lazily instantiates OpenAIClientWrapper if not provided at construction."""
        if self._llm_client is None: #Instantiate client only when first needed
            self._llm_client = OpenAIClientWrapper()
        return self._llm_client #Return active client wrapper

    def classify_risks(self, risk_chunks: List[TextChunkDTO]) -> List[RiskItemDTO]:
        """Classifies candidate risk text chunks into 7 domains with severity and supporting page quotes.

        Args:
            risk_chunks: List of TextChunkDTO objects containing filtered risk disclosure text.

        Returns:
            List[RiskItemDTO]: Categorized risk entries with severity and provenance quotes.

        Raises:
            TypeError: If risk_chunks is not a list or elements are not TextChunkDTO instances.
        """
        if not isinstance(risk_chunks, list): #Validate that the input is a list
            raise TypeError("risk_chunks must be a list of TextChunkDTO instances.")

        if not risk_chunks: #Fast return on empty chunk list
            return []

        for idx, chunk in enumerate(risk_chunks): #Validate each element is an instance of TextChunkDTO
            if not isinstance(chunk, TextChunkDTO):
                raise TypeError(
                    f"Element at index {idx} in risk_chunks is {type(chunk).__name__}, expected TextChunkDTO."
                )

        classified_risks: List[RiskItemDTO] = [] #Collection accumulator for all parsed risk DTOs

        for chunk in risk_chunks: #Process each risk chunk individually
            content = chunk.content.strip() #Clean chunk text
            if not content: #Skip empty or whitespace chunks
                continue

            prompt_messages = self._build_classification_prompt(chunk) #Construct constrained JSON prompt
            try:
                llm_result = self.llm_client.generate(prompt_messages) #Dispatch prompt to LLM wrapper
                raw_json = llm_result.raw_answer #Extract raw text response
                parsed_items = self._parse_llm_json( #Parse and validate JSON response into RiskItemDTOs
                    raw_text=raw_json,
                    fallback_page=chunk.page_number,
                    chunk_content=content,
                )
                classified_risks.extend(parsed_items) #Accumulate successfully validated risk items
            except Exception: #Handle transient LLM generation or parsing exceptions gracefully
                continue

        return classified_risks #Return all categorized risk items

    def _build_classification_prompt(self, chunk: TextChunkDTO) -> List[Dict[str, str]]:
        """Constructs system instructions and user message commanding structured JSON risk extraction."""
        system_instruction = ( #System prompt enforcing strict schema constraints and anti-hallucination rules
            "You are a Senior Financial Risk Analyst. Analyze the provided qualitative financial disclosure "
            "and extract distinct corporate business threats.\n\n"
            "MANDATORY CLASSIFICATION DOMAINS (Category MUST be exactly one of these 7):\n"
            "- Credit: Counterparty defaults, customer creditworthiness, non-payment.\n"
            "- Market: Equity price drops, interest rate swings, FX fluctuations, commodity costs.\n"
            "- Liquidity: Working capital shortfall, cash crunches, inability to refinance debt.\n"
            "- Operational: Supply chain bottlenecks, cybersecurity breaches, tech outages, factory failures.\n"
            "- Regulatory: Antitrust lawsuits, compliance fines, tax audits, trade sanctions, legislative changes.\n"
            "- Strategic: Competitor disruption, pricing pressure, technological obsolescence, M&A integration.\n"
            "- Macroeconomic: Inflation, GDP slowdown, recession, war, geopolitical turmoil.\n\n"
            "SEVERITY RATINGS:\n"
            "- High: Existential threat, severe material losses (>10% earnings), or business suspension.\n"
            "- Medium: Notable margin contraction, operational headwinds, or moderate regulatory exposure.\n"
            "- Low: Minor incidental friction, manageable localized risks.\n\n"
            "OUTPUT FORMAT RULES:\n"
            "1. Output ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "risks": [\n'
            "    {\n"
            '      "category": "Credit|Market|Liquidity|Operational|Regulatory|Strategic|Macroeconomic",\n'
            '      "severity": "High|Medium|Low",\n'
            '      "title": "Concise Risk Title",\n'
            '      "description": "2-3 sentence analysis of the threat mechanism and business impact.",\n'
            '      "supporting_quote": "Exact verbatim quote from the text proving this risk.",\n'
            f'      "page_number": {chunk.page_number}\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "2. Do not invent or extrapolate facts. Every risk MUST have a verbatim quote from the text.\n"
            "3. If no substantive risk is identifiable, return {\"risks\": []}."
        )

        user_content = ( #User message providing document provenance and chunk body
            f"SOURCE DOCUMENT ID: {chunk.document_id}\n"
            f"PAGE NUMBER: {chunk.page_number}\n\n"
            f"DISCLOSURE TEXT:\n{chunk.content}"
        )

        return [ #Return formatted chat messages list
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content},
        ]

    def _parse_llm_json( #Parses LLM JSON string, strips markdown code fences, and validates into RiskItemDTOs
        self,
        raw_text: str,
        fallback_page: int,
        chunk_content: str,
    ) -> List[RiskItemDTO]:
        """Extracts and validates RiskItemDTO instances from LLM JSON response."""
        cleaned_text = raw_text.strip() #Strip surrounding whitespace

        #Strip markdown code block fences if present (e.g. ```json ... ```)
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
            cleaned_text = cleaned_text.strip() #Re-strip whitespace after removing fences

        try:
            data = json.loads(cleaned_text) #Parse JSON string into python dict
        except Exception:
            #Attempt to locate inner JSON object {...} if surrounding conversation exists
            match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1)) #Parse extracted regex JSON fragment
                except Exception:
                    return []
            else:
                return []

        raw_items = data.get("risks", []) #Extract risks array from JSON payload
        if not isinstance(raw_items, list): #Ensure risks is a list
            return []

        validated_risks: List[RiskItemDTO] = [] #Collector for verified RiskItemDTOs

        for item in raw_items: #Validate each dictionary item against schema
            if not isinstance(item, dict):
                continue

            try:
                #Verify and ensure page_number is valid
                page_num = item.get("page_number", fallback_page)
                if not isinstance(page_num, int) or page_num < 1:
                    page_num = fallback_page

                #Extract supporting quote and verify against chunk content
                quote = str(item.get("supporting_quote", "")).strip()
                if not quote or quote.lower() not in chunk_content.lower():
                    #If LLM modified the quote, look for a matching sentence or use provided quote
                    quote = self._find_matching_quote(quote, chunk_content) or quote

                risk_dto = RiskItemDTO( #Instantiate and validate DTO
                    category=item.get("category", ""),
                    severity=item.get("severity", ""),
                    title=str(item.get("title", "")).strip(),
                    description=str(item.get("description", "")).strip(),
                    supporting_quote=quote,
                    page_number=page_num,
                )
                validated_risks.append(risk_dto) #Append valid DTO
            except Exception: #Skip invalid risk entries that violate schema
                continue

        return validated_risks #Return list of validated RiskItemDTO objects

    def _find_matching_quote(self, candidate_quote: str, chunk_content: str) -> Optional[str]:
        """Finds the best matching sentence in the chunk text if LLM lightly edited the quote."""
        if not candidate_quote: #Return None on empty candidate
            return None

        #Split chunk content into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk_content) if len(s.strip()) > 10]
        if not sentences: #Return None if no sentences exist
            return None

        candidate_words = set(re.findall(r"\w+", candidate_quote.lower())) #Extract candidate word set
        if not candidate_words:
            return None

        best_sentence: Optional[str] = None #Track sentence with highest word overlap
        max_overlap = 0

        for sentence in sentences: #Calculate word overlap across all chunk sentences
            sentence_words = set(re.findall(r"\w+", sentence.lower()))
            overlap = len(candidate_words.intersection(sentence_words))
            if overlap > max_overlap:
                max_overlap = overlap
                best_sentence = sentence

        #Require at least 50% overlap to accept as the matching source quote
        if max_overlap >= max(3, len(candidate_words) // 2):
            return best_sentence

        return None #No sufficiently close sentence found
