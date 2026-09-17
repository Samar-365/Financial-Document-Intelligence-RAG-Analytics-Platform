# Database Schema & 3NF Relational Model Documentation

Developer 2 — Backend, Database & API Architect

---

## 1. Entity Relationship (ER) Model Overview

The database architecture consists of five core tables designed in Third Normal Form (3NF) to support transactional integrity, document metadata tracking, vector chunk storage, financial metrics, and calculated analytics results.

```
┌──────────────┐       1:N       ┌──────────────┐
│    users     │─────────────────│  documents   │
└──────────────┘                 └──────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │ 1:N                   │ 1:N                   │ 1:1
                 ▼                       ▼                       ▼
      ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
      │  document_chunks   │   │ financial_metrics  │   │  analysis_results  │
      └────────────────────┘   └────────────────────┘   └────────────────────┘
```

---

## 2. Table Specifications

### 2.1 `users`
- Primary Key: `id` (UUID)
- Fields: `email` (VARCHAR(255), UNIQUE), `full_name`, `is_active`, `created_at`, `updated_at`

### 2.2 `documents`
- Primary Key: `id` (UUID)
- Foreign Key: `user_id` -> `users.id` (ON DELETE CASCADE)
- Unique Constraint: `file_hash` (SHA-256 for deduplication)
- Fields: `filename`, `file_size_bytes`, `page_count`, `status` (`UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`), `fiscal_year`, `fiscal_period`, `company_name`, `error_message`, `created_at`, `updated_at`
- Indexes:
  - `ix_documents_user_created` (`user_id`, `created_at`)
  - `ix_documents_company_period` (`company_name`, `fiscal_year`, `fiscal_period`)

### 2.3 `document_chunks`
- Primary Key: `id` (UUID)
- Foreign Key: `document_id` -> `documents.id` (ON DELETE CASCADE)
- Fields: `chunk_index`, `content` (TEXT), `page_number`, `section`, `char_count`, `embedding` (`ARRAY(Float)` / `vector(384)`)
- Indexes:
  - `ix_chunks_document_index` (`document_id`, `chunk_index`)
  - `ix_chunks_document_page` (`document_id`, `page_number`)

### 2.4 `financial_metrics`
- Primary Key: `id` (UUID)
- Foreign Key: `document_id` -> `documents.id` (ON DELETE CASCADE)
- Fields: `metric_name`, `value` (FLOAT), `unit`, `fiscal_year`, `fiscal_period`, `source_page`, `confidence`
- Indexes:
  - `ix_metrics_document_name` (`document_id`, `metric_name`)
  - `ix_metrics_doc_year_period` (`document_id`, `fiscal_year`, `fiscal_period`)

### 2.5 `analysis_results`
- Primary Key: `id` (UUID)
- Foreign Key / Unique: `document_id` -> `documents.id` (ON DELETE CASCADE, 1:1)
- Fields: `overall_score`, `growth_score`, `profitability_score`, `liquidity_score`, `leverage_score`, `cash_flow_score`, `opm`, `npm`, `roe`, `roce`, `current_ratio`, `quick_ratio`, `debt_to_equity`, `interest_coverage`, `risk_flags` (JSON)

---

## 3. 3NF Rationale

1. **First Normal Form (1NF)**: All column values are atomic scalars (chunk embeddings are vector arrays stored per column).
2. **Second Normal Form (2NF)**: All non-key attributes fully depend on the primary key UUIDs.
3. **Third Normal Form (3NF)**: Transitive dependencies are removed. Extracted metrics are isolated from derived health scores and ratios.
