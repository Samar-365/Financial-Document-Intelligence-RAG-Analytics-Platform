"""FastAPI Application Entrypoint for the Financial Document Intelligence & RAG Analytics Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

from app.core.rate_limit import setup_rate_limiting

def create_application() -> FastAPI:
    """Creates and configures the core FastAPI application instance."""
    # Configure logging
    configure_logging()

    app = FastAPI(
        title="Financial Document Intelligence & RAG Analytics Platform",
        description="Enterprise financial PDF processing, quantitative ratio analytics, and grounded RAG query engine.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register centralized exception handlers
    register_exception_handlers(app)

    # Setup rate limiting
    setup_rate_limiting(app)

    # Mount API v1 router
    app.include_router(api_router, prefix="/api/v1")

    # Attach Prometheus metrics instrumentation
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except Exception:
        pass

    @app.get("/health", tags=["System"])
    def health_check():
        """Basic system health status check."""
        return {"status": "ok", "service": "financial-intelligence-api", "version": "1.0.0"}

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
