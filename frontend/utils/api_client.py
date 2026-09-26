"""Frontend REST API Client for Streamlit Application (Developer 3 - Shreya).

Encapsulates all HTTP communication with Developer 2's FastAPI backend endpoints
with automatic retries, timeout protections, and friendly error notifications.
"""

import os
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from uuid import UUID

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


# Cached data access helpers for fast UI reruns
@st.cache_data(ttl=15, show_spinner=False)
def _fetch_cached_documents(base_url: str) -> List[Dict[str, Any]]:
    try:
        resp = requests.get(f"{base_url}/documents", timeout=10)
        if resp.status_code == 200:
            return resp.json().get("items", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_cached_metrics(base_url: str, document_id: str) -> List[Dict[str, Any]]:
    if not document_id:
        return []
    try:
        resp = requests.get(f"{base_url}/financial-metrics/{document_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json().get("metrics", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_cached_ratios(base_url: str, document_id: str) -> Optional[Dict[str, Any]]:
    if not document_id:
        return None
    try:
        resp = requests.get(f"{base_url}/financial-ratios/{document_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_cached_health(base_url: str, document_id: str) -> Optional[Dict[str, Any]]:
    if not document_id:
        return None
    try:
        resp = requests.get(f"{base_url}/health-score/{document_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def invalidate_financial_cache():
    """Invalidates cached documents and metrics when filings are uploaded, deleted, or re-indexed."""
    try:
        _fetch_cached_documents.clear()
        _fetch_cached_metrics.clear()
        _fetch_cached_ratios.clear()
        _fetch_cached_health.clear()
    except Exception:
        pass


class APIClient:
    """Client for interacting with the Financial Document Intelligence FastAPI backend."""

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Optional[Dict[str, Any]]:
        """Checks API server health probe."""
        try:
            url = self.base_url.replace("/api/v1", "") + "/health"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_documents(self) -> List[Dict[str, Any]]:
        """Retrieves list of all documents registered in database using cached read."""
        return _fetch_cached_documents(self.base_url)

    def upload_document(
        self,
        file_bytes: bytes,
        filename: str,
        company_name: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        fiscal_period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Uploads a PDF, CSV, or Excel file to the backend with clean error mapping."""
        files = {"file": (filename, file_bytes, "application/octet-stream")}
        data = {}
        if company_name and company_name.strip():
            data["company_name"] = company_name.strip()
        if fiscal_year:
            data["fiscal_year"] = int(fiscal_year)
        if fiscal_period and fiscal_period.strip():
            data["fiscal_period"] = fiscal_period.strip()

        try:
            resp = requests.post(f"{self.base_url}/documents/upload", files=files, data=data, timeout=60)
            if resp.status_code in [200, 201]:
                invalidate_financial_cache()
                return {
                    "success": True,
                    "is_duplicate": False,
                    "data": resp.json(),
                    "user_message": f"'{filename}' has been added to your workspace.",
                    "status_code": resp.status_code,
                }
            
            # Map backend error responses gracefully without raw JSON exposure
            resp_data = {}
            try:
                resp_data = resp.json()
            except Exception:
                pass

            err_code = resp_data.get("error", {}).get("code", "") if isinstance(resp_data.get("error"), dict) else ""
            err_msg = resp_data.get("error", {}).get("message", "") if isinstance(resp_data.get("error"), dict) else str(resp_data)

            if resp.status_code == 409 or err_code == "DOC_002" or "duplicate" in err_msg.lower():
                return {
                    "success": False,
                    "is_duplicate": True,
                    "error_code": "DOC_002",
                    "user_message": "This document has already been uploaded and processed. You can select it from your document workspace instead.",
                    "status_code": 409,
                    "data": None,
                }
            elif resp.status_code in (400, 422) or err_code == "DOC_001" or "format" in err_msg.lower() or "extension" in err_msg.lower():
                return {
                    "success": False,
                    "is_duplicate": False,
                    "error_code": "DOC_001",
                    "user_message": "This file format is not supported. Please upload a PDF, CSV, XLSX, or XLS file.",
                    "status_code": resp.status_code,
                    "data": None,
                }
            elif resp.status_code == 413 or err_code == "DOC_003" or "size" in err_msg.lower():
                return {
                    "success": False,
                    "is_duplicate": False,
                    "error_code": "DOC_003",
                    "user_message": "This file exceeds the maximum allowed size (50MB).",
                    "status_code": 413,
                    "data": None,
                }
            else:
                return {
                    "success": False,
                    "is_duplicate": False,
                    "error_code": err_code or "UNKNOWN",
                    "user_message": "Something went wrong while uploading the document. Please try again.",
                    "status_code": resp.status_code,
                    "data": None,
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "is_duplicate": False,
                "error_code": "NET_001",
                "user_message": "Unable to reach the server. Please check your connection and try again.",
                "status_code": 0,
                "data": None,
            }
        except Exception:
            return {
                "success": False,
                "is_duplicate": False,
                "error_code": "INTERNAL",
                "user_message": "Something went wrong while uploading the document. Please try again.",
                "status_code": 500,
                "data": None,
            }

    def delete_document(self, document_id: str) -> bool:
        """Deletes a document and its cascading chunks from database."""
        try:
            resp = requests.delete(f"{self.base_url}/documents/{document_id}", timeout=10)
            if resp.status_code == 204:
                invalidate_financial_cache()
                return True
            return False
        except Exception:
            return False

    def query_rag(self, document_id: str, question: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """Queries the RAG retrieval engine with citation provenance (lazy loaded on demand)."""
        payload = {
            "document_id": document_id,
            "question": question,
            "top_k": top_k,
        }
        try:
            resp = requests.post(f"{self.base_url}/query", json=payload, timeout=45)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_financial_metrics(self, document_id: str) -> List[Dict[str, Any]]:
        """Fetches extracted line items for a specific document with cached read."""
        return _fetch_cached_metrics(self.base_url, document_id)

    def get_financial_ratios(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Fetches calculated 8 core financial ratios with cached read."""
        return _fetch_cached_ratios(self.base_url, document_id)

    def get_health_score(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Fetches 5D corporate health score and qualitative risk flags with cached read."""
        return _fetch_cached_health(self.base_url, document_id)

    def compare_documents(self, document_ids: List[str]) -> Optional[Dict[str, Any]]:
        """Performs multi-period side-by-side comparative analysis."""
        payload = {"document_ids": document_ids}
        try:
            resp = requests.post(f"{self.base_url}/compare", json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            st.error(f"Comparative analytics failed: {e}")
        return None


# Global singleton instance cached as a long-lived Streamlit resource
@st.cache_resource
def get_api_client() -> APIClient:
    return APIClient()


client = get_api_client()

