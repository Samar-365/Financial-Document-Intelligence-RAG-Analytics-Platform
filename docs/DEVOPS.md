# DevOps Documentation

## Financial Document Intelligence & RAG Analytics Platform

---

## Table of Contents

- [1. Git Workflow](#1-git-workflow)
- [2. Branching Strategy](#2-branching-strategy)
- [3. Pull Request Standards](#3-pull-request-standards)
- [4. GitHub Actions CI/CD](#4-github-actions-cicd)
- [5. Docker Image Building](#5-docker-image-building)
- [6. Deployment Pipeline](#6-deployment-pipeline)
- [7. Environment Management](#7-environment-management)

---

## 1. Git Workflow

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Usage | Example |
|---|---|---|
| `feat` | New feature | `feat(rag): add similarity threshold filtering` |
| `fix` | Bug fix | `fix(extraction): handle empty PDF pages` |
| `docs` | Documentation | `docs(api): update query endpoint examples` |
| `test` | Tests | `test(ratios): add debt-to-equity edge cases` |
| `refactor` | Code restructure | `refactor(analytics): extract ratio calculator class` |
| `chore` | Maintenance | `chore(deps): update sentence-transformers to 2.5` |
| `ci` | CI/CD changes | `ci: add PostgreSQL service to test job` |
| `style` | Formatting | `style: apply black formatting` |

### .gitignore

```
# Environment
.env
venv/
.venv/

# Data (runtime)
data/uploads/
data/faiss_index/
data/evaluation/results/

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
htmlcov/
.coverage
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db
```

---

## 2. Branching Strategy

### Git Flow (Simplified)

```mermaid
gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Project setup"
    branch feature/document-processing
    checkout feature/document-processing
    commit id: "PDF extraction"
    commit id: "Chunking"
    checkout develop
    merge feature/document-processing
    branch feature/rag-pipeline
    checkout feature/rag-pipeline
    commit id: "Embeddings"
    commit id: "Retriever"
    commit id: "Generator"
    checkout develop
    merge feature/rag-pipeline
    branch feature/analytics
    checkout feature/analytics
    commit id: "Metric extraction"
    commit id: "Health score"
    checkout develop
    merge feature/analytics
    checkout main
    merge develop tag: "v1.0.0"
```

### Branch Naming

| Branch Type | Pattern | Example | Merges Into |
|---|---|---|---|
| Main | `main` | `main` | — (production) |
| Development | `develop` | `develop` | `main` |
| Feature | `feature/<description>` | `feature/rag-pipeline` | `develop` |
| Bugfix | `fix/<description>` | `fix/empty-pdf-handling` | `develop` |
| Hotfix | `hotfix/<description>` | `hotfix/api-auth-bypass` | `main` + `develop` |
| Release | `release/<version>` | `release/1.0.0` | `main` + `develop` |

### Branch Rules

| Rule | Setting |
|---|---|
| `main` branch protection | Require PR + 1 approval (if team) |
| `develop` branch protection | Require passing CI |
| Feature branches | Squash merge to `develop` |
| Delete branch after merge | Enabled |

---

## 3. Pull Request Standards

### PR Template

```markdown
## Description
<!-- What does this PR do? -->

## Type of Change
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] Tests

## Changes Made
<!-- List specific changes -->

## Testing
<!-- How was this tested? -->
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style (PEP 8, type hints)
- [ ] Docstrings added for new functions/classes
- [ ] No secrets or credentials committed
- [ ] Documentation updated if needed
```

### Code Review Guidelines

| Focus Area | What to Check |
|---|---|
| **Correctness** | Does the code do what it claims? |
| **Security** | Any hardcoded secrets? Input validation present? |
| **Testing** | Are new features covered by tests? |
| **Style** | PEP 8 compliance, type hints, docstrings |
| **Performance** | Any obvious N+1 queries, memory leaks? |
| **Documentation** | Are new APIs/features documented? |

---

## 4. GitHub Actions CI/CD

### CI Pipeline (`ci.yml`)

Runs on every push and PR to `main`/`develop`:

```yaml
name: CI

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
      - name: Install linters
        run: pip install ruff black mypy
      - name: Ruff (linting)
        run: ruff check app/
      - name: Black (formatting)
        run: black --check app/ tests/
      - name: Mypy (type checking)
        run: mypy app/ --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml -v
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          OPENAI_API_KEY: sk-test-key-for-ci
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t fdi-backend:${{ github.sha }} .
```

### Pipeline Visualization

```mermaid
flowchart TD
    A[Developer Push] --> B[GitHub Actions Trigger]
    B --> C[Lint Job]
    C --> C1[Ruff - Code Quality]
    C --> C2[Black - Formatting]
    C --> C3[Mypy - Type Checking]
    C1 & C2 & C3 --> D{All Pass?}
    D -->|No| E[ Fail - Fix Required]
    D -->|Yes| F[Test Job]
    F --> F1[Start PostgreSQL Service]
    F1 --> F2[Install Dependencies]
    F2 --> F3[Run pytest + Coverage]
    F3 --> G{All Pass?}
    G -->|No| E
    G -->|Yes| H{Main Branch?}
    H -->|Yes| I[Build Docker Image]
    H -->|No| J[ PR Checks Pass]
    I --> K[Deploy]
    K --> L[Health Check]

    style E fill:#ffebee
    style J fill:#e8f5e9
    style L fill:#e8f5e9
```

---

## 5. Docker Image Building

### Multi-Stage Build (Optimized)

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built dependencies
COPY --from=builder /install /usr/local

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd -m appuser && \
    mkdir -p /app/data/uploads /app/data/faiss_index && \
    chown -R appuser:appuser /app
USER appuser

# Pre-download embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Image Optimization

| Optimization | Implementation |
|---|---|
| Multi-stage build | Separates build and runtime stages |
| Slim base image | `python:3.11-slim` instead of full image |
| Non-root user | Application runs as `appuser` |
| Layer caching | Dependencies installed before code copy |
| No cache pip | `--no-cache-dir` reduces image size |

---

## 6. Deployment Pipeline

### Full Pipeline

```mermaid
flowchart LR
    DEV[Developer] --> GIT[Git Push]
    GIT --> GH[GitHub]
    GH --> CI[CI Pipeline]
    CI --> LINT[Lint]
    LINT --> TEST[Test]
    TEST --> BUILD[Build Image]
    BUILD --> REG[Container Registry]
    REG --> DEPLOY[Deploy]
    DEPLOY --> HC[Health Check]
    HC -->|| DONE[Live]
    HC -->|| ROLL[Rollback]
```

---

## 7. Environment Management

| Environment | Purpose | Database | LLM | Auth |
|---|---|---|---|---|
| **Development** | Local coding and testing | Local PostgreSQL | OpenAI (test key) | Disabled |
| **Testing (CI)** | Automated test execution | PostgreSQL service container | Mock / test key | Disabled |
| **Staging** | Pre-production validation | Managed PostgreSQL | OpenAI | Enabled |
| **Production** | Live deployment | Managed PostgreSQL | OpenAI | Enabled |

### Environment-Specific Configuration

All differences between environments are controlled through environment variables. No code changes are needed to deploy across environments.

```bash
# Development
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Production
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```
