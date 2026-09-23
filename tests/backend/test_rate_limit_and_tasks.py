"""Unit tests for Rate Limiting and Background Task Queue Modules (Developer 4)."""

from fastapi import FastAPI
from app.core.rate_limit import setup_rate_limiting, get_limiter
from app.core.tasks import celery_app, process_document_async, HAS_CELERY


def test_rate_limiting_setup():
    """Verify rate limiter initialization and attachment to FastAPI app."""
    test_app = FastAPI()
    setup_rate_limiting(test_app)
    limiter = get_limiter()
    # If slowapi is installed, limiter is present
    if limiter is not None:
        assert hasattr(test_app.state, "limiter")
        assert test_app.state.limiter is limiter


def test_tasks_module_configuration():
    """Verify Celery task queue configurations and worker definitions."""
    if HAS_CELERY and celery_app:
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "UTC"
        assert process_document_async.name == "tasks.process_document_async"
