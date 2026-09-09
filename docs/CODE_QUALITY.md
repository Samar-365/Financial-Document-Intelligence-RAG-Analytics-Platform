# Code Quality Standards

## Financial Document Intelligence & RAG Analytics Platform

---

## 1. Python Style

| Standard | Rule |
|---|---|
| **PEP 8** | All code follows PEP 8 style guidelines |
| **Line length** | Maximum 100 characters (configurable in ruff) |
| **Formatter** | Black (with default settings) |
| **Linter** | Ruff |
| **Type checker** | mypy (with `--ignore-missing-imports`) |

### Enforced via CI

```bash
# Format check
black --check app/ tests/

# Lint
ruff check app/

# Type check
mypy app/ --ignore-missing-imports
```

---

## 2. Type Hints

All function signatures must include type annotations:

```python
# ✅ Correct
def calculate_ratio(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0:
        return None
    return numerator / denominator

# ❌ Incorrect
def calculate_ratio(numerator, denominator):
    return numerator / denominator
```

---

## 3. Docstrings

All modules, classes, and public functions must have docstrings (Google style):

```python
def extract_metrics(chunks: List[Chunk], document_id: UUID) -> List[ExtractedMetric]:
    """Extract financial metrics from document chunks.

    Identifies and extracts key financial figures (Revenue, EBITDA, etc.)
    from processed document chunks using pattern matching and NLP.

    Args:
        chunks: List of document text chunks with metadata.
        document_id: UUID of the source document.

    Returns:
        List of extracted metrics with values, units, and confidence scores.

    Raises:
        ExtractionError: If the extraction pipeline fails critically.
    """
```

---

## 4. Modular Architecture

| Principle | Rule |
|---|---|
| **Single Responsibility** | Each module/class has one clear purpose |
| **No circular imports** | Dependencies flow downward (API → Service → Processing → Data) |
| **Interface abstraction** | External services (VectorStore, LLM) accessed through abstract interfaces |
| **Dependency injection** | Services receive dependencies through constructors, not global imports |

---

## 5. Configuration

| Rule | Implementation |
|---|---|
| No hardcoded values | All configuration in `.env` or `config.py` |
| Pydantic Settings | `BaseSettings` class for validated configuration |
| No secrets in code | API keys only via environment variables |

---

## 6. Exception Handling

```python
# ✅ Specific exceptions with context
try:
    text = extract_pdf_text(file_path)
except PDFReadError as e:
    logger.error(f"PDF extraction failed: {e}", extra={"file": file_path})
    raise ProcessingError(f"Could not extract text from PDF") from e

# ❌ Bare except
try:
    text = extract_pdf_text(file_path)
except:
    pass
```

---

## 7. Testing Standards

| Standard | Target |
|---|---|
| Unit test coverage | ≥ 80% |
| All public functions tested | Required |
| Test naming | `test_<function>_<scenario>` |
| Fixtures over setup/teardown | Preferred |
| No test interdependence | Each test runs independently |

---

## 8. Logging

| Rule | Implementation |
|---|---|
| Use structured logging | JSON format with timestamp, level, module |
| Appropriate log levels | DEBUG for diagnostics, INFO for operations, WARNING/ERROR for issues |
| No sensitive data in logs | Never log API keys, passwords, or full document content |

---

## 9. Git Conventions

| Convention | Standard |
|---|---|
| Commit messages | Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`) |
| Branch naming | `feature/`, `fix/`, `hotfix/`, `release/` prefixes |
| PR size | Keep PRs focused — one feature or fix per PR |
| .gitignore | Comprehensive — no data files, secrets, or caches committed |

---

## 10. Pull Request Checklist

Before submitting a PR:

- [ ] Code passes `black --check`
- [ ] Code passes `ruff check`
- [ ] Code passes `mypy` (no new type errors)
- [ ] All existing tests pass
- [ ] New functionality has tests
- [ ] Public functions have docstrings
- [ ] No hardcoded credentials or secrets
- [ ] Documentation updated if public API changed
- [ ] Commit messages follow Conventional Commits
