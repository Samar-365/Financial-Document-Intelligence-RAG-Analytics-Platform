# API Documentation

## Financial Document Intelligence & RAG Analytics Platform

| Field | Value |
|---|---|
| **Base URL** | `http://localhost:8000` |
| **API Documentation** | `http://localhost:8000/docs` (Swagger UI) |
| **Format** | JSON |
| **Authentication** | Bearer Token (planned) |

---

## Table of Contents

- [Authentication](#authentication)
- [Endpoints Overview](#endpoints-overview)
- [Document Endpoints](#document-endpoints)
- [Query Endpoints](#query-endpoints)
- [Analytics Endpoints](#analytics-endpoints)
- [System Endpoints](#system-endpoints)
- [Error Responses](#error-responses)

---

## Authentication

> **MVP Note**: Authentication is optional during development. Production deployments must enable bearer token authentication.

```
Authorization: Bearer <token>
```

Unauthenticated requests to protected endpoints will receive:

```json
{
  "detail": "Not authenticated"
}
```

**Status Code**: `401 Unauthorized`

---

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/documents/upload` | Upload a financial document | Yes |
| `GET` | `/documents` | List all documents | Yes |
| `GET` | `/documents/{id}` | Get document details | Yes |
| `DELETE` | `/documents/{id}` | Delete a document | Yes |
| `POST` | `/documents/{id}/process` | Trigger document processing | Yes |
| `POST` | `/query` | Ask a question (RAG) | Yes |
| `POST` | `/compare` | Compare two documents | Yes |
| `GET` | `/analytics/{document_id}` | Get financial analytics | Yes |
| `GET` | `/health` | System health check | No |

---

## Document Endpoints

### POST `/documents/upload`

Upload a financial document for processing.

**Content-Type**: `multipart/form-data`

**Request Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | PDF file to upload (max 50 MB) |
| `company` | string | No | Company name |
| `financial_year` | string | No | Financial year (e.g., "FY2025") |
| `document_type` | string | No | Type: annual_report, quarterly_report, earnings, presentation, statement |

**Example Request:**

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@ABC_Annual_Report_2025.pdf" \
  -F "company=ABC Ltd." \
  -F "financial_year=FY2025" \
  -F "document_type=annual_report"
```

**Success Response (201 Created):**

```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "ABC_Annual_Report_2025.pdf",
  "company": "ABC Ltd.",
  "financial_year": "FY2025",
  "document_type": "annual_report",
  "status": "UPLOADED",
  "file_size_bytes": 4523981,
  "upload_date": "2026-09-10T12:30:00Z",
  "message": "Document uploaded successfully. Use POST /documents/{id}/process to start processing."
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 400 | Invalid file type | `{"detail": "Only PDF files are accepted. Received: image/jpeg"}` |
| 400 | File too large | `{"detail": "File size exceeds maximum limit of 50 MB"}` |
| 409 | Duplicate file | `{"detail": "A document with the same content has already been uploaded", "existing_document_id": "..."}` |
| 422 | Corrupt PDF | `{"detail": "The uploaded file appears to be a corrupted PDF"}` |

---

### GET `/documents`

List all uploaded documents.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `status` | string | No | Filter by status: UPLOADED, PROCESSING, PROCESSED, FAILED |
| `company` | string | No | Filter by company name |
| `limit` | integer | No | Max results (default: 50) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/documents?status=PROCESSED&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "documents": [
    {
      "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "ABC_Annual_Report_2025.pdf",
      "company": "ABC Ltd.",
      "financial_year": "FY2025",
      "document_type": "annual_report",
      "status": "PROCESSED",
      "page_count": 245,
      "file_size_bytes": 4523981,
      "upload_date": "2026-09-10T12:30:00Z",
      "processed_date": "2026-09-10T12:32:15Z"
    },
    {
      "document_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "filename": "ABC_Annual_Report_2024.pdf",
      "company": "ABC Ltd.",
      "financial_year": "FY2024",
      "document_type": "annual_report",
      "status": "PROCESSED",
      "page_count": 210,
      "file_size_bytes": 3891247,
      "upload_date": "2026-09-10T12:25:00Z",
      "processed_date": "2026-09-10T12:27:30Z"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

---

### GET `/documents/{id}`

Get detailed information about a specific document.

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | Yes | Document ID |

**Example Request:**

```bash
curl -X GET http://localhost:8000/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "ABC_Annual_Report_2025.pdf",
  "company": "ABC Ltd.",
  "financial_year": "FY2025",
  "document_type": "annual_report",
  "status": "PROCESSED",
  "page_count": 245,
  "file_size_bytes": 4523981,
  "upload_date": "2026-09-10T12:30:00Z",
  "processed_date": "2026-09-10T12:32:15Z",
  "processing_stats": {
    "chunks_created": 487,
    "total_tokens": 198542,
    "metrics_extracted": 12,
    "sections_detected": 8,
    "processing_time_seconds": 135
  }
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 404 | Document not found | `{"detail": "Document not found"}` |

---

### DELETE `/documents/{id}`

Delete a document and all associated data (chunks, embeddings, metrics, analysis).

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | Yes | Document ID |

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "message": "Document deleted successfully",
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "deleted": {
    "chunks": 487,
    "metrics": 12,
    "analysis_results": 1,
    "vectors_removed": 487
  }
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 404 | Document not found | `{"detail": "Document not found"}` |

---

### POST `/documents/{id}/process`

Trigger processing of an uploaded document (extraction, chunking, embedding, metric extraction).

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | Yes | Document ID |

**Request Body (optional):**

```json
{
  "force_reprocess": false
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `force_reprocess` | boolean | No | If true, reprocess even if already processed (default: false) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/process \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"force_reprocess": false}'
```

**Success Response (202 Accepted):**

```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PROCESSING",
  "message": "Document processing started. Check status via GET /documents/{id}"
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 404 | Document not found | `{"detail": "Document not found"}` |
| 409 | Already processing | `{"detail": "Document is currently being processed"}` |
| 409 | Already processed | `{"detail": "Document has already been processed. Set force_reprocess=true to reprocess"}` |

---

## Query Endpoints

### POST `/query`

Ask a natural-language question about uploaded documents using the RAG pipeline.

**Request Body:**

```json
{
  "question": "What was ABC Ltd's revenue in FY2025?",
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "top_k": 5,
  "similarity_threshold": 0.3
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `question` | string | Yes | Natural-language question (max 500 chars) |
| `document_id` | UUID | No | Restrict search to a specific document |
| `top_k` | integer | No | Number of chunks to retrieve (default: 5, max: 20) |
| `similarity_threshold` | float | No | Minimum similarity score (default: 0.3) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was ABC Ltd'\''s revenue in FY2025?",
    "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

**Success Response (200 OK):**

```json
{
  "answer": "ABC Ltd reported total revenue of ₹11,450 crore for FY2025, representing a year-over-year increase of 12.25% compared to ₹10,200 crore in FY2024. The growth was primarily driven by increased demand in the domestic market and expansion of the product portfolio.",
  "confidence": "high",
  "sources": [
    {
      "document": "ABC_Annual_Report_2025.pdf",
      "page": 87,
      "section": "Consolidated Statement of Profit & Loss",
      "relevance_score": 0.92
    },
    {
      "document": "ABC_Annual_Report_2025.pdf",
      "page": 42,
      "section": "Management Discussion & Analysis",
      "relevance_score": 0.85
    }
  ],
  "metadata": {
    "chunks_retrieved": 5,
    "chunks_used": 3,
    "query_time_ms": 245,
    "generation_time_ms": 1820,
    "total_time_ms": 2065
  }
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 400 | Empty question | `{"detail": "Question cannot be empty"}` |
| 400 | Question too long | `{"detail": "Question exceeds maximum length of 500 characters"}` |
| 404 | Document not found | `{"detail": "Document not found"}` |
| 422 | No processed documents | `{"detail": "No processed documents available for querying"}` |
| 503 | LLM unavailable | `{"detail": "The AI service is temporarily unavailable. Please try again"}` |

---

### POST `/compare`

Compare two financial documents and analyze differences.

**Request Body:**

```json
{
  "document_id_1": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "document_id_2": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "metrics": ["revenue", "ebitda", "net_income", "total_debt", "cash"]
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `document_id_1` | UUID | Yes | First document (typically the earlier period) |
| `document_id_2` | UUID | Yes | Second document (typically the later period) |
| `metrics` | string[] | No | Specific metrics to compare (default: all available) |

**Success Response (200 OK):**

```json
{
  "comparison": {
    "document_1": {
      "document_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "filename": "ABC_Annual_Report_2024.pdf",
      "company": "ABC Ltd.",
      "period": "FY2024"
    },
    "document_2": {
      "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "ABC_Annual_Report_2025.pdf",
      "company": "ABC Ltd.",
      "period": "FY2025"
    },
    "metric_changes": [
      {
        "metric": "revenue",
        "value_1": 10200.0,
        "value_2": 11450.0,
        "unit": "INR Crore",
        "absolute_change": 1250.0,
        "percentage_change": 12.25,
        "trend": "increase"
      },
      {
        "metric": "ebitda",
        "value_1": 2100.0,
        "value_2": 2340.0,
        "unit": "INR Crore",
        "absolute_change": 240.0,
        "percentage_change": 11.43,
        "trend": "increase"
      },
      {
        "metric": "net_income",
        "value_1": 1200.0,
        "value_2": 1410.0,
        "unit": "INR Crore",
        "absolute_change": 210.0,
        "percentage_change": 17.5,
        "trend": "increase"
      },
      {
        "metric": "total_debt",
        "value_1": 4200.0,
        "value_2": 3900.0,
        "unit": "INR Crore",
        "absolute_change": -300.0,
        "percentage_change": -7.14,
        "trend": "decrease"
      },
      {
        "metric": "cash",
        "value_1": 1800.0,
        "value_2": 2150.0,
        "unit": "INR Crore",
        "absolute_change": 350.0,
        "percentage_change": 19.44,
        "trend": "increase"
      }
    ],
    "risk_changes": {
      "new_risks": [
        {
          "category": "Regulatory",
          "description": "New data privacy compliance requirements",
          "severity": "Medium"
        }
      ],
      "removed_risks": [],
      "changed_risks": [
        {
          "category": "Financial",
          "description": "Debt exposure",
          "severity_change": "High → Medium",
          "reason": "Debt reduced by 7.14%"
        }
      ]
    },
    "ai_summary": "ABC Ltd. demonstrated strong financial performance in FY2025 compared to FY2024. Revenue grew by 12.25%, with net income increasing even faster at 17.5%, indicating improving operational efficiency. The company reduced its debt by 7.14% while increasing cash reserves by 19.44%, strengthening its balance sheet. A new regulatory risk related to data privacy compliance has emerged.",
    "sources": [
      {"document": "ABC_Annual_Report_2024.pdf", "pages": [87, 103, 142]},
      {"document": "ABC_Annual_Report_2025.pdf", "pages": [87, 103, 148]}
    ]
  }
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 400 | Same document | `{"detail": "Cannot compare a document with itself"}` |
| 404 | Document not found | `{"detail": "Document {id} not found"}` |
| 422 | Not processed | `{"detail": "Both documents must be in PROCESSED status"}` |

---

## Analytics Endpoints

### GET `/analytics/{document_id}`

Get financial analytics for a processed document.

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `document_id` | UUID | Yes | Document ID |

**Example Request:**

```bash
curl -X GET http://localhost:8000/analytics/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "company": "ABC Ltd.",
  "financial_year": "FY2025",
  "metrics": {
    "revenue": {"value": 11450.0, "unit": "INR Crore", "confidence": 0.95, "source_page": 87},
    "gross_profit": {"value": 4580.0, "unit": "INR Crore", "confidence": 0.90, "source_page": 87},
    "ebitda": {"value": 2340.0, "unit": "INR Crore", "confidence": 0.92, "source_page": 87},
    "operating_income": {"value": 1890.0, "unit": "INR Crore", "confidence": 0.88, "source_page": 87},
    "net_income": {"value": 1410.0, "unit": "INR Crore", "confidence": 0.95, "source_page": 87},
    "eps": {"value": 28.2, "unit": "INR", "confidence": 0.93, "source_page": 88},
    "total_assets": {"value": 18500.0, "unit": "INR Crore", "confidence": 0.90, "source_page": 92},
    "total_liabilities": {"value": 9800.0, "unit": "INR Crore", "confidence": 0.88, "source_page": 92},
    "total_debt": {"value": 3900.0, "unit": "INR Crore", "confidence": 0.91, "source_page": 93},
    "cash": {"value": 2150.0, "unit": "INR Crore", "confidence": 0.94, "source_page": 92},
    "operating_cash_flow": {"value": 2680.0, "unit": "INR Crore", "confidence": 0.89, "source_page": 95},
    "free_cash_flow": {"value": 1850.0, "unit": "INR Crore", "confidence": 0.85, "source_page": 95}
  },
  "ratios": {
    "revenue_growth": {"value": 12.25, "unit": "%"},
    "profit_margin": {"value": 12.31, "unit": "%"},
    "ebitda_margin": {"value": 20.44, "unit": "%"},
    "current_ratio": {"value": 1.65, "unit": "x"},
    "debt_to_equity": {"value": 0.45, "unit": "x"},
    "return_on_assets": {"value": 7.62, "unit": "%"},
    "return_on_equity": {"value": 16.21, "unit": "%"},
    "ocf_ratio": {"value": 1.12, "unit": "x"}
  },
  "health_score": {
    "composite": 78.0,
    "dimensions": {
      "growth": {"score": 86.0, "weight": 0.20},
      "profitability": {"score": 82.0, "weight": 0.25},
      "liquidity": {"score": 71.0, "weight": 0.20},
      "leverage": {"score": 74.0, "weight": 0.20},
      "cash_flow": {"score": 77.0, "weight": 0.15}
    },
    "interpretation": "Moderate — generally healthy with some areas that could improve",
    "disclaimer": "This is an indicative analytical score, not a certified credit rating or investment recommendation."
  },
  "risks": [
    {
      "category": "Financial",
      "description": "Increasing interest expenses due to rising rates",
      "severity": "Medium",
      "evidence": "Interest expenses increased by 18% year-over-year to ₹420 Cr",
      "source_page": 103,
      "section": "Notes to Financial Statements",
      "confidence": 0.85
    },
    {
      "category": "Regulatory",
      "description": "New environmental compliance requirements",
      "severity": "Medium",
      "evidence": "The company is required to comply with new emissions standards by FY2027",
      "source_page": 156,
      "section": "Risk Factors",
      "confidence": 0.78
    },
    {
      "category": "Market",
      "description": "Increased competition in the domestic market",
      "severity": "Low",
      "evidence": "Market share remained stable despite entry of two new competitors",
      "source_page": 42,
      "section": "Management Discussion & Analysis",
      "confidence": 0.72
    }
  ]
}
```

**Error Responses:**

| Status Code | Condition | Response |
|---|---|---|
| 404 | Document not found | `{"detail": "Document not found"}` |
| 422 | Not processed | `{"detail": "Document has not been processed yet. Current status: UPLOADED"}` |

---

## System Endpoints

### GET `/health`

Check system health and component status. No authentication required.

**Example Request:**

```bash
curl -X GET http://localhost:8000/health
```

**Success Response (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-10T12:30:00Z",
  "components": {
    "database": {"status": "connected", "latency_ms": 5},
    "vector_store": {"status": "loaded", "vector_count": 15420},
    "embedding_model": {"status": "loaded", "model": "all-MiniLM-L6-v2"},
    "llm": {"status": "available", "provider": "openai", "model": "gpt-4o-mini"}
  },
  "stats": {
    "documents_total": 12,
    "documents_processed": 10,
    "total_chunks": 15420
  }
}
```

**Degraded Response (200 OK but with warnings):**

```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "2026-09-10T12:30:00Z",
  "components": {
    "database": {"status": "connected", "latency_ms": 5},
    "vector_store": {"status": "loaded", "vector_count": 15420},
    "embedding_model": {"status": "loaded", "model": "all-MiniLM-L6-v2"},
    "llm": {"status": "unavailable", "error": "OpenAI API key not configured"}
  }
}
```

---

## Error Responses

### Standard Error Format

All error responses follow a consistent format:

```json
{
  "detail": "Human-readable error description",
  "error_code": "DESCRIPTIVE_ERROR_CODE",
  "timestamp": "2026-09-10T12:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|---|---|---|
| 200 | OK | Successful retrieval or operation |
| 201 | Created | Resource successfully created (document upload) |
| 202 | Accepted | Async operation started (document processing) |
| 400 | Bad Request | Invalid input or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource or invalid state transition |
| 422 | Unprocessable Entity | Valid syntax but semantic error (corrupt file, wrong status) |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | External dependency unavailable (LLM, database) |
