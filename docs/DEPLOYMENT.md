# Deployment Documentation

## Financial Document Intelligence & RAG Analytics Platform

---

## Table of Contents

- [1. Deployment Options](#1-deployment-options)
- [2. Local Development](#2-local-development)
- [3. Docker Deployment](#3-docker-deployment)
- [4. Environment Variables](#4-environment-variables)
- [5. Production Considerations](#5-production-considerations)
- [6. CI/CD Pipeline](#6-cicd-pipeline)
- [7. Health Checks & Monitoring](#7-health-checks--monitoring)
- [8. Architecture Diagram](#8-architecture-diagram)

---

## 1. Deployment Options

| Option | Use Case | Complexity | Production-Ready |
|---|---|---|---|
| **Local development** | Development and testing | Low | No |
| **Docker Compose** | Single-server deployment, demos | Medium | Partial |
| **Cloud deployment** | Production workloads | High | Yes |

---

## 2. Local Development

### Prerequisites

| Requirement | Version | Check Command |
|---|---|---|
| Python | 3.11+ | `python --version` |
| PostgreSQL | 15+ | `psql --version` |
| Git | Latest | `git --version` |
| pip | Latest | `pip --version` |

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/financial-document-intelligence.git
cd financial-document-intelligence

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing and dev tools

# 4. Set up PostgreSQL database
createdb financial_intelligence

# 5. Configure environment
cp .env.example .env
# Edit .env with your configuration (see Section 4)

# 6. Initialize database schema
python scripts/setup_db.py
# OR using Alembic:
alembic upgrade head

# 7. Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 8. Start Streamlit frontend (new terminal)
streamlit run frontend/app.py --server.port 8501
```

### Access Points (Local)

| Service | URL |
|---|---|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| API Documentation (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## 3. Docker Deployment

### Dockerfile

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/faiss_index

# Download embedding model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: fdi-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-fdi_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-fdi_password}
      POSTGRES_DB: ${POSTGRES_DB:-financial_intelligence}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-fdi_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fdi-backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-fdi_user}:${POSTGRES_PASSWORD:-fdi_password}@db:5432/${POSTGRES_DB:-financial_intelligence}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      EMBEDDING_MODEL: ${EMBEDDING_MODEL:-all-MiniLM-L6-v2}
      VECTOR_STORE_TYPE: ${VECTOR_STORE_TYPE:-faiss}
      FAISS_INDEX_PATH: /app/data/faiss_index
      APP_ENV: ${APP_ENV:-production}
    ports:
      - "8000:8000"
    volumes:
      - upload_data:/app/data/uploads
      - faiss_data:/app/data/faiss_index
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Streamlit Frontend
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: fdi-frontend
    environment:
      API_BASE_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
  upload_data:
  faiss_data:
```

### Docker Commands

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Rebuild a specific service
docker-compose up --build backend
```

---

## 4. Environment Variables

### Required Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | `Financial Document Intelligence` |
| `APP_ENV` | Environment (development/production) | `development` |
| `DEBUG` | Debug mode | `true` |
| `API_HOST` | FastAPI host | `0.0.0.0` |
| `API_PORT` | FastAPI port | `8000` |
| `STREAMLIT_PORT` | Streamlit port | `8501` |
| `OPENAI_MODEL` | LLM model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `all-MiniLM-L6-v2` |
| `EMBEDDING_DIMENSION` | Vector dimension | `384` |
| `VECTOR_STORE_TYPE` | Vector store backend | `faiss` |
| `FAISS_INDEX_PATH` | FAISS index directory | `./data/faiss_index` |
| `MAX_FILE_SIZE_MB` | Max upload size | `50` |
| `CHUNK_SIZE` | Token count per chunk | `512` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `RAG_TOP_K` | Chunks to retrieve | `5` |
| `RAG_SIMILARITY_THRESHOLD` | Min similarity score | `0.3` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SECRET_KEY` | Application secret key | *(generate random)* |

### .env.example

```env
# === Required ===
DATABASE_URL=postgresql://fdi_user:fdi_password@localhost:5432/financial_intelligence
OPENAI_API_KEY=your-openai-api-key-here

# === Application ===
APP_ENV=development
DEBUG=true
SECRET_KEY=generate-a-random-32-byte-hex-string

# === Embedding & LLM ===
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# === Vector Store ===
VECTOR_STORE_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index

# === Document Processing ===
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# === RAG ===
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.3

# === Server ===
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
```

---

## 5. Production Considerations

### Production Checklist

| # | Item | Status |
|---|---|---|
| 1 | Enable API authentication | ⏳ |
| 2 | Use strong `SECRET_KEY` | ⏳ |
| 3 | Set `APP_ENV=production` and `DEBUG=false` | ⏳ |
| 4 | Use managed PostgreSQL (e.g., AWS RDS, Cloud SQL) | ⏳ |
| 5 | Enable HTTPS/TLS | ⏳ |
| 6 | Configure rate limiting | ⏳ |
| 7 | Set up log aggregation | ⏳ |
| 8 | Configure backup strategy for database | ⏳ |
| 9 | Set resource limits on Docker containers | ⏳ |
| 10 | Migrate from FAISS to pgvector for persistence | ⏳ |
| 11 | Set up monitoring and alerting | ⏳ |

### Recommended Cloud Services

| Component | AWS | GCP | Azure |
|---|---|---|---|
| Compute | EC2 / ECS | Compute Engine / Cloud Run | Azure VM / Container Instances |
| Database | RDS PostgreSQL | Cloud SQL | Azure Database for PostgreSQL |
| File Storage | S3 | Cloud Storage | Blob Storage |
| Container Registry | ECR | Artifact Registry | ACR |
| CI/CD | CodePipeline | Cloud Build | Azure DevOps |
| Monitoring | CloudWatch | Cloud Monitoring | Azure Monitor |

---

## 6. CI/CD Pipeline

### GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff black mypy
      - run: ruff check app/
      - run: black --check app/
      - run: mypy app/ --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=app --cov-report=xml -v
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          OPENAI_API_KEY: test-key

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t fdi-backend .
```

### Pipeline Flow

```mermaid
flowchart LR
    A[Developer] --> B[Git Push]
    B --> C[GitHub]
    C --> D[CI Pipeline]
    D --> E[Lint<br/>ruff, black, mypy]
    E --> F[Test<br/>pytest + coverage]
    F --> G[Build<br/>Docker image]
    G --> H{Branch?}
    H -->|main| I[Deploy to Production]
    H -->|develop| J[Deploy to Staging]
    I --> K[Health Check]
    J --> K
```

---

## 7. Health Checks & Monitoring

### Health Check Endpoint

`GET /health` returns component-level status:

```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "connected"},
    "vector_store": {"status": "loaded"},
    "embedding_model": {"status": "loaded"},
    "llm": {"status": "available"}
  }
}
```

### Docker Health Checks

All services in `docker-compose.yml` include health checks:

- **PostgreSQL**: `pg_isready`
- **Backend**: `curl http://localhost:8000/health`
- **Frontend**: `curl http://localhost:8501`

### Monitoring Endpoints

| Metric | Source | Tool |
|---|---|---|
| API latency | FastAPI middleware | Application logs |
| Error rates | FastAPI exception handlers | Application logs |
| Database connections | SQLAlchemy pool stats | Health endpoint |
| Vector count | FAISS index size | Health endpoint |

---

## 8. Architecture Diagram

### Deployment Architecture (Docker Compose)

```mermaid
graph TB
    subgraph Host Machine
        subgraph Docker Network
            FE[Streamlit Frontend<br/>:8501]
            BE[FastAPI Backend<br/>:8000]
            DB[(PostgreSQL<br/>:5432)]
        end
        
        subgraph Volumes
            V1[postgres_data]
            V2[upload_data]
            V3[faiss_data]
        end
    end
    
    User[👤 User] --> FE
    FE --> BE
    BE --> DB
    BE --> OpenAI[☁️ OpenAI API]
    
    DB --- V1
    BE --- V2
    BE --- V3

    style User fill:#e1f5fe
    style FE fill:#fff3e0
    style BE fill:#e8f5e9
    style DB fill:#fff9c4
    style OpenAI fill:#f3e5f5
```

### Production Architecture (Cloud)

```mermaid
graph TB
    subgraph Internet
        User[👤 Users]
    end
    
    subgraph Cloud Provider
        LB[Load Balancer<br/>HTTPS]
        
        subgraph Compute
            FE[Streamlit<br/>Container]
            BE[FastAPI<br/>Container]
        end
        
        subgraph Data
            DB[(Managed PostgreSQL<br/>+ pgvector)]
            S3[Object Storage<br/>PDF Files]
        end
        
        subgraph Monitoring
            LOG[Log Aggregation]
            MON[Metrics & Alerts]
        end
    end
    
    subgraph External
        OpenAI[☁️ OpenAI API]
    end
    
    User --> LB
    LB --> FE
    LB --> BE
    FE --> BE
    BE --> DB
    BE --> S3
    BE --> OpenAI
    BE --> LOG
    BE --> MON

    style User fill:#e1f5fe
    style LB fill:#f3e5f5
    style DB fill:#fff9c4
    style S3 fill:#fff9c4
```
