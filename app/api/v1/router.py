"""Aggregates all v1 endpoint routers."""
from fastapi import APIRouter

from app.api.v1.endpoints import documents, financials, health, query

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(query.router)
api_router.include_router(financials.router)
api_router.include_router(health.router)