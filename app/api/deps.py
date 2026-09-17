"""Shared FastAPI dependencies."""
from typing import Optional
from uuid import UUID, uuid4

from fastapi import Header
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.db.session import get_db  # re-exported

__all__ = ["get_db", "get_current_user_id"]


async def get_current_user_id(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> UUID:
    """Stub auth: read X-User-Id header; fall back to a demo UUID.

    Replace with real JWT verification when Dev 4 ships `security.py`.
    """
    if x_user_id:
        try:
            return UUID(x_user_id)
        except ValueError:
            raise AppException("AUTH_001", "Invalid X-User-Id header", 401)
    return UUID("00000000-0000-0000-0000-000000000001")