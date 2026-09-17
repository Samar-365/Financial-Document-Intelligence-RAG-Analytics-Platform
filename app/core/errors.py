"""Centralized error taxonomy and FastAPI exception handlers."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError


# ─────────────────────────────────────────────────────────────
# Domain exceptions
# ─────────────────────────────────────────────────────────────
class AppException(Exception):
    """Base exception carrying an error code, HTTP status, and message."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundException(AppException):
    def __init__(self, document_id: str):
        super().__init__("DOC_003", f"Document {document_id} not found", 404)


class DuplicateDocumentException(AppException):
    def __init__(self, file_hash: str):
        super().__init__("DOC_002", f"Duplicate document (hash={file_hash[:12]})", 409)


class InvalidFileException(AppException):
    def __init__(self, reason: str = "Invalid file format"):
        super().__init__("DOC_001", reason, 400)


class ProcessingException(AppException):
    def __init__(self, reason: str):
        super().__init__("PROC_001", reason, 422)


class RAGException(AppException):
    def __init__(self, reason: str, code: str = "RAG_001"):
        super().__init__(code, reason, 422)


class AnalysisException(AppException):
    def __init__(self, reason: str):
        super().__init__("ANA_001", reason, 422)


# ─────────────────────────────────────────────────────────────
# Handler registration
# ─────────────────────────────────────────────────────────────
def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "path": str(request.url.path),
                },
                "meta": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "data": None,
                "error": {
                    "code": "VALIDATION_001",
                    "message": "Request validation failed",
                    "path": str(request.url.path),
                    "details": exc.errors(),
                },
                "meta": None,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "data": None,
                "error": {
                    "code": "DB_002",
                    "message": "Database integrity constraint violated",
                    "path": str(request.url.path),
                    "details": str(exc.orig),
                },
                "meta": None,
            },
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "data": None,
                "error": {
                    "code": "DB_001",
                    "message": "Database connection error — retry with backoff",
                    "path": str(request.url.path),
                    "details": str(exc.orig),
                },
                "meta": None,
            },
        )