"""API Rate Limiting Module — Developer 4 (DevOps, Platform & Security).

Configures SlowAPI token-bucket rate limiter middleware to protect LLM endpoints
and file upload operations from resource exhaustion attacks.
"""

from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["120/minute"],
        storage_uri="memory://",
    )
    HAS_SLOWAPI = True
except ImportError:
    HAS_SLOWAPI = False
    limiter = None  # type: ignore
    RateLimitExceeded = Exception  # type: ignore


def setup_rate_limiting(app: FastAPI) -> None:
    """Attaches rate limiting state and custom exception handlers to FastAPI application."""
    if HAS_SLOWAPI and limiter:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_limiter():
    """Returns configured limiter instance for route decorators."""
    return limiter
