# Standardized Error Catalog & Exception Handling Reference

Developer 2 — Backend, Database & API Architect

---

## 1. Overview & Error Response Envelope

All API exceptions return a structured JSON payload:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description of error",
    "path": "/api/v1/endpoint/path",
    "details": null
  },
  "meta": null
}
```

---

## 2. Standardized Error Taxonomy

| Prefix | Domain | HTTP Code | Error Code | Description |
|:---|:---|:---:|:---|:---|
| `DOC_` | Document Management | 400 | `DOC_001` | Invalid PDF format or file signature |
| `DOC_` | Document Management | 409 | `DOC_002` | Duplicate document detected via SHA-256 hash |
| `DOC_` | Document Management | 404 | `DOC_003` | Target document ID not found |
| `PROC_` | Extraction & Processing | 422 | `PROC_001` | Document processing / parsing failure |
| `RAG_` | RAG & Vector Retrieval | 422 | `RAG_001` | Retrieval or contextual generation error |
| `ANA_` | Financial Analytics | 422 | `ANA_001` | Ratio calculation or health scoring failure |
| `DB_` | Database Infrastructure | 503 | `DB_001` | Connection pool exhaustion or connection error |
| `DB_` | Database Infrastructure | 409 | `DB_002` | Database unique/foreign-key integrity violation |
| `VALIDATION_` | Schema Boundary | 422 | `VALIDATION_001` | Request payload validation failure |
