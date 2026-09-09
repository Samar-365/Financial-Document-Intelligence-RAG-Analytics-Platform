# Logging & Monitoring Documentation

## Financial Document Intelligence & RAG Analytics Platform

---

## Table of Contents

- [1. Logging Strategy](#1-logging-strategy)
- [2. Monitored Areas](#2-monitored-areas)
- [3. Metrics Definition](#3-metrics-definition)
- [4. Alerting](#4-alerting)
- [5. Log Configuration](#5-log-configuration)

---

## 1. Logging Strategy

### Log Levels

| Level | Usage | Example |
|---|---|---|
| **DEBUG** | Detailed diagnostic information (development only) | `Chunk 47: 512 tokens, page 23, section: Income Statement` |
| **INFO** | Normal operational events | `Document abc123 processed successfully in 45.2s` |
| **WARNING** | Unexpected but non-critical events | `Page 15 extraction returned empty text` |
| **ERROR** | Failures requiring attention | `LLM API call failed: timeout after 30s` |
| **CRITICAL** | System-level failures | `Database connection pool exhausted` |

### Log Format

```
{timestamp} | {level} | {module} | {function} | {message} | {extra}
```

**Example:**

```
2026-09-10T12:30:15Z | INFO | document_processing.pdf_extractor | extract_text | Document processing complete | {"document_id": "abc123", "pages": 245, "chunks": 487, "duration_ms": 45200}
```

### Structured Logging Implementation

```python
import logging
import json
from datetime import datetime, timezone

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra
        return json.dumps(log_entry)
```

---

## 2. Monitored Areas

### 2.1 API Latency

| Metric | Description | Threshold |
|---|---|---|
| `api.response_time_ms` | End-to-end API response time | Warn: > 2000ms, Alert: > 5000ms |
| `api.request_count` | Total requests per minute | Info only |
| `api.error_rate` | Percentage of 4xx/5xx responses | Warn: > 5%, Alert: > 10% |

**What to log:**
```
POST /query | 200 | 2150ms | user_id=abc
POST /documents/upload | 201 | 340ms | file_size=4.5MB
```

### 2.2 Document Processing Time

| Metric | Description | Threshold |
|---|---|---|
| `processing.duration_seconds` | Total document processing time | Warn: > 120s, Alert: > 300s |
| `processing.pages_per_second` | Extraction throughput | Info only |
| `processing.chunks_created` | Chunks generated per document | Info only |
| `processing.failure_rate` | Processing failure percentage | Alert: > 10% |

**What to log:**
```
Document abc123 | Pages: 245 | Chunks: 487 | Metrics: 12 | Duration: 45.2s | Status: PROCESSED
```

### 2.3 RAG Latency

| Metric | Description | Threshold |
|---|---|---|
| `rag.embedding_time_ms` | Query embedding generation time | Warn: > 100ms |
| `rag.search_time_ms` | Vector search execution time | Warn: > 200ms |
| `rag.generation_time_ms` | LLM generation time | Warn: > 5000ms |
| `rag.total_time_ms` | End-to-end RAG pipeline time | Warn: > 6000ms |
| `rag.chunks_retrieved` | Number of chunks returned by search | Info only |
| `rag.chunks_above_threshold` | Chunks above similarity threshold | Info only |

**What to log:**
```
Query: "What was revenue?" | Embed: 25ms | Search: 45ms | LLM: 1820ms | Total: 2065ms | Chunks: 5/5 above threshold
```

### 2.4 Retrieval Results

| Metric | Description | Purpose |
|---|---|---|
| `retrieval.avg_similarity_score` | Mean similarity of top-K results | Track retrieval quality over time |
| `retrieval.min_similarity_score` | Lowest score in top-K | Detect queries with poor matches |
| `retrieval.zero_results_rate` | Percentage of queries with no results | Identify coverage gaps |

### 2.5 LLM Failures

| Metric | Description | Threshold |
|---|---|---|
| `llm.failure_count` | Failed LLM API calls | Alert: > 3 in 5 minutes |
| `llm.timeout_count` | Timed-out LLM calls | Alert: > 2 in 5 minutes |
| `llm.token_usage` | Tokens used per request | Info (cost tracking) |
| `llm.rate_limit_hits` | Rate limit responses from OpenAI | Alert: any occurrence |

### 2.6 Embedding Failures

| Metric | Description | Threshold |
|---|---|---|
| `embedding.failure_count` | Failed embedding generations | Alert: > 0 |
| `embedding.model_load_time_ms` | Model loading time at startup | Info only |
| `embedding.batch_duration_ms` | Batch embedding time | Warn: > 10000ms |

### 2.7 Database Errors

| Metric | Description | Threshold |
|---|---|---|
| `db.connection_pool_usage` | Active connections / pool size | Warn: > 80% |
| `db.query_duration_ms` | Query execution time | Warn: > 1000ms |
| `db.error_count` | Database errors per minute | Alert: > 0 |
| `db.transaction_rollbacks` | Transaction rollback count | Warn: > 0 |

### 2.8 Upload Failures

| Metric | Description | Threshold |
|---|---|---|
| `upload.failure_count` | Failed uploads per hour | Warn: > 5 |
| `upload.validation_failures` | File validation rejections | Info (expected) |
| `upload.avg_file_size_mb` | Average uploaded file size | Info only |
| `upload.disk_usage_gb` | Total upload storage used | Warn: > 80% capacity |

---

## 3. Metrics Definition

### Key Performance Indicators (KPIs)

| KPI | Formula | Target | Frequency |
|---|---|---|---|
| **System Availability** | Uptime / Total Time × 100 | ≥ 99% | Daily |
| **API Success Rate** | (2xx Responses) / Total Requests × 100 | ≥ 95% | Hourly |
| **Avg Query Latency** | Mean(rag.total_time_ms) | < 5000ms | Hourly |
| **Processing Success Rate** | Processed / Total Processed × 100 | ≥ 90% | Daily |
| **LLM Availability** | Successful LLM Calls / Total LLM Calls × 100 | ≥ 99% | Hourly |

---

## 4. Alerting

### Alert Rules (Production)

| Alert | Condition | Severity | Notification |
|---|---|---|---|
| API down | Health check fails 3 consecutive times | Critical | Immediate |
| Database unreachable | Connection fails for > 30 seconds | Critical | Immediate |
| LLM unavailable | > 3 failures in 5 minutes | High | Within 5 minutes |
| High error rate | API error rate > 10% for 5 minutes | High | Within 5 minutes |
| Slow queries | Avg latency > 10s for 10 minutes | Medium | Within 15 minutes |
| Disk space low | Upload directory > 80% capacity | Medium | Within 1 hour |
| Processing stuck | Document in PROCESSING > 10 minutes | Medium | Within 15 minutes |

---

## 5. Log Configuration

### Application Logger Setup

```python
# app/core/logging.py
import logging
import sys

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    logger = logging.getLogger("fdi")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    
    # File handler (production)
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    return logger
```

### FastAPI Middleware for Request Logging

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
    )
    return response
```

### Log Rotation

| Setting | Value |
|---|---|
| Max file size | 100 MB |
| Backup count | 5 files |
| Rotation | Size-based |
| Retention | 30 days |

### Security — What NOT to Log

| Data Type | Reason |
|---|---|
| API keys | Credential exposure |
| Database passwords | Credential exposure |
| Full document content | Data privacy |
| User passwords | Credential exposure |
| Full query responses | Data volume + privacy |
