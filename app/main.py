"""FastAPI Application Entrypoint for the Financial Document Intelligence & RAG Analytics Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_application() -> FastAPI:
    """Creates and configures the core FastAPI application instance."""
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

    @app.get("/health", tags=["System"])
    def health_check():
        """Basic system health status check."""
        return {"status": "ok", "service": "financial-intelligence-api", "version": "1.0.0"}

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
