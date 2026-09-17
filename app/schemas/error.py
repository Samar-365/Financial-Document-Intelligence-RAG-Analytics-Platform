"""Standard error response schema."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    path: Optional[str] = None
    details: Optional[list] = None