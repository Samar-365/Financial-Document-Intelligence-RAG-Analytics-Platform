# Project Structure

## Financial Document Intelligence & RAG Analytics Platform

---

## Directory Layout

```
financial-document-intelligence/
│
├── app/                              # Backend application (FastAPI)
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   │
│   ├── api/                          # API route handlers
│   │   ├── __init__.py
│   │   ├── documents.py              # Document upload, list, delete endpoints
│   │   ├── query.py                  # RAG query endpoint
│   │   ├── analytics.py              # Financial analytics endpoints
│   │   ├── compare.py                # Document comparison endpoint
│   │   └── health.py                 # System health check endpoint
│   │
│   ├── core/                         # Application configuration & infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                 # Settings management (Pydantic BaseSettings)
│   │   ├── database.py               # SQLAlchemy engine, session factory
│   │   ├── security.py               # Authentication, file validation
│   │   └── logging.py                # Logging configuration
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                   # User model
│   │   ├── document.py               # Document model
│   │   ├── chunk.py                  # DocumentChunk model
│   │   ├── financial_metric.py       # FinancialMetric model
│   │   └── analysis_result.py        # AnalysisResult model
│   │
│   ├── schemas/                      # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── document.py               # Document create/read/list schemas
│   │   ├── query.py                  # Query request/response schemas
│   │   ├── analytics.py              # Analytics response schemas
│   │   └── compare.py                # Comparison request/response schemas
│   │
│   ├── services/                     # Business logic orchestration
│   │   ├── __init__.py
│   │   ├── document_service.py       # Document CRUD + processing orchestration
│   │   ├── query_service.py          # RAG query orchestration
│   │   ├── analytics_service.py      # Financial analytics orchestration
│   │   └── comparison_service.py     # Document comparison logic
│   │
│   ├── document_processing/          # Document ingestion pipeline
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py          # PDF text & table extraction (PyMuPDF, pdfplumber)
│   │   ├── text_cleaner.py           # Text normalization & cleaning
│   │   ├── section_detector.py       # Financial document section detection
│   │   ├── chunking.py               # Text chunking with overlap
│   │   └── metadata_extractor.py     # Company, year, section metadata
│   │
│   ├── rag/                          # RAG pipeline components
│   │   ├── __init__.py
│   │   ├── embeddings.py             # Sentence Transformers embedding service
│   │   ├── vector_store.py           # FAISS / pgvector abstraction
│   │   ├── retriever.py              # Semantic retrieval with filtering
│   │   ├── prompt_builder.py         # System & context prompt construction
│   │   ├── generator.py              # LLM response generation (OpenAI)
│   │   └── citation.py              # Citation extraction & formatting
│   │
│   ├── analytics/                    # Financial analytics engine
│   │   ├── __init__.py
│   │   ├── metric_extractor.py       # Financial metric identification & extraction
│   │   ├── ratio_calculator.py       # Financial ratio computation
│   │   ├── health_score.py           # 0-100 health score engine
│   │   ├── risk_analyzer.py          # Risk identification & classification
│   │   └── comparator.py             # Year-over-year metric comparison
│   │
│   └── utils/                        # Shared utilities
│       ├── __init__.py
│       ├── logger.py                 # Application logger
│       ├── validators.py             # Input validation helpers
│       ├── file_utils.py             # File handling utilities
│       └── text_utils.py             # Text processing helpers
│
├── frontend/                         # Streamlit frontend application
│   ├── app.py                        # Main Streamlit entry point
│   ├── pages/                        # Streamlit multi-page app
│   │   ├── 1_📊_Dashboard.py         # Main dashboard view
│   │   ├── 2_📄_Upload.py            # Document upload page
│   │   ├── 3_📈_Analysis.py          # Financial analysis page
│   │   ├── 4_🤖_AI_Analyst.py        # Chat / Q&A interface
│   │   └── 5_🔄_Comparison.py        # Document comparison page
│   ├── components/                   # Reusable Streamlit components
│   │   ├── __init__.py
│   │   ├── kpi_card.py               # KPI display card
│   │   ├── health_gauge.py           # Health score gauge chart
│   │   ├── chart_builder.py          # Plotly chart factory
│   │   ├── risk_display.py           # Risk summary component
│   │   └── chat_interface.py         # Chat message display
│   └── utils/                        # Frontend utilities
│       ├── __init__.py
│       ├── api_client.py             # HTTP client for FastAPI backend
│       └── formatters.py             # Display formatting helpers
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Shared fixtures and configuration
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_pdf_extractor.py
│   │   ├── test_chunking.py
│   │   ├── test_text_cleaner.py
│   │   ├── test_metric_extractor.py
│   │   ├── test_ratio_calculator.py
│   │   ├── test_health_score.py
│   │   ├── test_risk_analyzer.py
│   │   └── test_validators.py
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_document_pipeline.py
│   │   ├── test_rag_pipeline.py
│   │   └── test_analytics_pipeline.py
│   ├── api/                          # API endpoint tests
│   │   ├── __init__.py
│   │   ├── test_documents_api.py
│   │   ├── test_query_api.py
│   │   ├── test_analytics_api.py
│   │   └── test_health_api.py
│   └── evaluation/                   # RAG evaluation suite
│       ├── __init__.py
│       ├── eval_dataset.json
│       ├── test_retrieval_quality.py
│       ├── test_answer_quality.py
│       └── test_citation_accuracy.py
│
├── data/                             # Data storage (gitignored)
│   ├── uploads/                      # Uploaded PDF files
│   ├── faiss_index/                  # FAISS vector index files
│   └── evaluation/                   # Evaluation datasets and results
│
├── docs/                             # Project documentation
│   ├── INDEX.md                      # Documentation navigation
│   ├── SRS.md                        # Software Requirements Specification
│   ├── SYSTEM_DESIGN.md              # Architecture & design
│   ├── DATABASE.md                   # Database schema
│   ├── API.md                        # REST API documentation
│   ├── UI_SPECIFICATION.md           # Frontend specification
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── TESTING.md                    # Testing strategy
│   ├── AI_EVALUATION.md              # RAG evaluation framework
│   ├── SECURITY.md                   # Security documentation
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── DEVOPS.md                     # CI/CD and DevOps
│   ├── MONITORING.md                 # Logging & monitoring
│   ├── ERROR_HANDLING.md             # Error handling patterns
│   ├── MODULE_DESIGN.md              # Module/class design
│   ├── SEQUENCE_DIAGRAMS.md          # Interaction diagrams
│   ├── USE_CASES.md                  # Use case documentation
│   ├── DECISIONS.md                  # Architecture decision records
│   ├── CODE_QUALITY.md               # Quality standards
│   ├── DATA_DICTIONARY.md            # Data field documentation
│   ├── GLOSSARY.md                   # Technical glossary
│   ├── LIMITATIONS.md                # Known limitations
│   ├── FUTURE_ENHANCEMENTS.md        # Planned improvements
│   ├── ROADMAP.md                    # Development roadmap
│   ├── INTERVIEW_PREPARATION.md      # Interview Q&A
│   ├── RESUME.md                     # Resume positioning
│   ├── PRESENTATION_OUTLINE.md       # Presentation slides
│   ├── PROJECT_REPORT.md             # Academic report
│   └── DOCUMENTATION_STATUS.md       # Documentation tracking
│
├── scripts/                          # Utility and setup scripts
│   ├── setup_db.py                   # Database initialization
│   ├── seed_data.py                  # Sample data seeding
│   ├── run_evaluation.py             # RAG evaluation runner
│   └── export_metrics.py             # Metrics export utility
│
├── alembic/                          # Database migration files
│   ├── env.py
│   ├── versions/                     # Migration version scripts
│   └── alembic.ini                   # Alembic configuration
│
├── .github/                          # GitHub configuration
│   └── workflows/
│       ├── ci.yml                    # CI pipeline (lint, test, build)
│       └── cd.yml                    # CD pipeline (deploy)
│
├── .env.example                      # Environment variable template
├── .gitignore                        # Git ignore rules
├── Dockerfile                        # Backend Docker image
├── docker-compose.yml                # Multi-service orchestration
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── pytest.ini                        # Pytest configuration
├── pyproject.toml                    # Project metadata and tool config
├── LICENSE                           # MIT License
└── README.md                         # Project README
```

---

## Directory Responsibilities

| Directory | Responsibility |
|---|---|
| `app/` | All backend application code — the FastAPI server, business logic, and processing engines |
| `app/api/` | HTTP route handlers. Each file maps to a group of related endpoints. No business logic — delegates to services |
| `app/core/` | Cross-cutting infrastructure: configuration, database connections, security, logging |
| `app/models/` | SQLAlchemy ORM model definitions. One file per database table |
| `app/schemas/` | Pydantic models for request validation and response serialization |
| `app/services/` | Business logic orchestration. Services coordinate between processing modules and the data layer |
| `app/document_processing/` | The document ingestion pipeline: PDF extraction, cleaning, section detection, chunking |
| `app/rag/` | The RAG pipeline: embeddings, vector search, retrieval, prompt construction, generation, citation |
| `app/analytics/` | Financial analytics: metric extraction, ratio calculation, health scoring, risk analysis |
| `app/utils/` | Shared utility functions used across multiple modules |
| `frontend/` | Streamlit dashboard application with multi-page navigation |
| `frontend/pages/` | Individual Streamlit pages (numbered for navigation order) |
| `frontend/components/` | Reusable UI components (KPI cards, charts, gauges) |
| `tests/` | Complete test suite organized by test type |
| `tests/unit/` | Unit tests for individual functions and classes |
| `tests/integration/` | End-to-end pipeline tests |
| `tests/api/` | REST API endpoint tests using FastAPI TestClient |
| `tests/evaluation/` | RAG quality evaluation tests and datasets |
| `data/` | Runtime data storage (gitignored) — uploads, FAISS index, evaluation data |
| `docs/` | All project documentation |
| `scripts/` | Utility scripts for setup, seeding, evaluation, and maintenance |
| `alembic/` | Database migration management |
| `.github/workflows/` | GitHub Actions CI/CD pipeline definitions |

---

## Key Files

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI application factory — creates the app, registers routes, configures middleware |
| `app/core/config.py` | Pydantic `BaseSettings` class loading configuration from `.env` |
| `app/core/database.py` | SQLAlchemy `create_engine`, `SessionLocal` factory, `get_db` dependency |
| `frontend/app.py` | Streamlit entry point with page configuration |
| `.env.example` | Template showing all required and optional environment variables |
| `docker-compose.yml` | Defines services: backend (FastAPI), frontend (Streamlit), database (PostgreSQL) |
| `Dockerfile` | Multi-stage build for the backend application |
| `requirements.txt` | Pinned production dependencies |
| `requirements-dev.txt` | Development tools: pytest, black, ruff, mypy |
