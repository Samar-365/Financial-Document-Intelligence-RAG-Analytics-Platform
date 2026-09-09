# Sequence Diagrams

## Financial Document Intelligence & RAG Analytics Platform

---

## 1. Document Upload

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant Val as Validator
    participant FS as File Storage
    participant DB as PostgreSQL

    User->>UI: Select PDF file
    User->>UI: Enter metadata (company, year)
    User->>UI: Click Upload
    UI->>API: POST /documents/upload (file + metadata)
    API->>Val: Validate file (type, size, magic bytes)
    
    alt Invalid File
        Val-->>API: Validation failed
        API-->>UI: 400/422 Error response
        UI-->>User: Display error message
    else Valid File
        Val-->>API: Validation passed
        API->>FS: Store PDF as {uuid}.pdf
        API->>DB: INSERT document record (status=UPLOADED)
        DB-->>API: document_id
        API-->>UI: 201 Created {document_id, status}
        UI-->>User: "Upload successful"
    end
```

---

## 2. Document Processing

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant DB as PostgreSQL
    participant PDF as PDFExtractor
    participant Clean as TextCleaner
    participant Chunk as ChunkingService
    participant Emb as EmbeddingService
    participant Vec as VectorStore
    participant Metric as MetricExtractor

    User->>UI: Click "Process"
    UI->>API: POST /documents/{id}/process
    API->>DB: UPDATE status = PROCESSING
    
    API->>PDF: extract_text(file_path)
    PDF-->>API: List[PageContent]
    
    API->>Clean: clean(raw_text)
    Clean-->>API: cleaned_text
    
    API->>Chunk: create_chunks(text, 512, 50)
    Chunk-->>API: List[Chunk] (487 chunks)
    
    API->>DB: INSERT document_chunks
    
    API->>Emb: embed_texts(chunk_texts)
    Emb-->>API: embeddings (487 × 384)
    
    API->>Vec: add(embeddings, chunk_ids)
    Vec-->>API: indexed
    
    API->>Metric: extract_metrics(chunks)
    Metric-->>API: List[Metric] (12 metrics)
    
    API->>DB: INSERT financial_metrics
    API->>DB: UPDATE status = PROCESSED
    
    API-->>UI: 200 "Processing complete"
    UI-->>User: Status: PROCESSED
```

---

## 3. RAG Question Answering

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant Emb as EmbeddingService
    participant Vec as VectorStore
    participant DB as PostgreSQL
    participant LLM as OpenAI GPT-4o-mini

    User->>UI: Type question
    User->>UI: Click Send
    UI->>API: POST /query {question, document_id}
    
    API->>Emb: embed_query(question)
    Emb-->>API: query_vector (384-dim)
    
    API->>Vec: search(query_vector, top_k=5)
    Vec-->>API: List[SearchResult] (chunk_ids + scores)
    
    API->>DB: Get chunk content + metadata
    DB-->>API: List[ChunkData]
    
    Note over API: Filter by similarity threshold ≥ 0.3
    Note over API: Construct context from top chunks
    Note over API: Build prompt: System + Context + Question
    
    API->>LLM: Generate(prompt)
    LLM-->>API: answer_text
    
    Note over API: Map answer claims → source chunks
    Note over API: Format citations
    
    API-->>UI: {answer, sources[], metadata}
    UI-->>User: Display answer + citations
```

---

## 4. Financial Analysis

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Ratio as RatioCalculator
    participant Health as HealthScoreEngine
    participant Risk as RiskAnalyzer
    participant LLM as OpenAI GPT-4o-mini

    User->>UI: Navigate to Analysis page
    User->>UI: Select document
    UI->>API: GET /analytics/{document_id}
    
    API->>DB: Get financial_metrics
    DB-->>API: List[Metric]
    
    API->>Ratio: calculate_ratios(metrics)
    Ratio-->>API: List[Ratio] (8 ratios)
    
    API->>Health: calculate_score(metrics, ratios)
    Health-->>API: HealthScore (78/100 + dimensions)
    
    API->>DB: Get document_chunks (risk sections)
    DB-->>API: risk_chunks
    
    API->>Risk: analyze_risks(chunks, metrics)
    Risk->>LLM: Extract risks from context
    LLM-->>Risk: identified_risks
    Risk-->>API: List[Risk]
    
    API->>DB: UPSERT analysis_results
    
    API-->>UI: {metrics, ratios, health_score, risks}
    UI-->>User: Render dashboard with charts
```

---

## 5. Document Comparison

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Comp as ReportComparator
    participant LLM as OpenAI GPT-4o-mini

    User->>UI: Select Document A (FY2024)
    User->>UI: Select Document B (FY2025)
    User->>UI: Click Compare
    UI->>API: POST /compare {doc_id_1, doc_id_2}
    
    API->>DB: Get metrics for doc_1
    DB-->>API: metrics_2024
    
    API->>DB: Get metrics for doc_2
    DB-->>API: metrics_2025
    
    API->>Comp: compare(metrics_2024, metrics_2025)
    Note over Comp: Calculate absolute changes
    Note over Comp: Calculate percentage changes
    Note over Comp: Determine trends
    Comp-->>API: metric_changes
    
    API->>DB: Get risks for both documents
    DB-->>API: risks_2024, risks_2025
    
    Note over API: Identify new, removed, changed risks
    
    API->>LLM: Generate comparison summary
    LLM-->>API: ai_summary
    
    API-->>UI: {metric_changes, risk_changes, ai_summary}
    UI-->>User: Render comparison table + summary
```

---

## 6. Dashboard Generation

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Plotly as Plotly Charts

    User->>UI: Open Dashboard page
    UI->>API: GET /documents (list)
    API->>DB: SELECT documents
    DB-->>API: document_list
    API-->>UI: document_list
    
    User->>UI: Select document from dropdown
    UI->>API: GET /analytics/{document_id}
    API->>DB: Get metrics + analysis_results
    DB-->>API: {metrics, ratios, health_score, risks, insights}
    API-->>UI: analytics_data
    
    Note over UI: Render components
    UI->>Plotly: Create KPI cards
    UI->>Plotly: Create health score gauge
    UI->>Plotly: Create trend charts
    UI->>UI: Render risk summary
    UI->>UI: Render AI insights
    
    UI-->>User: Complete dashboard
```
