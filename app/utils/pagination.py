"""Pagination helpers."""
import math
from typing import Sequence, TypeVar

T = TypeVar("T")


def paginate(items: Sequence[T], page: int, page_size: int) -> dict:
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": list(items[start:end]),
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)),
    }