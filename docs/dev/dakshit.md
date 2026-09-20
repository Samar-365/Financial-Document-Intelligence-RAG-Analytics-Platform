# Micro-Module Technical Roadmap & Implementation Guide — Developer 2
## Backend, Database & API Architect

---

## Module Overview & Dependency Map

Developer 2 owns seven interconnected micro-modules that form the persistence and API layer of the platform. Each module is designed to be developed with stub interfaces from Day 1, enabling parallel execution without blocking Developer 1, 3, or 4.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEVELOPER 2: MICRO-MODULE ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  D2-M1       │───▶│  D2-M2       │───▶│  D2-M3       │                   │
│  │  DB Engine   │    │  SQLAlchemy  │    │  Alembic     │                   │
│  │  & Pooling   │    │  3NF Models  │    │  Migrations  │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  D2-M4       │    │  D2-M5       │    │  D2-M6       │                   │
│  │  Pydantic    │    │  9 FastAPI   │    │  Error       │                   │
│  │  Schemas     │    │  Endpoints   │    │  Catalog     │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             ▼                                                │
│                    ┌──────────────┐                                          │
│                    │  D2-M7       │                                          │
│                    │  Pytest      │                                          │
│                    │  Test Suite  │                                          │
│                    └──────────────┘                                          │
│                                                                              │
│  Integration Points:                                                         │
│  ◀── Dev 1: Service DTOs (FinancialExtractor, RatioCalculator, RAGService)   │
│  ──▶ Dev 3: REST API JSON Contract (9 endpoints, Swagger /docs)              │
│  ◀── Dev 4: Docker Compose, .env contract, health probes                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## D2-M1: Database Engine & Connection Pooling

### Technical Objective
Establish a production-grade PostgreSQL connection layer using SQLAlchemy's `QueuePool` with tuned parameters for the FastAPI async request lifecycle.

### Implementation Specification

**Technology Stack**: `SQLAlchemy 2.0`, `psycopg2-binary`, `PostgreSQL 15`

**Module Location**: `app/db/session.py` + `app/core/config.py`

**Connection Pool Configuration**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Persistent connections maintained in pool
    max_overflow=10,        # Additional burst connections when pool exhausted
    pool_timeout=30,        # Seconds to wait before raising TimeoutError
    pool_recycle=1800,      # Recycle connections after 30 min (prevent stale)
    pool_pre_ping=True,     # Test connection liveness before checkout
    echo=False              # Disable SQL logging in production
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """FastAPI dependency yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

**Key Design Decisions**:
- **`pool_pre_ping=True`** is critical for PostgreSQL: it validates connections before use, preventing `OperationalError` from stale connections after network interruptions or server restarts.
- **`pool_size=20`** supports the expected concurrent load: with 4 developers testing simultaneously plus background Celery workers, 20 persistent connections is sufficient. SQLAlchemy defaults to `QueuePool` of size 5, which is too small for production API workloads.
- **`pool_recycle=1800`** addresses PostgreSQL's `idle_in_transaction_session_timeout` and prevents TCP connection drops from load balancers or firewalls.

**Testing Strategy (Sprint 1)**:
- Unit test: Verify `get_db()` yields a session, commits on success, and rolls back on exception.
- Integration test: Assert that 50 concurrent requests do not exhaust the pool (use `pytest-asyncio` with `asyncio.gather`).

---

## D2-M2: SQLAlchemy 3NF Relational Models

### Technical Objective
Define five normalized tables achieving Third Normal Form (3NF) — no transitive dependencies, all attributes depend on the primary key — using SQLAlchemy 2.0's declarative mapping.

### Schema Specification

**Entity Relationship (Logical)**:

| Table | Primary Key | Foreign Keys | 3NF Rationale |
|:---|:---|:---|:---|
| `users` | `id` (UUID) | — | Independent entity |
| `documents` | `id` (UUID) | `user_id → users.id` | Document metadata separate from content |
| `document_chunks` | `id` (UUID) | `document_id → documents.id` | Chunk text + embedding separated from document metadata |
| `financial_metrics` | `id` (UUID) | `document_id → documents.id` | Extracted metrics isolated per document |
| `analysis_results` | `id` (UUID) | `document_id → documents.id` | Ratios, health scores, risks derived from metrics |

**SQLAlchemy Model Patterns**:

```python
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    page_count = Column(Integer, nullable=True)
    status = Column(String(20), default="UPLOADED")  # UPLOADED, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships with cascade delete
    chunks = relationship("DocumentChunk", back_populates="document",
                          cascade="all, delete-orphan")
    metrics = relationship("FinancialMetric", back_populates="document",
                           cascade="all, delete-orphan")
    analysis = relationship("AnalysisResult", back_populates="document",
                            uselist=False, cascade="all, delete-orphan")

    # Composite index for multi-period queries
    __table_args__ = (
        Index("ix_documents_user_created", "user_id", "created_at"),
    )

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)  # Migrated to pgvector in Sprint 4

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_document_index", "document_id", "chunk_index"),
    )
```

**3NF Compliance Checklist**:
- **1NF**: All columns are atomic; no repeating groups or arrays of scalar values (embeddings stored as `ARRAY(Float)` — atomic per column).
- **2NF**: No partial dependencies — all non-key attributes depend on the full primary key (UUID `id`).
- **3NF**: No transitive dependencies — e.g., `document_chunks.content` depends only on `chunk_id`, not on `document_id` via `document.metadata`.

**Testing Strategy (Sprint 1)**:
- Write a `conftest.py` fixture creating an isolated test database (SQLite in-memory for unit tests, PostgreSQL for integration).
- Test cascade deletes: deleting a `Document` removes all associated chunks, metrics, and analysis results.
- Test unique constraints: duplicate `file_hash` raises `IntegrityError`.

---

## D2-M3: Alembic Database Migrations

### Technical Objective
Version-control all schema changes with Alembic, enabling reversible migrations across development, staging, and production environments.

### Implementation Specification

**Setup Commands (Sprint 1)**:

```bash
# Initialize Alembic in project root
alembic init alembic

# Configure alembic/env.py to import Base.metadata
# from app.models import Base
# target_metadata = Base.metadata

# Generate initial migration for all 5 tables
alembic revision --autogenerate -m "Initial schema: users, documents, chunks, metrics, analysis"

# Apply migration to database
alembic upgrade head
```

**`alembic/env.py` Configuration**:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base  # Import all models to register metadata
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

**Migration Naming Convention**:
- `{revision_hash}_{action}_{target}.py`
- Example: `a1b2c3d4_add_fiscal_year_to_metrics.py`

**Sprint-wise Migration Cadence**:
| Sprint | Migration Action |
|:---|:---|
| Sprint 1 | Initial schema (5 tables + indexes) |
| Sprint 2 | Add `status` enum check constraint on `documents` |
| Sprint 3 | Add composite index `(document_id, fiscal_year, fiscal_period)` on `financial_metrics` |
| Sprint 4 | Add `vector(384)` column to `document_chunks` for pgvector migration |

**Testing Strategy**:
- Test `alembic upgrade head` from an empty database succeeds.
- Test `alembic downgrade base` removes all tables (reversibility).
- CI pipeline runs `alembic upgrade head` against a PostgreSQL service container before pytest.

---

## D2-M4: Pydantic Request & Response Schemas

### Technical Objective
Define strict input validation and output serialization contracts for all 9 API endpoints using Pydantic v2, ensuring type safety and automatic OpenAPI documentation.

### Schema Architecture

**Naming Convention**:
- `{Entity}Create` — POST request body
- `{Entity}Update` — PATCH/PUT request body
- `{Entity}Response` — GET response body
- `{Entity}ListResponse` — Paginated list wrapper

**Core Schemas**:

```python
from pydantic import BaseModel, Field, UUID4, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

# ---- Request Schemas ----

class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: UUID4
    filename: str
    status: str = "UPLOADED"
    message: str

class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: UUID4
    question: str = Field(..., min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def sanitize_question(cls, v: str) -> str:
        # Strip prompt injection delimiters
        forbidden = ["<context>", "</context>", "IGNORE PREVIOUS", "SYSTEM:"]
        for pattern in forbidden:
            if pattern.lower() in v.lower():
                raise ValueError(f"Forbidden pattern detected: {pattern}")
        return v.strip()

# ---- Response Schemas ----

class Citation(BaseModel):
    document_id: UUID4
    page_number: int
    snippet: str = Field(..., max_length=500)
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    latency_ms: int
    model_used: str

class FinancialMetricResponse(BaseModel):
    metric_name: str
    value: float
    unit: str  # "INR_CR", "PERCENT", "RATIO"
    fiscal_year: int
    fiscal_period: str  # "Q1", "FY"
    source_page: int

class HealthScoreResponse(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    growth_score: float = Field(..., ge=0.0, le=100.0)
    profitability_score: float = Field(..., ge=0.0, le=100.0)
    liquidity_score: float = Field(..., ge=0.0, le=100.0)
    leverage_score: float = Field(..., ge=0.0, le=100.0)
    cash_flow_score: float = Field(..., ge=0.0, le=100.0)
    risk_flags: List[str] = []
```

**Pydantic v2 Best Practices Applied**:
- **`extra="forbid"`** : Rejects unknown fields, preventing silent data corruption.
- **`strict=True`** : Disables type coercion (e.g., string "123" will not be accepted for an int field).
- **`Field(ge=, le=)`** : Enforces numeric bounds at the schema level, reducing business logic validation.
- **`field_validator`** : Implements prompt injection filtering at the API boundary (owned by Dev 4, implemented by Dev 2).

**Testing Strategy**:
- Parametrized tests for every schema: valid payload, missing required field, extra field, out-of-bounds value, malicious injection pattern.
- Assert that `RequestValidationError` returns HTTP 422 with structured error details.

---

## D2-M5: 9 FastAPI REST Endpoints

### Technical Objective
Implement all nine REST operations with async route handlers, dependency injection for DB sessions, and integration with Developer 1's service DTOs.

### Endpoint Specification & Implementation Pattern

**Endpoint Inventory**:

| # | Method | Path | Handler Responsibility | Dev 1 Integration |
|:---|:---|:---|:---|:---|
| 1 | POST | `/documents/upload` | Accept file, store metadata, enqueue processing | Triggers Dev 1 `PDFService` |
| 2 | GET | `/documents` | Paginated list with filters | — |
| 3 | GET | `/documents/{id}` | Document detail + processing status | — |
| 4 | DELETE | `/documents/{id}` | Soft/hard delete with cascade | — |
| 5 | POST | `/query` | RAG query with citations | Calls Dev 1 `RAGService.query()` |
| 6 | GET | `/financial-metrics/{id}` | Extracted 12 metrics | Returns Dev 1 `ExtractedMetricsDTO` |
| 7 | GET | `/financial-ratios/{id}` | 8 calculated ratios | Calls Dev 1 `RatioCalculator` |
| 8 | GET | `/health-score/{id}` | 5D health score + risks | Calls Dev 1 `HealthScorer` |
| 9 | GET | `/health` | Deep health probe (DB + Redis) | — |

**Route Implementation Pattern**:

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from uuid import UUID

router = APIRouter(prefix="/api/v1", tags=["documents"])

@router.post("/documents/upload", response_model=DocumentUploadResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UUID4 = Depends(get_current_user_id)
):
    # Validate file magic bytes
    content = await file.read()
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail={"error_code": "DOC_001", "message": "Invalid PDF file signature"}
        )

    # Compute SHA-256 hash for deduplication
    file_hash = hashlib.sha256(content).hexdigest()

    # Check for duplicate
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"error_code": "DOC_002", "message": "Duplicate document detected"}
        )

    # Persist document metadata
    doc = Document(
        user_id=current_user,
        filename=file.filename,
        file_hash=file_hash,
        status="UPLOADED"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Enqueue background processing (Celery — Sprint 3+)
    # process_document.delay(str(doc.id), content)

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        message="Document uploaded and queued for processing"
    )
```

**Dependency Injection Architecture**:
- `get_db()` → SQLAlchemy session (per-request, committed on success)
- `get_current_user_id()` → extracts UUID from JWT header (stub in Sprint 1, real in Sprint 2)
- `get_rag_service()` → returns Dev 1's `RAGService` instance (stubbed in Sprint 1)

**Sprint-wise Endpoint Delivery**:
| Sprint | Endpoints Delivered |
|:---|:---|
| Sprint 1 | #1, #2, #3, #4, #9 (stub responses for #5–#8) |
| Sprint 2 | #5, #6, #7, #8 (wired to Dev 1 real services) |
| Sprint 3 | Add `/compare` multi-document endpoint (extends #2) |
| Sprint 4 | Performance tuning, pgvector-backed `/query` |

---

## D2-M6: Standardized Error Catalog & Centralized Exception Handling

### Technical Objective
Implement a unified error taxonomy with prefix-based error codes, enabling frontend (Dev 3) to display user-friendly messages and enabling observability (Dev 4) to route alerts by error domain.

### Error Taxonomy

| Prefix | Domain | Owner | HTTP Range | Example Codes |
|:---|:---|:---|:---|:---|
| `DOC_` | Document operations | Dev 2 | 400–409 | `DOC_001` Invalid PDF, `DOC_002` Duplicate, `DOC_003` Not Found |
| `PROC_` | Processing pipeline | Dev 1 + Dev 2 | 422–500 | `PROC_001` Extraction Failed, `PROC_002` Chunking Failed |
| `RAG_` | Retrieval & generation | Dev 1 | 422–504 | `RAG_001` No Context Found, `RAG_002` LLM Timeout |
| `ANA_` | Financial analysis | Dev 1 | 422–500 | `ANA_001` Missing Metrics, `ANA_002` Division by Zero |
| `DB_` | Database layer | Dev 2 | 500–503 | `DB_001` Connection Pool Exhausted, `DB_002` Integrity Violation |
| `AUTH_` | Authentication | Dev 4 | 401–403 | `AUTH_001` Invalid Token, `AUTH_002` Insufficient Permissions |

### Implementation Specification

```python
# app/core/errors.py
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

class AppException(Exception):
    """Base exception with error code, HTTP status, and message."""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DocumentNotFoundException(AppException):
    def __init__(self, document_id: str):
        super().__init__(
            code="DOC_003",
            message=f"Document {document_id} not found",
            status_code=404
        )

# app/main.py — Register global exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url.path)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_001",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "DB_002",
                "message": "Database integrity constraint violated",
                "detail": str(exc.orig)
            }
        }
    )

@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "DB_001",
                "message": "Database connection error — retry with backoff",
                "detail": str(exc.orig)
            }
        }
    )
```

**Design Rationale**:
- Custom exception classes inherit from `AppException`, not `HTTPException`, to keep domain logic decoupled from HTTP concerns.
- Global handlers catch `RequestValidationError`, `IntegrityError`, and `OperationalError` and translate them into the standardized error envelope.
- Frontend (Dev 3) can switch on `error.code` to render specific UI states (e.g., `DOC_003` → "Document not found" toast; `DB_001` → "Service temporarily unavailable, retrying...").

---

## D2-M7: Pytest API Test Suite

### Technical Objective
Achieve ≥ 85% backend test coverage with fast, deterministic integration tests using `TestClient` and database dependency overrides.

### Test Architecture

```
tests/
├── conftest.py              # Fixtures: test DB, client, auth mock
├── test_database.py         # D2-M1: Pooling, session lifecycle
├── test_models.py           # D2-M2: 3NF relationships, cascades
├── test_migrations.py       # D2-M3: Alembic upgrade/downgrade
├── test_schemas.py          # D2-M4: Pydantic validation
├── test_api_documents.py    # D2-M5: Upload, list, get, delete
├── test_api_query.py        # D2-M5: RAG query with citations
├── test_api_financials.py   # D2-M5: Metrics, ratios, health score
├── test_errors.py           # D2-M6: Error catalog mapping
└── test_integration.py      # End-to-end: upload → process → query
```

**Core Fixture Pattern**:

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.models import Base

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_financial"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Yield a session with transaction rollback per test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with overridden DB dependency."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Key Test Cases by Module**:

| Module | Test Case | Assertion |
|:---|:---|:---|
| D2-M1 | `test_pool_exhaustion` | 25 concurrent requests succeed; 26th raises `TimeoutError` after 30s |
| D2-M1 | `test_session_rollback` | Exception in route → no data persisted |
| D2-M2 | `test_cascade_delete` | DELETE document → chunks, metrics, analysis all deleted |
| D2-M2 | `test_unique_file_hash` | Duplicate upload → 409 `DOC_002` |
| D2-M3 | `test_migration_head` | `alembic upgrade head` exits 0 |
| D2-M4 | `test_extra_field_rejected` | POST with unknown field → 422 |
| D2-M4 | `test_injection_pattern_rejected` | Question containing `<context>` → 422 |
| D2-M5 | `test_upload_valid_pdf` | POST multipart → 201 with `document_id` |
| D2-M5 | `test_query_with_citations` | POST `/query` → response has `citations` array |
| D2-M6 | `test_not_found_error_code` | GET missing document → 404 with `DOC_003` |
| D2-M6 | `test_validation_error_format` | Malformed payload → 422 with `VALIDATION_001` |

**Coverage Enforcement**:
- `pytest --cov=app --cov-fail-under=85` in CI (Dev 4's GitHub Actions workflow).
- Exclude `alembic/` and `tests/` from coverage calculation.

---

## Integration Contracts & Parallel Development

### Contract 1: Developer 1 → Developer 2 (Python Service DTOs)

**Agreement**: Developer 1 publishes the following signatures by **Day 2 of Sprint 1**. Developer 2 writes stub implementations immediately, enabling route development without waiting for real logic.

```python
# app/services/stubs.py (Dev 2 writes these in Sprint 1)
from typing import List

def extract_metrics_stub(text: str) -> dict:
    """Stub returning dummy metrics — replaced by Dev 1 in Sprint 2."""
    return {
        "revenue": 0.0, "net_profit": 0.0, "total_assets": 0.0,
        "current_assets": 0.0, "current_liabilities": 0.0,
        "total_debt": 0.0, "equity": 0.0, "ebit": 0.0,
        "interest_expense": 0.0, "operating_cash_flow": 0.0,
        "inventory": 0.0, "capital_employed": 0.0
    }

def calculate_ratios_stub(metrics: dict) -> dict:
    return {"opm": 0.0, "npm": 0.0, "roe": 0.0, "roce": 0.0,
            "current_ratio": 0.0, "quick_ratio": 0.0,
            "debt_to_equity": 0.0, "interest_coverage": 0.0}

def health_score_stub(metrics: dict, ratios: dict) -> dict:
    return {"overall": 0.0, "growth": 0.0, "profitability": 0.0,
            "liquidity": 0.0, "leverage": 0.0, "cash_flow": 0.0}

def rag_query_stub(document_id: str, question: str) -> dict:
    return {"answer": "Stub answer", "citations": [], "latency_ms": 0}
```

**Integration Point (Sprint 2, Day 1)**: Developer 1 delivers real `FinancialExtractor`, `RatioCalculator`, `HealthScorer`, and `RAGService`. Developer 2 replaces stubs with direct imports:

```python
from app.services.financial_extractor import FinancialExtractor
from app.services.ratio_calculator import RatioCalculator
from app.services.health_scorer import HealthScorer
from app.services.rag_service import RAGService
```

### Contract 2: Developer 2 → Developer 3 (REST API JSON Contract)

**Agreement**: Developer 2 publishes Swagger UI at `/docs` by **Day 3 of Sprint 1**. Developer 3 points Streamlit `api_client.py` to `http://localhost:8000/api/v1`.

**Fixed Response Envelope**:

```json
{
  "data": { ... },
  "error": null,
  "meta": { "request_id": "uuid", "latency_ms": 42 }
}
```

**Error Response Envelope**:

```json
{
  "data": null,
  "error": { "code": "DOC_003", "message": "Document not found", "path": "/api/v1/documents/abc" },
  "meta": { "request_id": "uuid", "latency_ms": 3 }
}
```

### Contract 3: Developer 4 → Developer 2 (Infrastructure & Configuration)

**Agreement**: Developer 4 publishes `.env.example` by **Day 2 of Sprint 1** with the following variables:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/financial_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# API
API_PORT=8000
API_HOST=0.0.0.0
CORS_ORIGINS=http://localhost:8501

# Security
RATE_LIMIT_PER_MINUTE=100
JWT_SECRET=change-me-in-production

# Observability
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true

# Celery (Sprint 3+)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
```

Developer 2 must ensure `app/core/config.py` reads all variables with `pydantic-settings` and fails fast on missing required values.

---

## Sprint-wise Execution Guide for Developer 2

### Sprint 1: Foundation (Weeks 1–2)

| Day | Task | Deliverable | Verification |
|:---|:---|:---|:---|
| 1–2 | Set up `app/core/config.py` with `pydantic-settings` | Settings class reads `.env` | `python -c "from app.core.config import settings; print(settings.DATABASE_URL)"` |
| 3–4 | Implement `app/db/session.py` with `QueuePool` | Engine + `get_db()` dependency | Unit test: session commit/rollback |
| 5–6 | Define 5 SQLAlchemy models in `app/models/` | 3NF schema with relationships | `Base.metadata.tables` prints 5 tables |
| 7–8 | Initialize Alembic, generate initial migration | `alembic/versions/xxx_initial.py` | `alembic upgrade head` creates tables in PostgreSQL |
| 9–10 | Implement Pydantic schemas in `app/schemas/` | Request/response models for all 9 endpoints | Parametrized validation tests pass |
| 11–12 | Scaffold FastAPI app, CORS, router registration | `app/main.py` with `/docs` accessible | Swagger UI shows 9 endpoints |
| 13–14 | Implement document CRUD endpoints (#1–#4, #9) | Upload, list, get, delete, health | `TestClient` integration tests pass |

**Sprint 1 Exit Criteria**: `docker compose up` starts PostgreSQL + FastAPI; `/docs` renders; document upload stores metadata in DB; all Sprint 1 tests pass.

### Sprint 2: Intelligence Integration (Weeks 3–4)

| Day | Task | Deliverable | Verification |
|:---|:---|:---|:---|
| 1–2 | Replace stubs with Dev 1's real service imports | `financial_extractor.py`, `ratio_calculator.py`, `rag_service.py` integrated | End-to-end: upload PDF → metrics extracted |
| 3–4 | Implement `/query` endpoint with RAG + citations | POST `/query` returns answer + citation array | `test_api_query.py` passes |
| 5–6 | Implement `/financial-metrics/{id}`, `/financial-ratios/{id}` | GET endpoints return Dev 1 DTOs | Metrics response matches DB records |
| 7–8 | Implement `/health-score/{id}` with 5D scores | GET endpoint returns weighted scores | Health score sums to 100 |
| 9–10 | Implement centralized error handlers | `app/core/errors.py` with 6 exception handlers | `test_errors.py` covers DOC_, DB_, VALIDATION_ |
| 11–12 | Persist chunks, metrics, analysis to PostgreSQL | ORM `add_all()` + `commit()` in processing pipeline | DB query confirms rows inserted |
| 13–14 | Run full integration test suite | `pytest --cov=app` ≥ 85% | Coverage report passes threshold |

**Sprint 2 Exit Criteria**: Full user loop works — upload PDF → view extracted metrics → ask question → receive cited answer.

### Sprint 3: Comparison & Hardening (Weeks 5–6)

| Day | Task | Deliverable | Verification |
|:---|:---|:---|:---|
| 1–2 | Add composite index `(document_id, fiscal_year, fiscal_period)` | Alembic migration | `EXPLAIN ANALYZE` shows index scan |
| 3–4 | Implement `/compare` multi-document endpoint | POST `/compare` with `document_ids: List[UUID4]` | Returns side-by-side deltas |
| 5–6 | Build comparative delta engine in `comparison_service.py` | YoY/QoQ percentage change calculation | Unit test: 2 documents → correct deltas |
| 7–8 | Add database indexes for chunk retrieval | `ix_chunks_document_index` | Query plan uses index |
| 9–10 | Write unit tests for financial endpoints | `test_api_financials.py` expanded | ≥ 85% coverage maintained |
| 11–12 | Integration test: upload → process → compare | `test_integration.py` end-to-end | Full workflow passes |
| 13–14 | Performance profiling with `EXPLAIN ANALYZE` | Query time < 50ms for metrics lookup | Query plan documented |

**Sprint 3 Exit Criteria**: Multi-document comparison active; all financial endpoints tested; query performance benchmarked.

### Sprint 4: Production Hardening & pgvector Migration (Weeks 7–8)

| Day | Task | Deliverable | Verification |
|:---|:---|:---|:---|
| 1–2 | Add `vector(384)` column to `document_chunks` via Alembic | Migration script | `alembic upgrade head` succeeds |
| 3–4 | Create HNSW index on embedding column | `CREATE INDEX ... USING hnsw` | `EXPLAIN ANALYZE` uses index scan |
| 5–6 | Migrate chunk embeddings from `ARRAY(Float)` to `vector(384)` | Data migration script | Row count matches; cosine distance query returns results |
| 7–8 | Connection pool tuning based on load test | `pool_size=30`, `max_overflow=15` | 50 concurrent requests < 100ms p95 |
| 9–10 | Finalize Swagger/ReDoc documentation | `/docs` and `/redoc` with examples | All endpoints documented with response schemas |
| 11–12 | Database backup/restore verification | `pg_dump` + `pg_restore` scripts | Restored DB passes integrity checks |
| 13–14 | Final error catalog audit | All HTTP status codes mapped to error codes | `test_errors.py` covers 100% of catalog |

**Sprint 4 Exit Criteria**: pgvector-backed vector search operational; connection pool tuned; backup/restore validated; error catalog complete.

---

## Risk Register & Mitigation

| Risk | Probability | Impact | Mitigation |
|:---|:---|:---|:---|
| Dev 1 DTO changes after Sprint 1 | Medium | High | Freeze DTO signatures in `docs/INTERFACES.md`; changes require team consensus |
| PostgreSQL connection pool exhaustion under load | Low | High | `pool_pre_ping=True`, `pool_size=20`, monitoring via Prometheus metrics |
| Alembic autogenerate misses constraints | Medium | Medium | Manual review of every migration script; test upgrade + downgrade in CI |
| pgvector migration data loss | Low | Critical | Run migration in transaction; backup before migration; test on staging first |
| Test suite slow (> 5 min) | Medium | Medium | Use `NullPool` for test engine; transaction rollback per test; parallelize with `pytest-xdist` |
| Dependency override not working in TestClient | Medium | Medium | Remove `routes` param from `FastAPI()` constructor; use `app.dependency_overrides` |

---

## Daily Workflow & Collaboration Protocol

**Standup (15 min, 10:00 AM)**:
- Report: Yesterday's completed module, today's target, blockers.
- Blockers escalate to Dev 1 (DTO contract), Dev 4 (infrastructure), or team lead (scope).

**Branch Strategy**:
- `feature/d2-{module}-{sprint}` → e.g., `feature/d2-models-sprint1`
- PR requires: 1 approval + CI green (lint, type check, pytest).
- Merge to `develop` after Sprint milestone; `main` only at release tags.

**Documentation Artifacts Owned by Dev 2**:
- `docs/API.md` — Full OpenAPI spec with request/response examples
- `docs/SCHEMA.md` — ER diagram + 3NF justification
- `docs/ERROR_CATALOG.md` — Complete error code reference
- `docs/MIGRATION_GUIDE.md` — Alembic workflow for team

**Daily Code Quality Gates**:
```bash
# Run before every commit
black app/ tests/              # Formatting
flake8 app/ tests/             # Linting
mypy app/                      # Type checking
pytest --cov=app --cov-fail-under=85  # Tests + coverage
```

---

## Summary: Developer 2's Critical Path

Developer 2's work is the **backbone** of the platform. The critical path is:

```
D2-M1 (Pooling) → D2-M2 (Models) → D2-M3 (Migrations) → D2-M5 (Endpoints) → D2-M7 (Tests)
                                          ↓
                                    D2-M4 (Schemas) → D2-M6 (Errors)
```

**Key Success Factors**:
1. **Stub-first development**: Write stub service functions in Sprint 1 so routes are testable immediately.
2. **Contract freeze**: DTO signatures and API JSON schemas frozen by Day 3 of Sprint 1.
3. **Test-driven integration**: Every endpoint must have a `TestClient` test before Sprint milestone.
4. **Migration discipline**: Every schema change goes through Alembic — no manual DDL.
5. **Error code consistency**: All exceptions mapped to the standardized catalog before Sprint 2 exit.