# Developer 1: Micro-Module Technical Roadmap & Implementation Guide

**Role**: AI, RAG & Financial Analytics Lead  
**Domain**: Core Intelligence, Unstructured Document Extraction, Vector Search, Grounded RAG, Deterministic Ratio Modeling, Health Scoring, and Quality Evaluation  
**Architecture Principle**: Every module contains strictly one or at most two laser-focused technical tasks.  
**Execution Target**: 4 Sprints (8 Weeks standard / 4 Weeks accelerated)  

---

## 1. Developer 1 Micro-Module Topology

The complete intelligence engine is divided into **11 sequential phases** containing **32 micro-modules**. Every micro-module has a single target file, precise function signatures, and at most two atomic technical tasks.

```
+---------------------------------------------------------------------------------------+
| PHASE 1: DOCUMENT INGESTION & TEXT PREPROCESSING                                      |
|  Module 1.1: PDF File Validator & Boundary Checker   (validator.py)                   |
|  Module 1.2: Digital Text Extractor                  (text_extractor.py)              |
|  Module 1.3: Table Detection & Grid Extractor        (table_extractor.py)             |
|  Module 1.4: Financial Text Normalizer & Cleaner     (cleaner.py)                     |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 2: SEMANTIC CHUNKING & SPLITTING                                                |
|  Module 2.1: Recursive Character Splitter            (chunker.py)                     |
|  Module 2.2: Contextual Overlap & Table Boundary     (chunk_boundary.py)              |
|  Module 2.3: Chunk Metadata & Provenance Tagger      (metadata_tagger.py)             |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 3: DENSE EMBEDDINGS & VECTOR RETRIEVAL                                          |
|  Module 3.1: Dense Vector Embedding Generator        (embeddings.py)                  |
|  Module 3.2: In-Memory FAISS Vector Index            (faiss_store.py)                 |
|  Module 3.3: Vector Similarity Retriever             (retriever.py)                   |
+---------------------------------------------------------------------------------------+
                                           |
                      +--------------------+--------------------+
                      |                                         |
                      v                                         v
+-------------------------------------------+ +-----------------------------------------+
| PHASE 4: PROMPT ASSEMBLY & LLM ENGINE     | | PHASE 6: FINANCIAL METRICS EXTRACTION   |
|  Module 4.1: Context Builder & Sandboxing | |  Module 6.1: Accounting Synonym Matcher |
|  Module 4.2: Negative System Prompts      | |  Module 6.2: Currency & Unit Normalizer |
|  Module 4.3: OpenAI GPT-4o-mini Client    | |  Module 6.3: Regex Table Line Extractor |
|  Module 4.4: Local Ollama Fallback Engine | |  Module 6.4: Structured JSON Extractor  |
+-------------------------------------------+ +-----------------------------------------+
                      |                                         |
                      v                                         v
+-------------------------------------------+ +-----------------------------------------+
| PHASE 5: CITATION & PROVENANCE ENGINE     | | PHASE 7: DETERMINISTIC RATIO CALCULATOR |
|  Module 5.1: Inline Citation Regex Parser | |  Module 7.1: Profitability Ratios       |
|  Module 5.2: Snippet & Provenance Mapper  | |  Module 7.2: Liquidity Ratios           |
+-------------------------------------------+ |  Module 7.3: Leverage & Coverage Ratios |
                      |                       +-----------------------------------------+
                      |                                         |
                      |                                         v
                      |                       +-----------------------------------------+
                      |                       | PHASE 8: 5D CORPORATE HEALTH SCORING    |
                      |                       |  Module 8.1: Growth & Profit Scorer     |
                      |                       |  Module 8.2: Solvency & Cash Scorer     |
                      |                       |  Module 8.3: Health Score Aggregator    |
                      |                       +-----------------------------------------+
                      |                                         |
                      |                                         v
                      |                       +-----------------------------------------+
                      |                       | PHASE 9: QUALITATIVE RISK CLASSIFIER    |
                      |                       |  Module 9.1: Risk Disclosure Parser     |
                      |                       |  Module 9.2: 7-Domain Risk Classifier   |
                      |                       +-----------------------------------------+
                      |                                         |
                      +--------------------+--------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 10: RAGAS QUALITY EVALUATION & ADVERSARIAL BENCHMARKING                         |
|  Module 10.1: 50-Pair Golden Benchmark Dataset       (eval_dataset.py)                |
|  Module 10.2: Ragas Automated Evaluation Harness     (run_eval.py)                    |
|  Module 10.3: Prompt Injection Adversarial Harness   (test_injection.py)              |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 11: PRODUCTION PGVECTOR MIGRATION                                               |
|  Module 11.1: PostgreSQL pgvector Storage & HNSW Index (pgvector_store.py)            |
+---------------------------------------------------------------------------------------+
```

---

## 2. Micro-Module Technical Specifications

---

### Phase 1: Document Ingestion & Text Preprocessing

#### Module 1.1: PDF File Validator & Boundary Checker
* **Target File**: `app/document_processing/validator.py`
* **Dependencies**: `os`, `pydantic`
* **Sprint**: Sprint 1 (Day 1)

##### Technical Tasks (Max 2)
1. **Task 1 (Magic-Byte Inspection)**: Read the first 8 bytes of the uploaded file and verify that the header strictly matches `%PDF-1.x`. Reject any spoofed non-PDF files with error `DOC_001`.
2. **Task 2 (Size & Encryption Check)**: Enforce a strict 50 MB upper file size limit and verify that the document is not encrypted or password-protected. Throw `DOC_002` if encrypted.

##### Signatures & Contracts
```python
class ValidationResultDTO(BaseModel):
    is_valid: bool
    file_size_bytes: int
    pdf_version: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class PDFValidator:
    @staticmethod
    def validate_file(file_path: str) -> ValidationResultDTO:
        """Validates PDF magic bytes, file size, and encryption status."""
        pass
```
* **DoD**: Unit test correctly accepts valid digital PDFs and rejects corrupted files, executables, and files > 50MB.

---

#### Module 1.2: Digital Text Extractor
* **Target File**: `app/document_processing/text_extractor.py`
* **Dependencies**: `pypdf`, `pydantic`
* **Sprint**: Sprint 1 (Day 1)

##### Technical Tasks (Max 2)
1. **Task 1 (Page-by-Page Narrative Extraction)**: Iterate through all document pages and extract raw text strings preserving sequential page numbers.
2. **Task 2 (Scanned Document Detection)**: Calculate the character density per page; if an entire document yields zero extractable characters, abort and raise `PROC_002` (Scanned PDF requiring OCR).

##### Signatures & Contracts
```python
class ExtractedPageTextDTO(BaseModel):
    page_number: int
    raw_text: str
    char_count: int

class TextExtractor:
    def extract_text_by_page(self, file_path: str) -> List[ExtractedPageTextDTO]:
        """Extracts digital narrative text page by page with character density checks."""
        pass
```
* **DoD**: Extracts text from a 100-page filing in < 2 seconds; throws `PROC_002` when supplied with an image-only PDF.

---

#### Module 1.3: Table Detection & Grid Extractor
* **Target File**: `app/document_processing/table_extractor.py`
* **Dependencies**: `pdfplumber`, `pydantic`
* **Sprint**: Sprint 1 (Day 2)

##### Technical Tasks (Max 2)
1. **Task 1 (Table Bounding Box Detection)**: Use `pdfplumber` to detect horizontal and vertical cell borders on financial statement pages.
2. **Task 2 (Markdown Table Serialization)**: Convert 2D table grid cells into standardized pipe-delimited markdown tables (`| Line Item | FY24 | FY25 |`), preserving column alignment and header rows.

##### Signatures & Contracts
```python
class ExtractedTableDTO(BaseModel):
    page_number: int
    table_index: int
    markdown_table: str
    row_count: int
    col_count: int

class TableExtractor:
    def extract_tables(self, file_path: str) -> List[ExtractedTableDTO]:
        """Detects tables and serializes them into markdown pipe-delimited text blocks."""
        pass
```
* **DoD**: Financial statement balance sheet table extracts into valid markdown preserving numbers under their respective fiscal year column headers.

---

#### Module 1.4: Financial Text Normalizer & Cleaner
* **Target File**: `app/document_processing/cleaner.py`
* **Dependencies**: `re`
* **Sprint**: Sprint 1 (Day 2)

##### Technical Tasks (Max 2)
1. **Task 1 (Ligature & Character Normalization)**: Normalize Unicode ligatures (`fi` -> `fi`, `fl` -> `fl`), convert non-breaking spaces (`\u00A0`) to standard whitespace, and unify dashes.
2. **Task 2 (Header & Footer Stripping)**: Detect and remove repetitive running headers (e.g., *"ABC Limited Annual Report 2025"*) and footers based on positional coordinates to prevent chunk pollution.

##### Signatures & Contracts
```python
class TextCleaner:
    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Normalizes Unicode ligatures, cleans whitespace, and removes running headers/footers."""
        pass
```
* **DoD**: Cleans text without altering numbers, commas, decimal points, or negative brackets `(120.50)`.

---

### Phase 2: Semantic Chunking & Splitting

#### Module 2.1: Recursive Character Splitter
* **Target File**: `app/document_processing/chunker.py`
* **Dependencies**: `typing`
* **Sprint**: Sprint 1 (Day 3)

##### Technical Tasks (Max 2)
1. **Task 1 (Hierarchical Recursive Splitting)**: Implement recursive character splitting targeting an 800-character window using the priority hierarchy: `\n\n` -> `\n` -> `. ` -> `; ` -> ` `.
2. **Task 2 (Minimum Chunk Threshold)**: Merge dangling text fragments smaller than 100 characters into the preceding chunk to avoid useless sparse vectors.

##### Signatures & Contracts
```python
class TextSplitter:
    def __init__(self, target_chunk_size: int = 800, min_chunk_size: int = 100):
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size

    def split_text(self, text: str) -> List[str]:
        """Recursively splits text into target-sized character chunks."""
        pass
```
* **DoD**: Document splits with 90% of chunks between 650 and 850 characters; zero chunks smaller than 100 characters.

---

#### Module 2.2: Contextual Overlap & Table Boundary Preserver
* **Target File**: `app/document_processing/chunk_boundary.py`
* **Dependencies**: `typing`
* **Sprint**: Sprint 1 (Day 3)

##### Technical Tasks (Max 2)
1. **Task 1 (150-Character Contextual Overlap)**: Prepend the trailing 150 characters of Chunk $N$ to the beginning of Chunk $N+1$, ensuring sentences cut at boundaries remain intelligible.
2. **Task 2 (Table Integrity Lock)**: If a text block begins with a markdown table row (`|`), force the splitter to keep all table rows together up to the target window rather than splitting mid-table.

##### Signatures & Contracts
```python
class BoundaryManager:
    def apply_overlap(self, raw_chunks: List[str], overlap_size: int = 150) -> List[str]:
        """Applies backward overlap across chunk boundaries while respecting table rows."""
        pass
```
* **DoD**: 100% of consecutive chunk pairs share exact 150-character overlap; zero markdown tables split across a single cell row.

---

#### Module 2.3: Chunk Metadata & Provenance Tagger
* **Target File**: `app/document_processing/metadata_tagger.py`
* **Dependencies**: `pydantic`, `uuid`
* **Sprint**: Sprint 1 (Day 4)

##### Technical Tasks (Max 2)
1. **Task 1 (Provenance Metadata Assembly)**: Package each chunk into `TextChunkDTO` with unique UUID, `document_id`, sequential `chunk_index`, and verified source `page_number`.
2. **Task 2 (Token Count Estimation)**: Estimate token length using a 4-character-per-token heuristic and tag boolean flag `is_table_chunk`.

##### Signatures & Contracts
```python
class TextChunkDTO(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    page_number: int
    content: str
    token_estimate: int
    is_table_chunk: bool

class MetadataTagger:
    def tag_chunks(self, document_id: str, page_chunks: List[Tuple[int, str]]) -> List[TextChunkDTO]:
        """Tags chunks with UUID, document ID, page provenance, and token estimates."""
        pass
```
* **DoD**: Every chunk emits valid metadata with non-null `page_number` matching the originating PDF page.

---

### Phase 3: Dense Embeddings & Vector Retrieval

#### Module 3.1: Dense Vector Embedding Generator
* **Target File**: `app/rag/embeddings.py`
* **Dependencies**: `sentence-transformers`, `numpy`, `torch`
* **Sprint**: Sprint 1 (Day 4)

##### Technical Tasks (Max 2)
1. **Task 1 (Model Initialization & Batch Inference)**: Load `all-MiniLM-L6-v2` onto CPU and generate 384-dimensional dense vectors in batches of 32 chunks.
2. **Task 2 (L2 Unit Normalization)**: Normalize all embedding vectors to unit length ($\hat{\mathbf{v}} = \mathbf{v} / \|\mathbf{v}\|_2$) so dot products equal cosine similarity.

##### Signatures & Contracts
```python
class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        pass

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Returns L2-normalized numpy array of shape (N, 384)."""
        pass
```
* **DoD**: Embeds 500 chunks in < 3 seconds on standard CPU; every output vector has Euclidean norm equal to 1.0 (+- 1e-5).

---

#### Module 3.2: In-Memory FAISS Vector Index
* **Target File**: `app/rag/faiss_store.py`
* **Dependencies**: `faiss-cpu`, `numpy`
* **Sprint**: Sprint 1 (Day 5)

##### Technical Tasks (Max 2)
1. **Task 1 (Index Construction)**: Initialize FAISS `IndexFlatIP` (Inner Product) with 384 dimensions and add normalized chunk embeddings.
2. **Task 2 (ID Mapping Dictionary)**: Build an in-memory dictionary mapping FAISS integer indices (`0, 1, 2...`) to chunk UUIDs and metadata for lookup.

##### Signatures & Contracts
```python
class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        pass

    def add_vectors(self, document_id: str, embeddings: np.ndarray, chunks: List[TextChunkDTO]):
        """Populates FAISS index and stores chunk metadata mappings."""
        pass
```
* **DoD**: FAISS index initializes, adds vectors, and retrieves correct metadata by integer index.

---

#### Module 3.3: Vector Similarity Retriever
* **Target File**: `app/rag/retriever.py`
* **Dependencies**: `faiss-cpu`, `pydantic`
* **Sprint**: Sprint 1 (Day 5)

##### Technical Tasks (Max 2)
1. **Task 1 (Top-K Similarity Retrieval)**: Given a 384-dim query vector, execute `index.search()` to retrieve Top-K ($K=5$) nearest chunk candidates.
2. **Task 2 (Confidence Threshold Filtering)**: Filter out chunks with cosine similarity score $< 0.45$, returning only high-confidence financial context.

##### Signatures & Contracts
```python
class RetrievedChunkDTO(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    page_number: int
    content: str
    similarity_score: float

class VectorRetriever:
    def retrieve(self, document_id: str, query_vector: np.ndarray, top_k: int = 5) -> List[RetrievedChunkDTO]:
        """Retrieves Top-K chunks filtered by similarity threshold."""
        pass
```
* **DoD**: Sub-20ms search response time; chunks below score threshold are discarded.

---

### Phase 4: Grounded Prompt Assembly & LLM Generation

#### Module 4.1: Context Builder & Delimiter Sandboxing
* **Target File**: `app/rag/prompt_builder.py`
* **Dependencies**: `typing`
* **Sprint**: Sprint 2 (Day 6)

##### Technical Tasks (Max 2)
1. **Task 1 (XML Delimiter Isolation)**: Wrap retrieved chunks inside structural XML tags (`<context>...</context>`) to neutralize prompt injection instructions.
2. **Task 2 (Provenance Tag Formatting)**: Prepend each chunk with its citation marker: `[Doc: {doc_name}, Page: {page_number}]`.

##### Signatures & Contracts
```python
class PromptBuilder:
    @staticmethod
    def build_context_block(chunks: List[RetrievedChunkDTO]) -> str:
        """Formats retrieved chunks into delimited XML context blocks with citation markers."""
        pass
```
* **DoD**: Returns cleanly formatted context string containing all Top-K excerpts demarcated with page headers.

---

#### Module 4.2: Negative-Constraint System Prompt Formulation
* **Target File**: `app/rag/system_prompts.py`
* **Dependencies**: `typing`
* **Sprint**: Sprint 2 (Day 6)

##### Technical Tasks (Max 2)
1. **Task 1 (Negative Constraint Prompt Rule)**: Formulate system prompt commanding the model to answer *only* from context and state failure if data is absent.
2. **Task 2 (Standardized Fallback String)**: Define deterministic fallback token string: *"The provided document does not contain sufficient information to answer this query."*

##### Signatures & Contracts
```python
class FinancialSystemPrompts:
    RAG_SYSTEM_PROMPT: str
    FALLBACK_RESPONSE: str = "The provided document does not contain sufficient information to answer this query."

    @classmethod
    def get_grounded_prompt(cls, user_query: str, context_block: str) -> List[Dict[str, str]]:
        """Returns OpenAI-compatible messages list with system instructions and user context."""
        pass
```
* **DoD**: Prompt passes audit for strict compliance, instructing model never to extrapolate or fabricate.

---

#### Module 4.3: OpenAI GPT-4o-mini Client Wrapper
* **Target File**: `app/rag/llm_client.py`
* **Dependencies**: `openai`, `pydantic`
* **Sprint**: Sprint 2 (Day 7)

##### Technical Tasks (Max 2)
1. **Task 1 (Deterministic Inference Dispatch)**: Dispatch prompt to OpenAI GPT-4o-mini with `temperature=0.1`, `top_p=0.95`, and `max_tokens=1024`.
2. **Task 2 (Rate Limit & Exponential Retry)**: Implement retry logic handling HTTP 429 (Rate Limit) and 503 (Service Unavailable) with backoff.

##### Signatures & Contracts
```python
class LLMGenerationResultDTO(BaseModel):
    raw_answer: str
    prompt_tokens: int
    completion_tokens: int
    model_name: str

class OpenAIClientWrapper:
    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Calls GPT-4o-mini with deterministic parameters and retry handling."""
        pass
```
* **DoD**: Returns answer text and token metrics; retries up to 3 times on transient network drops.

---

#### Module 4.4: Local Air-Gapped Ollama Fallback Engine
* **Target File**: `app/rag/ollama_client.py`
* **Dependencies**: `requests`, `pydantic`
* **Sprint**: Sprint 2 (Day 7)

##### Technical Tasks (Max 2)
1. **Task 1 (Ollama REST Integration)**: Query local Ollama instance (`http://localhost:11434/api/chat` with `llama3` or `mistral`).
2. **Task 2 (Automatic Failover Switch)**: If OpenAI API fails after retries or if `AIR_GAPPED_MODE=True`, route query to Ollama transparently.

##### Signatures & Contracts
```python
class OllamaClientWrapper:
    def generate(self, messages: List[Dict[str, str]]) -> LLMGenerationResultDTO:
        """Queries local Ollama instance for zero-network-egress air-gapped inference."""
        pass
```
* **DoD**: System returns complete answers when internet access is disabled.

---

### Phase 5: Citation Parsing & Hallucination Mitigation

#### Module 5.1: Inline Citation Regex Parser
* **Target File**: `app/rag/citation_parser.py`
* **Dependencies**: `re`, `typing`
* **Sprint**: Sprint 2 (Day 8)

##### Technical Tasks (Max 2)
1. **Task 1 (Citation Token Extraction)**: Parse inline bracketed citation markers using regex: `r"\[Doc:\s*([^,]+),\s*Page:\s*(\d+)\]"`.
2. **Task 2 (Citation Deduplication)**: Deduplicate multiple identical page citations, preserving first-occurrence order.

##### Signatures & Contracts
```python
class RawCitationToken(BaseModel):
    document_name: str
    page_number: int

class CitationParser:
    @staticmethod
    def parse_citations(text: str) -> List[RawCitationToken]:
        """Extracts unique [Doc: X, Page: Y] tokens from generated text."""
        pass
```
* **DoD**: Parses `[Doc: annual_report.pdf, Page: 42]` into structured token with page integer 42.

---

#### Module 5.2: Provenance Verification & Snippet Mapper
* **Target File**: `app/rag/citation_verifier.py`
* **Dependencies**: `pydantic`, `typing`
* **Sprint**: Sprint 2 (Day 8)

##### Technical Tasks (Max 2)
1. **Task 1 (Retrieved Chunk Cross-Referencing)**: Verify that cited page numbers exist in the Top-K retrieved chunks. Flag phantom citations.
2. **Task 2 (Evidence Snippet Extraction)**: Extract the exact sentence from the source chunk to serve as verifiable proof in UI citation cards.

##### Signatures & Contracts
```python
class VerifiedCitationDTO(BaseModel):
    citation_id: str
    document_name: str
    page_number: int
    source_snippet: str
    is_verified: bool

class CitationVerifier:
    def verify_citations(
        self, tokens: List[RawCitationToken], retrieved_chunks: List[RetrievedChunkDTO]
    ) -> List[VerifiedCitationDTO]:
        """Cross-references citations against retrieved chunks and extracts text evidence."""
        pass
```
* **DoD**: 100% of valid citations contain verifiable snippet text; phantom citations flagged `is_verified=False`.

---

### Phase 6: Quantitative Financial Line-Item Extraction

#### Module 6.1: Accounting Synonym & Terminology Matcher
* **Target File**: `app/analytics/synonym_matcher.py`
* **Dependencies**: `typing`
* **Sprint**: Sprint 2 (Day 9)

##### Technical Tasks (Max 2)
1. **Task 1 (Standard Metric Synonym Registry)**: Build dictionary mapping Indian and global accounting aliases to 12 canonical metric keys (e.g., `Turnover`, `Net Sales` -> `revenue`).
2. **Task 2 (Statement Classification Rules)**: Classify metric targets into P&L, Balance Sheet, or Cash Flow domains.

##### Signatures & Contracts
```python
class SynonymMatcher:
    SYNONYM_REGISTRY: Dict[str, List[str]]

    @classmethod
    def resolve_metric_name(cls, line_label: str) -> Optional[str]:
        """Matches raw text label against canonical 12 financial metric keys."""
        pass
```
* **DoD**: Successfully maps 20+ accounting variations to canonical metric keys.

---

#### Module 6.2: Financial Currency & Unit Normalizer
* **Target File**: `app/analytics/unit_normalizer.py`
* **Dependencies**: `decimal`, `re`
* **Sprint**: Sprint 2 (Day 9)

##### Technical Tasks (Max 2)
1. **Task 1 (Indian Unit Scaling)**: Detect `Crore` (`Cr`) and `Lakh` multipliers, converting to base numbers (e.g., `12.5 Cr` -> `125,000,000`).
2. **Task 2 (Western Unit Scaling & Parentheses)**: Convert `Million` (`M`) and `Billion` (`B`), and parse accounting negative parentheses `(1,250)` to `-1250`.

##### Signatures & Contracts
```python
class FinancialUnitNormalizer:
    @staticmethod
    def normalize_value(raw_string: str, document_unit: str = "base") -> Decimal:
        """Parses currency strings into exact Decimal base currency representations."""
        pass
```
* **DoD**: `₹ 1,250.50 Cr` converts to `Decimal('12505000000.00')`; `(45.20) M` converts to `Decimal('-45200000.00')`.

---

#### Module 6.3: Regex Tabular Line-Item Extractor
* **Target File**: `app/analytics/regex_extractor.py`
* **Dependencies**: `decimal`, `re`
* **Sprint**: Sprint 2 (Day 10)

##### Technical Tasks (Max 2)
1. **Task 1 (Markdown Table Line Matching)**: Scan markdown tables for canonical metric aliases and extract figures in the active fiscal year column.
2. **Task 2 (Multi-Year Column Alignment)**: Detect fiscal year column headers (`FY24`, `FY25`, `2024`, `2025`) to extract the correct column value.

##### Signatures & Contracts
```python
class RegexMetricExtractor:
    def extract_from_tables(
        self, markdown_tables: List[str], target_year: str
    ) -> Dict[str, Decimal]:
        """Scans tables for 12 financial metrics matching target fiscal year column."""
        pass
```
* **DoD**: Accurately extracts Revenue, EBIT, and PAT from standard annual report tabular disclosures.

---

#### Module 6.4: Structured LLM JSON Fallback Extractor
* **Target File**: `app/analytics/llm_extractor.py`
* **Dependencies**: `openai`, `pydantic`
* **Sprint**: Sprint 2 (Day 10)

##### Technical Tasks (Max 2)
1. **Task 1 (Constrained JSON Schema Extraction)**: For line items missed by regex, prompt GPT-4o-mini using Pydantic JSON mode on financial statement pages.
2. **Task 2 (Audit Metadata Assignment)**: Mark extracted values with `is_calculated` and `confidence` metadata to preserve transparency.

##### Signatures & Contracts
```python
class ExtractedFinancialMetricsDTO(BaseModel):
    document_id: str
    fiscal_year: str
    currency: str = "INR"
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

class LLMMetricExtractor:
    def extract_missing_metrics(
        self, statement_text: str, current_metrics: Dict[str, Decimal]
    ) -> ExtractedFinancialMetricsDTO:
        """Extracts missing line items using structured LLM JSON schema mode."""
        pass
```
* **DoD**: Fills missing metrics with valid `Decimal` values; returns `None` when items are genuinely unstated.

---

### Phase 7: Deterministic Financial Ratios Calculation

#### Module 7.1: Profitability Ratios Calculator
* **Target File**: `app/analytics/ratios_profitability.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 1 (Day 5 - Early Contract Delivery)

##### Technical Tasks (Max 2)
1. **Task 1 (Operating & Net Margin Formulas)**: Compute Operating Profit Margin (OPM) and Net Profit Margin (NPM) with zero-revenue division guards.
2. **Task 2 (Return Ratios Formulas)**: Compute Return on Equity (ROE) and Return on Capital Employed (ROCE), asserting capital employed $> 0$.

##### Signatures & Contracts
```python
class ProfitabilityRatiosDTO(BaseModel):
    operating_profit_margin: Optional[float] = None
    net_profit_margin: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_capital_employed: Optional[float] = None
    warnings: List[str] = []

class ProfitabilityCalculator:
    @staticmethod
    def calculate(metrics: ExtractedFinancialMetricsDTO) -> ProfitabilityRatiosDTO:
        """Computes OPM, NPM, ROE, ROCE with zero-division protections."""
        pass
```
* **DoD**: Returns `OPM = 15.5` for Revenue 1000 and EBIT 155; returns `None` without crashing when Revenue == 0.

---

#### Module 7.2: Liquidity & Solvency Ratios Calculator
* **Target File**: `app/analytics/ratios_liquidity.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 1 (Day 5 - Early Contract Delivery)

##### Technical Tasks (Max 2)
1. **Task 1 (Current Ratio Formula)**: Compute Current Ratio ($\text{Current Assets} / \text{Current Liabilities}$) with zero-denominator protection.
2. **Task 2 (Quick Ratio Formula)**: Compute Quick Ratio ($(\text{Current Assets} - \text{Inventories}) / \text{Current Liabilities}$) with fallback to Current Assets if inventory unstated.

##### Signatures & Contracts
```python
class LiquidityRatiosDTO(BaseModel):
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    warnings: List[str] = []

class LiquidityCalculator:
    @staticmethod
    def calculate(metrics: ExtractedFinancialMetricsDTO) -> LiquidityRatiosDTO:
        """Computes Current and Quick ratios with zero-liability safeguards."""
        pass
```
* **DoD**: Current Ratio returns float matching manual calculation; returns warning if current liabilities are zero.

---

#### Module 7.3: Leverage & Coverage Ratios Calculator
* **Target File**: `app/analytics/ratios_leverage.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 1 (Day 5 - Early Contract Delivery)

##### Technical Tasks (Max 2)
1. **Task 1 (Debt-to-Equity Formula)**: Compute Debt-to-Equity ($\text{Total Debt} / \text{Shareholder Equity}$) and flag warning if Equity $< 0$.
2. **Task 2 (Interest Coverage Formula)**: Compute Interest Coverage Ratio ($\text{EBIT} / \text{Interest Expense}$) with zero-debt check.

##### Signatures & Contracts
```python
class LeverageRatiosDTO(BaseModel):
    debt_to_equity: Optional[float] = None
    interest_coverage_ratio: Optional[float] = None
    warnings: List[str] = []

class LeverageCalculator:
    @staticmethod
    def calculate(metrics: ExtractedFinancialMetricsDTO, interest_expense: Optional[Decimal] = None) -> LeverageRatiosDTO:
        """Computes D/E and ICR with negative equity distress flags."""
        pass
```
* **DoD**: D/E correctly handles zero debt (`D/E = 0.0`) and negative equity with explicit warnings.

---

### Phase 8: Explainable 5-Dimension Corporate Health Scoring

#### Module 8.1: Growth & Profitability Scoring Engine
* **Target File**: `app/analytics/health_growth_profit.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 2 (Day 10)

##### Technical Tasks (Max 2)
1. **Task 1 (Growth Scoring Engine - 20% Weight)**: Score YoY Revenue Growth ($>10\% \rightarrow 100$) and PAT Growth ($>15\% \rightarrow 100$) using piecewise linear mapping.
2. **Task 2 (Profitability Scoring Engine - 25% Weight)**: Score Operating Margin ($>15\% \rightarrow 100$) and Net Margin ($>10\% \rightarrow 100$), deducting points for margin contraction.

##### Signatures & Contracts
```python
class DimensionScoreDTO(BaseModel):
    score: float  # 0 to 100
    grade: str   # Excellent, Good, Fair, Poor
    deductions: List[str]

class GrowthProfitScorer:
    def score_growth(self, rev_growth: Optional[float], pat_growth: Optional[float]) -> DimensionScoreDTO:
        """Scores Growth dimension (20% weight)."""
        pass

    def score_profitability(self, opm: Optional[float], npm: Optional[float]) -> DimensionScoreDTO:
        """Scores Profitability dimension (25% weight)."""
        pass
```
* **DoD**: Accurately computes sub-scores and provides human-readable deduction strings.

---

#### Module 8.2: Solvency & Cash Flow Scoring Engine
* **Target File**: `app/analytics/health_solvency_cash.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 2 (Day 10)

##### Technical Tasks (Max 2)
1. **Task 1 (Liquidity & Leverage Scoring - 40% Weight)**: Score Liquidity (optimal Current Ratio between 1.5 and 2.5) and Leverage (penalizing D/E $> 2.0x$).
2. **Task 2 (Cash Flow Quality Scoring - 15% Weight)**: Score CFO / Net Income ratio ($\ge 1.0 \rightarrow 100$), penalizing paper earnings not backed by operational cash collections.

##### Signatures & Contracts
```python
class SolvencyCashScorer:
    def score_liquidity_leverage(
        self, current_ratio: Optional[float], debt_to_equity: Optional[float]
    ) -> Tuple[DimensionScoreDTO, DimensionScoreDTO]:
        """Scores Liquidity (20%) and Leverage (20%) dimensions."""
        pass

    def score_cash_flow(self, cfo: Optional[Decimal], pat: Optional[Decimal]) -> DimensionScoreDTO:
        """Scores Cash Flow Quality (15%) dimension."""
        pass
```
* **DoD**: Correctly penalizes companies with high D/E ($>2.0$) and poor cash-to-net-income conversion.

---

#### Module 8.3: Composite Health Score & Rationale Aggregator
* **Target File**: `app/analytics/health_scorer.py`
* **Dependencies**: `pydantic`
* **Sprint**: Sprint 2 (Day 10)

##### Technical Tasks (Max 2)
1. **Task 1 (Weighted Score Aggregator)**: Compute overall composite score (0–100) using weights: Growth 20%, Profit 25%, Liquidity 20%, Leverage 20%, Cash Flow 15%.
2. **Task 2 (Executive Rationale Generator)**: Compile overall rating (`Strong`, `Stable`, `Moderate`, `Fragile`, `Distressed`) and append standard regulatory disclaimer.

##### Signatures & Contracts
```python
class CorporateHealthReportDTO(BaseModel):
    overall_score: float  # 0 to 100
    rating_category: str
    dimension_scores: Dict[str, DimensionScoreDTO]
    summary_rationales: List[str]
    disclaimer: str

class HealthScoreAggregator:
    def aggregate(
        self, growth: DimensionScoreDTO, profit: DimensionScoreDTO, liquidity: DimensionScoreDTO, leverage: DimensionScoreDTO, cash_flow: DimensionScoreDTO
    ) -> CorporateHealthReportDTO:
        """Aggregates dimensional scores into final explainable corporate health report."""
        pass
```
* **DoD**: Score calculation is 100% deterministic; includes regulatory disclaimer string.

---

### Phase 9: Qualitative Risk Analysis & Categorization

#### Module 9.1: Risk Factor Disclosure Parser
* **Target File**: `app/analytics/risk_parser.py`
* **Dependencies**: `re`, `typing`
* **Sprint**: Sprint 3 (Day 11)

##### Technical Tasks (Max 2)
1. **Task 1 (Item 1A Section Locator)**: Scan document chunks for Item 1A / Risk Disclosures headers and isolate candidate risk paragraphs.
2. **Task 2 (Boilerplate Noise Filtering)**: Filter out standard generic regulatory disclaimers using keyword heuristics to retain specific business threats.

##### Signatures & Contracts
```python
class RiskDisclosureParser:
    def locate_risk_sections(self, chunks: List[TextChunkDTO]) -> List[TextChunkDTO]:
        """Extracts and filters candidate risk factor disclosure chunks."""
        pass
```
* **DoD**: Isolates risk sections from 10-K / Annual Reports; discards generic legal boilerplate.

---

#### Module 9.2: 7-Domain Risk Classifier & Severity Ranker
* **Target File**: `app/analytics/risk_classifier.py`
* **Dependencies**: `openai`, `pydantic`
* **Sprint**: Sprint 3 (Day 11)

##### Technical Tasks (Max 2)
1. **Task 1 (7-Category Classification)**: Prompt LLM using constrained JSON schema to classify risks into Credit, Market, Liquidity, Operational, Regulatory, Strategic, or Macroeconomic domains.
2. **Task 2 (Severity & Source Provenance Tagging)**: Assign severity (`High`, `Medium`, `Low`) and link each risk to its source quote and page number.

##### Signatures & Contracts
```python
class RiskItemDTO(BaseModel):
    category: str  # One of 7 domains
    severity: str  # High, Medium, Low
    title: str
    description: str
    supporting_quote: str
    page_number: int

class RiskClassifier:
    def classify_risks(self, risk_chunks: List[TextChunkDTO]) -> List[RiskItemDTO]:
        """Classifies risk text into 7 domains with severity and supporting page quotes."""
        pass
```
* **DoD**: Output contains at least 3 categorized risk entries with direct supporting quotes and page numbers.

---

### Phase 10: Ragas AI Quality Evaluation & Benchmarking

#### Module 10.1: 50-Pair Golden Benchmark Dataset Formulator
* **Target File**: `evaluation/eval_dataset.py`
* **Dependencies**: `json`, `pydantic`
* **Sprint**: Sprint 3 (Day 12)

##### Technical Tasks (Max 2)
1. **Task 1 (Curate 50 Benchmark Q&A Pairs)**: Formulate 50 ground-truth pairs: 20 Factual, 10 Analytical, 10 Risk, 5 Comparative, and 5 Negative tests.
2. **Task 2 (JSON Schema Serialization)**: Validate and export dataset to `evaluation/benchmark_dataset.json` with questions, expected facts, and source pages.

##### Signatures & Contracts
```python
class BenchmarkQAPair(BaseModel):
    id: str
    category: str  # factual, analytical, risk, comparative, negative
    question: str
    expected_answer_keywords: List[str]
    expected_page_numbers: List[int]
    should_answer: bool

class BenchmarkDatasetManager:
    @staticmethod
    def load_dataset(path: str) -> List[BenchmarkQAPair]:
        """Loads and validates golden benchmark dataset."""
        pass
```
* **DoD**: Dataset passes JSON schema validation; contains all 5 required test categories.

---

#### Module 10.2: Ragas Automated Metric Harness & Reporter
* **Target File**: `evaluation/run_eval.py`
* **Dependencies**: `ragas`, `pytest`, `pandas`
* **Sprint**: Sprint 3 (Day 13)

##### Technical Tasks (Max 2)
1. **Task 1 (Ragas Pipeline Execution)**: Run batch evaluation computing Faithfulness, Answer Relevance, and Context Precision across the benchmark dataset.
2. **Task 2 (Benchmark Target Assertion)**: Output statistical scorecard and assert targets: Faithfulness >= 0.90, Answer Relevance >= 0.85, Context Precision >= 0.85.

##### Signatures & Contracts
```python
class EvaluationScorecardDTO(BaseModel):
    faithfulness: float
    answer_relevance: float
    context_precision: float
    context_recall: float
    all_targets_met: bool

class RagasEvaluator:
    def evaluate_pipeline(self, dataset: List[BenchmarkQAPair]) -> EvaluationScorecardDTO:
        """Executes automated Ragas evaluation suite and returns scorecard."""
        pass
```
* **DoD**: Outputs formatted evaluation summary; pipeline fails CI if Faithfulness < 0.90.

---

#### Module 10.3: Prompt Injection Adversarial Test Suite
* **Target File**: `tests/evaluation/test_injection.py`
* **Dependencies**: `pytest`
* **Sprint**: Sprint 3 (Day 14)

##### Technical Tasks (Max 2)
1. **Task 1 (Adversarial Payload Generation)**: Formulate test suite of 10 indirect prompt injection payloads embedded in synthetic document chunks.
2. **Task 2 (Boundary Neutralization Assertion)**: Verify that XML delimiter sandboxing prevents the LLM from executing override instructions (100% defense rate).

##### Signatures & Contracts
```python
def test_prompt_injection_neutralized():
    """Asserts that malicious system override instructions in chunks are ignored."""
    pass
```
* **DoD**: 100% of injected instructions are treated strictly as passive context data and ignored.

---

### Phase 11: Production Vector Store Migration

#### Module 11.1: PostgreSQL pgvector Storage & HNSW Index
* **Target File**: `app/rag/pgvector_store.py`
* **Dependencies**: `sqlalchemy`, `pgvector`
* **Sprint**: Sprint 4 (Day 16-17)

##### Technical Tasks (Max 2)
1. **Task 1 (pgvector Table Persistence)**: Migrate chunk embeddings from in-memory FAISS into PostgreSQL `document_chunks` table using `Vector(384)` column.
2. **Task 2 (HNSW Index & Latency Benchmark)**: Configure HNSW cosine index (`vector_cosine_ops`) and benchmark sub-50ms query execution across 50,000 vectors.

##### Signatures & Contracts
```python
class PGVectorStore:
    def store_embeddings(self, session, document_id: str, chunks: List[TextChunkDTO], embeddings: np.ndarray):
        """Persists 384-dim embeddings into PostgreSQL document_chunks table."""
        pass

    def search_similar(self, session, query_vector: np.ndarray, top_k: int = 5) -> List[RetrievedChunkDTO]:
        """Executes HNSW nearest-neighbor cosine search in PostgreSQL."""
        pass
```
* **DoD**: Search queries against pgvector return identical Top-5 results to FAISS with < 50ms latency.

---

## 3. Sprint Timeline & Day-by-Day Tactical Checklist

| Sprint | Days | Micro-Modules Covered | Primary Milestone Delivered |
| :--- | :--- | :--- | :--- |
| **Sprint 1** | Days 1-2 | Modules 1.1, 1.2, 1.3, 1.4 | High-fidelity PDF text and table extraction engine |
| **Sprint 1** | Days 3-4 | Modules 2.1, 2.2, 2.3, 3.1 | Financial chunking (800/150) and embedding generation |
| **Sprint 1** | Day 5 | Modules 3.2, 3.3, 7.1, 7.2, 7.3 | FAISS index setup + 8 financial ratios calculator |
| **Sprint 2** | Days 6-7 | Modules 4.1, 4.2, 4.3, 4.4 | Grounded RAG engine with GPT-4o-mini & Ollama |
| **Sprint 2** | Day 8 | Modules 5.1, 5.2 | Citation parser and source snippet evidence mapper |
| **Sprint 2** | Days 9-10 | Modules 6.1, 6.2, 6.3, 6.4, 8.1, 8.2, 8.3 | 12 metrics extractor + 5D health scoring engine |
| **Sprint 3** | Day 11 | Modules 9.1, 9.2 | 7-domain qualitative risk classifier |
| **Sprint 3** | Days 12-14 | Modules 10.1, 10.2, 10.3 | 50-pair golden dataset, Ragas harness, prompt security |
| **Sprint 4** | Days 15-18 | Module 11.1 | pgvector migration, latency profiling, final report |

---

## 4. Immediate Day 1 Action Plan

To start right now:

1. Create directory layout:
   ```bash
   mkdir -p app/document_processing app/rag app/analytics evaluation tests/evaluation
   ```
2. Build **Module 7.1, 7.2, 7.3 (`ratios_profitability.py`, `ratios_liquidity.py`, `ratios_leverage.py`)**:
   - Zero external dependencies.
   - You can code and unit test all 8 ratios in the first 3 hours.
   - Hand the `FinancialRatiosDTO` schema to Developer 2 to unblock database and API routes.
3. Build **Module 1.1 (`validator.py`)** & **Module 1.2 (`text_extractor.py`)**:
   - Implement magic-byte checks and page-by-page text extraction on a sample annual report PDF.
