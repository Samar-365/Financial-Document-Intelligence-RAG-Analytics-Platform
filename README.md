<h1> Financial Document Intelligence & RAG Analytics Platform</h1>
  <p>
    <strong>AI-powered financial document analysis platform combining Retrieval-Augmented Generation with explainable financial analytics to deliver citation-grounded insights from corporate filings.</strong>
  </p>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
</p>

<p>
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square" alt="PRs Welcome">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [How It Works](#how-it-works)
- [RAG Pipeline](#rag-pipeline)
- [Financial Analytics](#financial-analytics)
- [Dashboard](#dashboard)
- [Example Workflow](#example-workflow)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Overview](#api-overview)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Evaluation](#evaluation)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Deployment](#deployment)
- [Contributors](#contributors)
- [License](#license)

---

## Overview

The **Financial Document Intelligence & RAG Analytics Platform** is an end-to-end AI-powered system that transforms unstructured financial documents — annual reports, quarterly filings, earnings reports, and investor presentations — into structured, queryable financial intelligence.

Unlike generic document chatbots, this platform is purpose-built for financial analysis. It combines:

- **Retrieval-Augmented Generation (RAG)** for citation-grounded question answering
- **Automated financial metric extraction** from unstructured text
- **Financial ratio analysis and year-over-year comparison**
- **Explainable financial health scoring** (0–100 scale)
- **AI-driven risk identification** with document evidence
- **Interactive analytics dashboards** with KPI visualization

Every AI-generated insight is grounded in document evidence and accompanied by source citations, ensuring transparency and explainability.

> **Note**: This platform is designed for analytical and research purposes. It does not provide certified financial advice, investment recommendations, or trading signals.

---

## Problem Statement

Financial analysts, researchers, and students routinely process large volumes of financial documents — annual reports often exceed 200+ pages. Extracting specific metrics, comparing year-over-year performance, and identifying risks requires:

1. **Manual reading** of hundreds of pages per document
2. **Manual data extraction** of financial figures from tables and narratives
3. **Manual calculation** of financial ratios and growth metrics
4. **Cross-referencing** multiple documents for trend analysis
5. **Subjective interpretation** without standardized scoring

This process is time-consuming, error-prone, and difficult to scale. Existing tools either provide generic document Q&A without financial domain understanding, or require structured data inputs that don't exist for most corporate filings.

---

## Solution

This platform automates the entire financial document analysis workflow:

```
Upload PDF → Extract & Chunk → Embed → Index → Query → Analyze → Visualize
```

**Key differentiators from generic document Q&A systems:**

| Capability | Generic Chatbot | This Platform |
|---|---|---|
| Document Q&A | ✅ | ✅ |
| Source citations | ❌ | ✅ |
| Financial metric extraction | ❌ | ✅ |
| Financial ratio calculation | ❌ | ✅ |
| Year-over-year comparison | ❌ | ✅ |
| Financial health scoring | ❌ | ✅ |
| Risk identification | ❌ | ✅ |
| Analytics dashboard | ❌ | ✅ |
| Hallucination mitigation | ❌ | ✅ |
| Multi-document comparison | ❌ | ✅ |

---

## Key Features

### RAG-Powered Financial Q&A
Ask natural-language questions about uploaded financial documents. Answers are generated from retrieved document evidence, not fabricated by the LLM.

### Citation-Grounded Responses
Every answer includes document name, page number, and relevant section references — enabling users to verify AI-generated insights.

### Automated Financial Metric Extraction
Automatically identifies and extracts 12 key financial metrics: Revenue, Gross Profit, EBITDA, Operating Income, Net Income, EPS, Total Assets, Total Liabilities, Debt, Cash, Operating Cash Flow, and Free Cash Flow.

### Financial Ratio Analysis
Calculates 8 financial ratios including Revenue Growth, Profit Margin, EBITDA Margin, Current Ratio, Debt-to-Equity, ROA, ROE, and Operating Cash Flow Ratio.

### Financial Health Scoring
Generates an explainable 0–100 financial health score across 5 dimensions: Growth (20%), Profitability (25%), Liquidity (20%), Leverage (20%), and Cash Flow (15%).

### Risk Identification
Identifies financial, market, operational, regulatory, credit, liquidity, and business risks from document evidence — each with severity level, supporting evidence, and source page.

### Year-over-Year Comparison
Compares financial performance across periods with percentage change calculations and trend identification.

### Interactive Dashboard
Streamlit-based analytics dashboard with KPI cards, trend charts, risk summaries, and AI insights.

### Multi-Document Comparison
Compare two financial documents (e.g., FY2024 vs FY2025 annual reports) to identify metric changes, new risks, and business developments.

### Semantic Document Search
Search across all uploaded documents using natural language, financial terms, or keywords — powered by vector similarity search.

---

## System Architecture

```mermaid
graph TB
    User[ User] --> UI[Streamlit Frontend]
    UI --> API[FastAPI Backend]
    
    API --> DocEngine[Document Processing Engine]
    API --> RAGEngine[RAG Engine]
    API --> AnalyticsEngine[Financial Analytics Engine]
    
    DocEngine --> PDFParser[PDF Parser<br/>PyMuPDF / pdfplumber]
    DocEngine --> Chunker[Text Chunker]
    DocEngine --> EmbedGen[Embedding Generator<br/>Sentence Transformers]
    
    RAGEngine --> VectorDB[(Vector Store<br/>FAISS / pgvector)]
    RAGEngine --> LLM[LLM<br/>OpenAI GPT-4o-mini]
    
    AnalyticsEngine --> MetricExtractor[Metric Extractor]
    AnalyticsEngine --> RatioCalc[Ratio Calculator]
    AnalyticsEngine --> HealthScore[Health Score Engine]
    AnalyticsEngine --> RiskAnalyzer[Risk Analyzer]
    
    DocEngine --> DB[(PostgreSQL)]
    RAGEngine --> DB
    AnalyticsEngine --> DB
    
    EmbedGen --> VectorDB

    style User fill:#e1f5fe
    style UI fill:#fff3e0
    style API fill:#e8f5e9
    style DocEngine fill:#f3e5f5
    style RAGEngine fill:#fce4ec
    style AnalyticsEngine fill:#e0f2f1
    style DB fill:#fff9c4
    style VectorDB fill:#fff9c4
    style LLM fill:#f3e5f5
```

### Architecture Layers

| Layer | Responsibility | Technology |
|---|---|---|
| **Presentation** | User interface, visualization | Streamlit, Plotly |
| **API** | REST endpoints, request handling | FastAPI |
| **Document Processing** | PDF parsing, chunking, embedding | PyMuPDF, pdfplumber, Sentence Transformers |
| **RAG** | Retrieval, context construction, generation | FAISS, OpenAI API |
| **Analytics** | Metrics, ratios, scoring, risk analysis | Pandas, scikit-learn |
| **Data** | Persistence, vector storage | PostgreSQL, FAISS/pgvector |

> For detailed architecture documentation, see [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Core application logic |
| **Frontend** | Streamlit | Interactive analytics dashboard |
| **Backend** | FastAPI | REST API server |
| **Database** | PostgreSQL | Structured data persistence |
| **Vector Store** | FAISS (MVP) / pgvector (production) | Embedding storage and similarity search |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) | Document chunk embeddings |
| **LLM** | OpenAI GPT-4o-mini | RAG response generation |
| **PDF Processing** | PyMuPDF, pdfplumber | Text and table extraction |
| **Data Analysis** | Pandas, NumPy | Financial calculations |
| **ML** | scikit-learn | Scoring and classification |
| **Visualization** | Plotly | Interactive charts |
| **Containerization** | Docker, Docker Compose | Deployment packaging |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Version Control** | Git, GitHub | Source code management |

---

## How It Works

```mermaid
flowchart LR
    A[ Upload PDF] --> B[ Validate]
    B --> C[ Extract Text]
    C --> D[ Chunk]
    D --> E[ Embed]
    E --> F[ Store]
    F --> G{User Action}
    G --> H[ Ask Question]
    G --> I[ View Analytics]
    G --> J[ Compare Documents]
    H --> K[ RAG Pipeline]
    I --> L[ Dashboard]
    J --> M[ Comparison Report]
```

### Step-by-Step Flow

1. **Upload** — User uploads a financial document (PDF) through the Streamlit UI or REST API
2. **Validate** — System validates file type, size, and checks for duplicate uploads
3. **Extract** — PyMuPDF/pdfplumber extracts text and table content from the PDF
4. **Clean** — Raw text is cleaned, normalized, and sections are detected
5. **Chunk** — Document is split into semantic chunks (~512 tokens with 50-token overlap)
6. **Embed** — Each chunk is converted to a 384-dimensional vector using Sentence Transformers
7. **Store** — Chunks and embeddings are stored in PostgreSQL and the vector database
8. **Analyze** — Financial metrics are automatically extracted and ratios calculated
9. **Query** — Users interact through Q&A, dashboard, or comparison interfaces

---

## RAG Pipeline

The Retrieval-Augmented Generation pipeline ensures that all AI-generated answers are grounded in document evidence.

```mermaid
flowchart TD
    Q[User Question] --> QE[Query Embedding<br/>Sentence Transformers]
    QE --> VS[Vector Search<br/>Top-K Retrieval]
    VS --> RF[Relevance Filtering<br/>Score Threshold]
    RF --> CC[Context Construction<br/>Chunk Assembly]
    CC --> PP[Prompt Construction<br/>System + Context + Query]
    PP --> LLM[LLM Generation<br/>GPT-4o-mini]
    LLM --> CG[Citation Generation<br/>Source Mapping]
    CG --> RV[Response Validation<br/>Hallucination Check]
    RV --> R[ Grounded Response<br/>+ Citations]

    style Q fill:#e3f2fd
    style R fill:#e8f5e9
    style LLM fill:#f3e5f5
```

### Hallucination Mitigation

| Strategy | Description |
|---|---|
| **Retrieval grounding** | LLM only sees retrieved document chunks, not its parametric knowledge |
| **System prompt constraints** | Explicit instruction to answer only from provided context |
| **Citation requirement** | Every claim must map to a specific source chunk |
| **Confidence signaling** | System indicates when information is insufficient |
| **No-answer fallback** | Returns "information not found" rather than fabricating data |

> For detailed RAG architecture, see [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md#rag-architecture).

---

## Financial Analytics

### Extracted Metrics

| Metric | Description |
|---|---|
| Revenue | Total revenue / net sales |
| Gross Profit | Revenue minus cost of goods sold |
| EBITDA | Earnings before interest, taxes, depreciation, amortization |
| Operating Income | Profit from core operations |
| Net Income | Bottom-line profit after all expenses |
| EPS | Earnings per share |
| Total Assets | Sum of all assets |
| Total Liabilities | Sum of all liabilities |
| Total Debt | Short-term + long-term debt |
| Cash | Cash and cash equivalents |
| Operating Cash Flow | Cash generated from operations |
| Free Cash Flow | Operating cash flow minus capital expenditure |

### Financial Ratios

| Ratio | Formula |
|---|---|
| Revenue Growth | (Current Revenue − Previous Revenue) / Previous Revenue × 100 |
| Profit Margin | Net Income / Revenue × 100 |
| EBITDA Margin | EBITDA / Revenue × 100 |
| Current Ratio | Current Assets / Current Liabilities |
| Debt-to-Equity | Total Debt / Total Equity |
| Return on Assets | Net Income / Total Assets × 100 |
| Return on Equity | Net Income / Shareholders' Equity × 100 |
| Operating Cash Flow Ratio | Operating Cash Flow / Current Liabilities |

### Financial Health Score (0–100)

| Dimension | Weight | What It Measures |
|---|---|---|
| Growth | 20% | Revenue and earnings growth trajectory |
| Profitability | 25% | Margin quality and earnings power |
| Liquidity | 20% | Short-term obligation coverage |
| Leverage | 20% | Debt burden and capital structure |
| Cash Flow | 15% | Cash generation and operational efficiency |

>  The financial health score is an **indicative analytical metric** designed for research and educational purposes. It is not a certified credit rating, investment recommendation, or professional financial advice.

---

## Dashboard

The Streamlit dashboard provides five main views:

| Page | Description |
|---|---|
| **Dashboard** | Company overview, health score, KPI cards, AI insights, risk summary |
| **Document Upload** | Drag-and-drop upload, file validation, processing status tracker |
| **Financial Analysis** | Detailed KPI cards, charts, ratios, trend analysis |
| **AI Analyst** | Chat interface with suggested questions, source citations |
| **Comparison** | Side-by-side document comparison with metric changes and AI summary |

> For detailed UI specifications, see [docs/UI_SPECIFICATION.md](docs/UI_SPECIFICATION.md).

---

## Example Workflow

### 1. Upload & Process

```
User uploads: "ABC_Ltd_Annual_Report_2025.pdf"
→ System validates PDF format
→ Extracts 245 pages of text
→ Creates 487 semantic chunks
→ Generates 487 embeddings (384-dim each)
→ Stores in vector database
→ Extracts 12 financial metrics
→ Status: PROCESSED 
```

### 2. Ask a Question

```
User: "What was ABC Ltd's revenue in FY2025?"

System Response:
  ABC Ltd reported total revenue of ₹11,450 crore for FY2025,
  representing a year-over-year increase of 12.25% compared to
  ₹10,200 crore in FY2024.

  Sources:
  • ABC Ltd Annual Report 2025, Page 87
  • Consolidated Statement of Profit & Loss
```

### 3. View Financial Health

```
Financial Health Score: 78/100

  Growth:        86/100  ████████▌
  Profitability:  82/100  ████████▏
  Liquidity:     71/100  ███████
  Leverage:      74/100  ███████▍
  Cash Flow:     77/100  ███████▋

  AI Insights:
  • Revenue increased by 12.4% driven by [evidence]
  • Debt decreased by 7.1%, improving leverage position
  • Operating cash flow improved by [evidence]
  • Regulatory risk remains significant — see Page 103
```

---

## Screenshots

> 📸 Screenshots will be added after the frontend implementation is complete.
>
> Planned screenshots:
> - Dashboard overview with KPI cards and health score
> - Document upload interface with processing status
> - AI Analyst chat with citation-grounded responses
> - Financial comparison view (FY2024 vs FY2025)
> - Financial trend charts

---

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for containerized deployment)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/financial-document-intelligence.git
cd financial-document-intelligence
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL

```bash
# Create database
createdb financial_intelligence

# Run migrations (if using Alembic)
alembic upgrade head
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

---

## Configuration

Create a `.env` file in the project root:

```env
# Application
APP_NAME=Financial Document Intelligence
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/financial_intelligence

# OpenAI
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Vector Store
VECTOR_STORE_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index

# Document Processing
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=.pdf
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
STREAMLIT_PORT=8501
```

---

## Running the Application

### Local Development

```bash
# Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Streamlit frontend (in a separate terminal)
streamlit run frontend/app.py --server.port 8501
```

### Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Access:
# Frontend: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/documents/upload` | Upload a financial document |
| `GET` | `/documents` | List all uploaded documents |
| `GET` | `/documents/{id}` | Get document details |
| `DELETE` | `/documents/{id}` | Delete a document |
| `POST` | `/documents/{id}/process` | Trigger document processing |
| `POST` | `/query` | Ask a question (RAG) |
| `POST` | `/compare` | Compare two documents |
| `GET` | `/analytics/{document_id}` | Get financial analytics |
| `GET` | `/health` | System health check |

> For complete API documentation with request/response schemas, see [docs/API.md](docs/API.md).

---

## Project Structure

```
project-root/
│
├── app/                          # Backend application
│   ├── api/                      # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── documents.py          # Document upload/management endpoints
│   │   ├── query.py              # RAG query endpoint
│   │   ├── analytics.py          # Financial analytics endpoints
│   │   └── health.py             # Health check endpoint
│   ├── core/                     # Application configuration
│   │   ├── __init__.py
│   │   ├── config.py             # Settings and environment variables
│   │   ├── database.py           # Database connection and session
│   │   └── security.py           # Authentication and validation
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── financial_metric.py
│   │   └── analysis_result.py
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── query.py
│   │   └── analytics.py
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   └── comparison_service.py
│   ├── document_processing/      # Document ingestion pipeline
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py
│   │   ├── text_cleaner.py
│   │   ├── section_detector.py
│   │   └── chunking.py
│   ├── rag/                      # RAG pipeline
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── generator.py
│   ├── analytics/                # Financial analytics engine
│   │   ├── __init__.py
│   │   ├── metric_extractor.py
│   │   ├── ratio_calculator.py
│   │   ├── health_score.py
│   │   └── risk_analyzer.py
│   ├── utils/                    # Shared utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── main.py                   # FastAPI application entry point
│
├── frontend/                     # Streamlit frontend
│   ├── app.py                    # Main Streamlit application
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── upload.py
│   │   ├── analysis.py
│   │   ├── analyst.py
│   │   └── comparison.py
│   └── components/
│       ├── kpi_card.py
│       ├── health_gauge.py
│       └── chat_interface.py
│
├── tests/                        # Test suite
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── evaluation/
│
├── data/                         # Data storage (gitignored)
│   ├── uploads/
│   ├── faiss_index/
│   └── evaluation/
│
├── docs/                         # Project documentation
│
├── scripts/                      # Utility scripts
│   ├── setup_db.py
│   └── seed_data.py
│
├── .env.example                  # Environment variable template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md
```

> For detailed directory descriptions, see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
```

### Test Categories

| Category | Scope | Framework |
|---|---|---|
| Unit Tests | Individual functions and classes | pytest |
| Integration Tests | End-to-end pipeline flows | pytest |
| API Tests | REST endpoint validation | pytest + FastAPI TestClient |
| RAG Evaluation | Retrieval and generation quality | Custom evaluation framework |

> For detailed testing strategy, see [docs/TESTING.md](docs/TESTING.md).

---

## Evaluation

### RAG Quality Metrics

| Metric | Description | Target |
|---|---|---|
| Retrieval Precision | % of retrieved chunks that are relevant | ≥ 80% |
| Retrieval Recall | % of relevant chunks that are retrieved | ≥ 75% |
| Answer Relevance | Semantic similarity of answer to question | ≥ 0.8 |
| Citation Accuracy | % of citations pointing to correct sources | ≥ 90% |
| Faithfulness | % of answer claims supported by context | ≥ 95% |
| Hallucination Rate | % of unsupported claims in responses | ≤ 5% |

> For the complete evaluation framework, see [docs/AI_EVALUATION.md](docs/AI_EVALUATION.md).

---

## Security Considerations

- **File validation**: Only PDF files accepted; MIME type and magic byte verification
- **API authentication**: Token-based authentication for API endpoints
- **Secrets management**: All credentials stored in environment variables, never in source code
- **Input sanitization**: User inputs validated and sanitized before processing
- **Prompt injection mitigation**: System prompts designed to resist injection attacks
- **Document isolation**: User documents stored in isolated paths
- **SQL injection prevention**: Parameterized queries via SQLAlchemy ORM

> For comprehensive security documentation, see [docs/SECURITY.md](docs/SECURITY.md).

---

## Limitations

- **PDF extraction accuracy**: Complex layouts, scanned documents, and intricate tables may not extract perfectly
- **Table extraction**: Financial tables with merged cells or non-standard formatting may lose structure
- **OCR limitations**: Scanned PDFs require OCR, which introduces potential errors
- **LLM hallucination**: Despite mitigation strategies, LLMs may occasionally generate unsupported claims
- **Context window**: Very long documents may exceed LLM context limits, requiring careful chunk selection
- **Financial terminology**: Ambiguous or non-standard financial terms may be misinterpreted
- **Historical data**: System only analyzes uploaded documents — no external financial data integration
- **Language**: Currently optimized for English-language financial documents

> For detailed limitations discussion, see [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

---

## Future Enhancements

| Enhancement | Priority | Difficulty |
|---|---|---|
| Multi-company portfolio analysis | High | Medium |
| FinBERT sentiment analysis | High | Medium |
| Financial news integration | Medium | Medium |
| Earnings call transcript analysis | Medium | Hard |
| Time-series forecasting | Medium | Hard |
| Fraud/anomaly detection | Low | Hard |
| Agentic financial research | Low | Hard |
| Local LLM deployment (Ollama) | Medium | Easy |
| Enterprise RBAC | Low | Medium |
| Kubernetes deployment | Low | Medium |

> For detailed enhancement descriptions, see [docs/FUTURE_ENHANCEMENTS.md](docs/FUTURE_ENHANCEMENTS.md).

---

## Deployment

### Docker Compose (Recommended)

```bash
docker-compose up --build -d
```

### Manual Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Start FastAPI backend
4. Start Streamlit frontend

> For detailed deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Contributors

| Name | Role |
|---|---|
| **Samar** | Developer — Architecture, Backend, AI/ML, Analytics |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

| Document | Description |
|---|---|
| [SRS](docs/SRS.md) | Software Requirements Specification |
| [System Design](docs/SYSTEM_DESIGN.md) | Architecture and design documentation |
| [Database](docs/DATABASE.md) | Database schema and ER diagram |
| [API](docs/API.md) | REST API documentation |
| [UI Specification](docs/UI_SPECIFICATION.md) | Frontend interface specification |
| [Testing](docs/TESTING.md) | Testing strategy and test cases |
| [AI Evaluation](docs/AI_EVALUATION.md) | RAG evaluation framework |
| [Security](docs/SECURITY.md) | Security documentation |
| [Deployment](docs/DEPLOYMENT.md) | Deployment guide |
| [Roadmap](docs/ROADMAP.md) | Development roadmap |
| [Full Index](docs/INDEX.md) | Complete documentation index |

---

