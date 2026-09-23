"""Asynchronous Background Task Queue Module — Developer 4 (DevOps, Platform & Security).

Configures Celery + Redis worker for offloading 100+ page PDF extraction,
dense vector embedding generation, and analytical metric calculations.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    from celery import Celery

    celery_app = Celery(
        "fdi_tasks",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=1800,  # 30 minute maximum timeout for 500+ page filings
    )
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    celery_app = None  # type: ignore


if HAS_CELERY and celery_app:
    @celery_app.task(bind=True, name="tasks.process_document_async")
    def process_document_async(self, document_id: str, file_path: str) -> Dict[str, Any]:
        """Asynchronous background worker task for full document processing lifecycle."""
        logger.info(f"Starting Celery background processing for doc {document_id} from {file_path}")
        try:
            from app.db.session import SessionLocal
            from app.services.document_service import process_document_pipeline

            db = SessionLocal()
            try:
                result = process_document_pipeline(db=db, document_id=document_id, file_path=file_path)
                return {"status": "SUCCESS", "document_id": document_id, "result": result}
            finally:
                db.close()
        except Exception as exc:
            logger.error(f"Error processing document {document_id} asynchronously: {exc}")
            raise self.retry(exc=exc, countdown=10, max_retries=3)
