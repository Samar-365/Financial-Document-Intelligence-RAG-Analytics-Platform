# Error Handling Documentation

## Financial Document Intelligence & RAG Analytics Platform

---

## Table of Contents

- [1. Error Handling Philosophy](#1-error-handling-philosophy)
- [2. Error Catalog](#2-error-catalog)
- [3. Error Response Format](#3-error-response-format)
- [4. Recovery Strategies](#4-recovery-strategies)

---

## 1. Error Handling Philosophy

| Principle | Implementation |
|---|---|
| **User-friendly messages** | Never expose stack traces, internal paths, or technical details to users |
| **Detailed internal logs** | Log full error context (stack trace, request params, state) for debugging |
| **Fail gracefully** | System continues operating even when individual components fail |
| **Specific error codes** | Each error type has a unique code for programmatic handling |
| **Actionable guidance** | Error messages suggest what the user can do to resolve the issue |

---

## 2. Error Catalog

### Document Upload Errors

| Error Code | HTTP Status | Condition | User-Facing Message | Internal Handling | Recovery Strategy |
|---|---|---|---|---|---|
| `DOC_001` | 400 | Non-PDF file uploaded | "Only PDF files are accepted. Please upload a valid PDF document." | Log filename and MIME type | User re-uploads correct file |
| `DOC_002` | 400 | File exceeds size limit | "File size exceeds the maximum limit of 50 MB. Please upload a smaller file." | Log file size | User uploads smaller file |
| `DOC_003` | 422 | Corrupt PDF | "The uploaded PDF appears to be corrupted and cannot be read. Please verify the file and try again." | Log corruption details from PyMuPDF | User re-uploads valid file |
| `DOC_004` | 422 | Empty/no-text PDF | "No readable text was found in this document. It may be a scanned image without a text layer." | Log page count, text length = 0 | User uploads text-based PDF |
| `DOC_005` | 422 | Password-protected PDF | "This PDF is password-protected. Please upload an unprotected version." | Log password detection | User uploads unprotected file |
| `DOC_006` | 409 | Duplicate document | "A document with identical content has already been uploaded." | Log file hash match, existing document_id | User reviews existing document |

### Document Processing Errors

| Error Code | HTTP Status | Condition | User-Facing Message | Internal Handling | Recovery Strategy |
|---|---|---|---|---|---|
| `PROC_001` | 500 | Text extraction failure | "Document processing encountered an error. Our team has been notified." | Log extraction error, page number, stack trace; set document status to FAILED | Automatic retry (1x); manual reprocess via API |
| `PROC_002` | 500 | Chunking failure | "Document processing encountered an error during text segmentation." | Log chunk failure details | Retry with fallback chunking strategy |
| `PROC_003` | 500 | Embedding generation failure | "Document processing encountered an error during indexing." | Log batch number, error; partial embeddings stored | Retry failed batch; skip individual chunks on repeated failure |
| `PROC_004` | 500 | Vector storage failure | "Document processing encountered an error during indexing." | Log FAISS error, index state | Rebuild FAISS index from stored chunks |
| `PROC_005` | 500 | Metric extraction failure | "Financial metrics could not be extracted from this document." | Log extraction attempt details | Document is still usable for Q&A; analytics may be incomplete |

### RAG Query Errors

| Error Code | HTTP Status | Condition | User-Facing Message | Internal Handling | Recovery Strategy |
|---|---|---|---|---|---|
| `RAG_001` | 400 | Empty query | "Please enter a question." | Validate before processing | User enters a question |
| `RAG_002` | 400 | Query too long | "Your question exceeds the maximum length of 500 characters." | Log query length | User shortens query |
| `RAG_003` | 422 | No processed documents | "No documents are available for querying. Please upload and process a document first." | Check document count | User uploads documents |
| `RAG_004` | 200 | No relevant chunks found | "The requested information could not be reliably identified in the uploaded documents." | Log query, similarity scores (all below threshold) | Suggest rephrasing; lower threshold if appropriate |
| `RAG_005` | 503 | LLM API failure | "The AI service is temporarily unavailable. Please try again in a moment." | Log API error (timeout, rate limit, auth); alert if persistent | Automatic retry (2x with exponential backoff); return cached response if available |
| `RAG_006` | 503 | LLM timeout | "The AI service took too long to respond. Please try again." | Log timeout duration | Retry with shorter context; reduce top_k |
| `RAG_007` | 500 | Embedding failure (query) | "An error occurred while processing your question. Please try again." | Log embedding error | Retry; if model not loaded, reload model |

### Analytics Errors

| Error Code | HTTP Status | Condition | User-Facing Message | Internal Handling | Recovery Strategy |
|---|---|---|---|---|---|
| `ANA_001` | 422 | Document not processed | "This document has not been processed yet. Please process it first." | Check document status | User triggers processing |
| `ANA_002` | 200 | Missing financial metrics | "Some financial metrics could not be extracted from this document. Available metrics are shown below." | Log which metrics are missing | Display available metrics; note missing ones |
| `ANA_003` | 200 | Ratio calculation failure | "Some financial ratios could not be calculated due to missing data." | Log which ratios failed and why (missing inputs, division by zero) | Display calculable ratios; explain missing ones |
| `ANA_004` | 200 | Health score partial | "The financial health score is based on partial data. Some dimensions could not be evaluated." | Log missing dimensions, weight redistribution | Display score with disclaimer about completeness |

### Database Errors

| Error Code | HTTP Status | Condition | User-Facing Message | Internal Handling | Recovery Strategy |
|---|---|---|---|---|---|
| `DB_001` | 500 | Connection failure | "A system error occurred. Please try again later." | Log connection error, retry count | Retry with exponential backoff; alert if persistent |
| `DB_002` | 500 | Query timeout | "The request took too long. Please try again." | Log query, execution time | Optimize query; increase timeout if appropriate |
| `DB_003` | 500 | Transaction failure | "A system error occurred. Your data was not affected." | Log transaction details, rollback | Automatic rollback ensures consistency |

---

## 3. Error Response Format

### API Error Response

```json
{
  "detail": "Human-readable error description",
  "error_code": "DOC_001",
  "timestamp": "2026-09-10T12:30:00Z"
}
```

### Implementation

```python
from fastapi import HTTPException
from datetime import datetime, timezone

class AppError(HTTPException):
    def __init__(self, status_code: int, error_code: str, detail: str):
        super().__init__(
            status_code=status_code,
            detail={
                "detail": detail,
                "error_code": error_code,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

# Usage
raise AppError(
    status_code=400,
    error_code="DOC_001",
    detail="Only PDF files are accepted. Please upload a valid PDF document."
)
```

---

## 4. Recovery Strategies

### Retry Policy

| Component | Max Retries | Backoff | Timeout |
|---|---|---|---|
| LLM API calls | 2 | Exponential (1s, 3s) | 30s per call |
| Database connections | 3 | Exponential (0.5s, 1s, 2s) | 10s per attempt |
| Embedding generation | 1 | — | 60s per batch |
| FAISS index write | 1 | — | 30s |

### Graceful Degradation

| Failure | System Behavior |
|---|---|
| LLM unavailable | Q&A returns "AI service unavailable"; dashboard and search still work |
| FAISS index corrupt | Rebuild from stored chunks in PostgreSQL |
| Metric extraction fails | Document still usable for Q&A; analytics show "data unavailable" |
| Single page extraction fails | Skip page, continue processing; log warning |
| Database slow | Return cached data if available; increase timeout |
