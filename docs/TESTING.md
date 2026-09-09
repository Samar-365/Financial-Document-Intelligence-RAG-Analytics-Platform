# Testing Strategy

## Financial Document Intelligence & RAG Analytics Platform

| Field | Value |
|---|---|
| **Framework** | pytest |
| **API Testing** | FastAPI TestClient |
| **Coverage Target** | ≥ 80% (unit tests) |

---

## Table of Contents

- [1. Testing Overview](#1-testing-overview)
- [2. Unit Testing](#2-unit-testing)
- [3. Integration Testing](#3-integration-testing)
- [4. API Testing](#4-api-testing)
- [5. RAG Evaluation](#5-rag-evaluation)
- [6. UI Testing](#6-ui-testing)
- [7. Test Configuration](#7-test-configuration)

---

## 1. Testing Overview

### Test Pyramid

```
          ┌─────────┐
          │   UI    │  Manual / Smoke tests
         ┌┴─────────┴┐
         │    RAG    │  Evaluation framework
        ┌┴───────────┴┐
        │    API     │  Endpoint tests (TestClient)
       ┌┴─────────────┴┐
       │ Integration  │  Pipeline tests
      ┌┴───────────────┴┐
      │   Unit Tests   │  Functions & classes
      └─────────────────┘
```

| Layer | Count (Target) | Framework | Execution |
|---|---|---|---|
| Unit | 40+ tests | pytest | Every commit (CI) |
| Integration | 10+ tests | pytest | Every PR (CI) |
| API | 15+ tests | pytest + TestClient | Every PR (CI) |
| RAG Evaluation | 10+ test cases | Custom + pytest | Weekly / manual |
| UI | Manual checklist | Manual | Pre-release |

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
pytest tests/evaluation/

# Run with verbose output
pytest -v --tb=short

# Run a specific test file
pytest tests/unit/test_ratio_calculator.py

# Run tests matching a keyword
pytest -k "test_revenue"
```

---

## 2. Unit Testing

Unit tests validate individual functions and classes in isolation.

### 2.1 PDF Extraction Tests

**File**: `tests/unit/test_pdf_extractor.py`

| Test Case | Input | Expected Output | Purpose |
|---|---|---|---|
| `test_extract_text_valid_pdf` | Valid PDF file | Extracted text with page mapping | Verify basic text extraction |
| `test_extract_text_multipage` | 10-page PDF | Text from all 10 pages | Verify page completeness |
| `test_extract_tables` | PDF with financial table | Structured table data | Verify table extraction |
| `test_extract_empty_page` | PDF with blank page | Empty string for blank page | Handle empty pages gracefully |
| `test_extract_invalid_file` | Non-PDF file | Raises `ExtractionError` | Reject invalid input |
| `test_extract_corrupt_pdf` | Corrupt PDF | Raises `ExtractionError` | Handle corruption |

### 2.2 Chunking Tests

**File**: `tests/unit/test_chunking.py`

| Test Case | Input | Expected Output | Purpose |
|---|---|---|---|
| `test_chunk_basic_text` | 2000-word text, size=512 | ~4 chunks with overlap | Verify chunk count and size |
| `test_chunk_overlap` | Text with known boundary | Overlapping content between chunks | Verify overlap preservation |
| `test_chunk_short_text` | 100-word text | 1 chunk | Handle short texts |
| `test_chunk_empty_text` | Empty string | Empty list | Handle empty input |
| `test_chunk_preserves_sentences` | Text with sentences | Chunks split at sentence boundaries | Verify sentence-boundary splitting |
| `test_chunk_metadata` | Text with page info | Chunks with page_number metadata | Verify metadata attachment |

### 2.3 Financial Calculation Tests

**File**: `tests/unit/test_ratio_calculator.py`

| Test Case | Input | Expected Output | Purpose |
|---|---|---|---|
| `test_revenue_growth` | Rev: 10000 → 11000 | 10.0% | Verify growth calculation |
| `test_revenue_growth_negative` | Rev: 10000 → 9000 | -10.0% | Handle negative growth |
| `test_revenue_growth_zero_base` | Rev: 0 → 5000 | N/A | Handle division by zero |
| `test_profit_margin` | NI: 1400, Rev: 11000 | 12.73% | Verify margin calculation |
| `test_current_ratio` | CA: 5000, CL: 3000 | 1.67 | Verify ratio calculation |
| `test_debt_to_equity` | Debt: 4000, Eq: 8000 | 0.50 | Verify leverage ratio |
| `test_roe` | NI: 1400, Eq: 8000 | 17.50% | Verify return calculation |
| `test_ratio_missing_input` | NI: None, Rev: 11000 | None with reason | Handle missing data |

### 2.4 Health Score Tests

**File**: `tests/unit/test_health_score.py`

| Test Case | Input | Expected Output | Purpose |
|---|---|---|---|
| `test_perfect_scores` | All metrics excellent | Score ~100 | Verify ceiling |
| `test_zero_scores` | All metrics poor | Score ~0 | Verify floor |
| `test_weighted_calculation` | Known dimension scores | Correct weighted average | Verify weight application |
| `test_missing_dimension` | One dimension missing | Weights redistributed, score calculated | Handle partial data |
| `test_score_range` | Any valid input | 0 ≤ score ≤ 100 | Validate score bounds |
| `test_normalization` | Known metric values | Correct normalized sub-scores | Verify normalization logic |

### 2.5 Risk Analyzer Tests

**File**: `tests/unit/test_risk_analyzer.py`

| Test Case | Input | Expected Output | Purpose |
|---|---|---|---|
| `test_identify_financial_risk` | Text mentioning debt increase | Financial risk identified | Detect financial risk language |
| `test_identify_regulatory_risk` | Text about compliance | Regulatory risk identified | Detect regulatory risk |
| `test_severity_high` | "Significant" debt increase | Severity: High | Verify severity assignment |
| `test_severity_low` | "Minor" concern | Severity: Low | Verify low severity |
| `test_no_risks` | Text without risk indicators | Empty risk list | Handle no-risk documents |
| `test_risk_evidence` | Risk text with page info | Risk with page reference | Verify evidence attachment |

---

## 3. Integration Testing

Integration tests validate end-to-end pipeline flows.

### 3.1 Document Processing Pipeline

**File**: `tests/integration/test_document_pipeline.py`

| Test Case | Flow | Validates |
|---|---|---|
| `test_full_document_pipeline` | Upload → Extract → Clean → Chunk → Embed → Store | Complete pipeline produces indexed chunks |
| `test_pipeline_creates_metrics` | Upload → Process → Extract Metrics | Financial metrics are extracted and stored |
| `test_pipeline_status_transitions` | Upload → Process | Status: UPLOADED → PROCESSING → PROCESSED |
| `test_pipeline_failure_handling` | Upload corrupt PDF → Process | Status: UPLOADED → PROCESSING → FAILED |
| `test_pipeline_idempotency` | Process same document twice | No duplicate chunks or metrics |

### 3.2 RAG Pipeline

**File**: `tests/integration/test_rag_pipeline.py`

| Test Case | Flow | Validates |
|---|---|---|
| `test_rag_end_to_end` | Upload → Process → Query | Returns relevant answer with citations |
| `test_rag_citation_accuracy` | Process known document → Query with known answer | Citations point to correct pages |
| `test_rag_no_context` | Query about non-existent topic | Returns "not found" message |
| `test_rag_document_filter` | Two documents uploaded → Query filtered to one | Only retrieves from target document |

### 3.3 Analytics Pipeline

**File**: `tests/integration/test_analytics_pipeline.py`

| Test Case | Flow | Validates |
|---|---|---|
| `test_analytics_full` | Process → Extract → Calculate Ratios → Score → Risks | Complete analytics output |
| `test_comparison` | Two documents → Compare | Metric differences calculated correctly |

---

## 4. API Testing

API tests validate REST endpoint behavior using FastAPI's `TestClient`.

**Files**: `tests/api/test_*_api.py`

### 4.1 Document API Tests

| Test Case | Method | Endpoint | Validates |
|---|---|---|---|
| `test_upload_valid_pdf` | POST | `/documents/upload` | 201 Created + document metadata |
| `test_upload_invalid_file` | POST | `/documents/upload` | 400 Bad Request |
| `test_upload_oversized` | POST | `/documents/upload` | 400 with size error |
| `test_list_documents` | GET | `/documents` | 200 + document list |
| `test_list_filter_status` | GET | `/documents?status=PROCESSED` | Filtered results |
| `test_get_document` | GET | `/documents/{id}` | 200 + document details |
| `test_get_nonexistent` | GET | `/documents/{bad_id}` | 404 Not Found |
| `test_delete_document` | DELETE | `/documents/{id}` | 200 + deletion confirmation |
| `test_process_document` | POST | `/documents/{id}/process` | 202 Accepted |

### 4.2 Query API Tests

| Test Case | Method | Endpoint | Validates |
|---|---|---|---|
| `test_query_valid` | POST | `/query` | 200 + answer + citations |
| `test_query_empty` | POST | `/query` | 400 Bad Request |
| `test_query_too_long` | POST | `/query` | 400 with length error |
| `test_query_no_docs` | POST | `/query` | 422 no processed documents |

### 4.3 Analytics API Tests

| Test Case | Method | Endpoint | Validates |
|---|---|---|---|
| `test_get_analytics` | GET | `/analytics/{id}` | 200 + metrics + ratios + score + risks |
| `test_analytics_unprocessed` | GET | `/analytics/{id}` | 422 not processed |
| `test_compare_documents` | POST | `/compare` | 200 + comparison data |
| `test_compare_same_doc` | POST | `/compare` | 400 same document |

### 4.4 Health API Tests

| Test Case | Method | Endpoint | Validates |
|---|---|---|---|
| `test_health_check` | GET | `/health` | 200 + component status |
| `test_health_no_auth` | GET | `/health` | 200 (no auth required) |

---

## 5. RAG Evaluation

Dedicated evaluation framework for measuring RAG pipeline quality.

### 5.1 Evaluation Metrics

| Metric | Definition | Target | Measurement Method |
|---|---|---|---|
| **Retrieval Precision** | % of retrieved chunks relevant to the query | ≥ 80% | Manual annotation of top-K chunks |
| **Retrieval Recall** | % of relevant chunks that were retrieved | ≥ 75% | Compare retrieved vs. all relevant chunks |
| **Answer Relevance** | Semantic similarity of answer to the question | ≥ 0.8 | Embedding cosine similarity |
| **Citation Accuracy** | % of citations pointing to correct sources | ≥ 90% | Manual verification against source |
| **Faithfulness** | % of answer claims supported by retrieved context | ≥ 95% | LLM-as-judge or manual check |
| **Hallucination Rate** | % of claims NOT supported by context | ≤ 5% | 1 − Faithfulness |

### 5.2 Evaluation Dataset

See [AI_EVALUATION.md](AI_EVALUATION.md) for the complete evaluation dataset and methodology.

---

## 6. UI Testing

Manual testing checklist for the Streamlit frontend.

### Upload Flow

| # | Test | Expected Result |
|---|---|---|
| 1 | Upload valid PDF | File accepted, processing starts, status updates |
| 2 | Upload non-PDF file | Error message: "Only PDF files are accepted" |
| 3 | Upload file > 50 MB | Error message: "File size exceeds limit" |
| 4 | View document list | All uploaded documents shown with correct status |
| 5 | Delete document | Confirmation dialog → document removed from list |

### Dashboard

| # | Test | Expected Result |
|---|---|---|
| 1 | Select processed document | Dashboard loads with KPIs, health score, risks |
| 2 | Health score displayed | Score between 0–100 with dimension breakdown |
| 3 | KPI cards show values | Metrics displayed with units and YoY changes |
| 4 | Charts render | Plotly charts are interactive (hover, zoom) |
| 5 | No document selected | "Select a document" prompt shown |

### AI Analyst

| # | Test | Expected Result |
|---|---|---|
| 1 | Ask a factual question | Relevant answer with citations |
| 2 | Click suggested question | Question fills input field |
| 3 | Ask about missing info | "Information not found" response |
| 4 | Long response | Answer fully displayed with scrolling |

### Comparison

| # | Test | Expected Result |
|---|---|---|
| 1 | Select two documents and compare | Metric comparison table rendered |
| 2 | Select same document twice | Error: "Select two different documents" |
| 3 | Risk changes displayed | New, removed, changed risks shown |

### Error States

| # | Test | Expected Result |
|---|---|---|
| 1 | Backend offline | Graceful error message |
| 2 | LLM API unavailable | "AI service unavailable" message |
| 3 | Database error | "System error" message |

---

## 7. Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    api: API endpoint tests
    evaluation: RAG evaluation tests
    slow: Tests that take > 10 seconds
```

### Test Fixtures (conftest.py)

```python
@pytest.fixture
def db_session():
    """Provide a clean database session for each test."""

@pytest.fixture
def test_client():
    """FastAPI TestClient for API tests."""

@pytest.fixture
def sample_pdf():
    """Load a sample PDF for testing."""

@pytest.fixture
def sample_chunks():
    """Pre-created document chunks for RAG tests."""

@pytest.fixture
def sample_metrics():
    """Pre-created financial metrics for analytics tests."""
```

### CI Integration

Tests are executed automatically via GitHub Actions on every push and pull request:

```yaml
# .github/workflows/ci.yml (test step)
- name: Run Tests
  run: |
    pytest --cov=app --cov-report=xml -v
```
