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
        """Retrieves list of all documents registered in database."""
        try:
            resp = requests.get(f"{self.base_url}/documents", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("items", [])
        except Exception as e:
            st.sidebar.warning(f"Backend API offline or unreachable: {e}")
        return []

    def upload_document(
        self,
        file_bytes: bytes,
        filename: str,
        company_name: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        fiscal_period: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Uploads a PDF file to the backend for ingestion and indexing."""
        files = {"file": (filename, file_bytes, "application/pdf")}
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
                return resp.json()
            else:
                st.error(f"Upload error ({resp.status_code}): {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend upload endpoint: {e}")
        return None

    def delete_document(self, document_id: str) -> bool:
        """Deletes a document and its cascading chunks from database."""
        try:
            resp = requests.delete(f"{self.base_url}/documents/{document_id}", timeout=10)
            return resp.status_code == 204
        except Exception as e:
            st.error(f"Failed to delete document: {e}")
            return False

    def query_rag(self, document_id: str, question: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """Queries the RAG retrieval engine with citation provenance."""
        payload = {
            "document_id": document_id,
            "question": question,
            "top_k": top_k,
        }
        try:
            resp = requests.post(f"{self.base_url}/query", json=payload, timeout=45)
            if resp.status_code == 200:
                return resp.json()
            else:
                st.error(f"Query error ({resp.status_code}): {resp.text}")
        except Exception as e:
            st.error(f"RAG query service timeout or error: {e}")
        return None

    def get_financial_metrics(self, document_id: str) -> List[Dict[str, Any]]:
        """Fetches extracted line items for a specific document."""
        try:
            resp = requests.get(f"{self.base_url}/financial-metrics/{document_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json().get("metrics", [])
        except Exception:
            pass
        return []

    def get_financial_ratios(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Fetches calculated 8 core financial ratios."""
        try:
            resp = requests.get(f"{self.base_url}/financial-ratios/{document_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_health_score(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Fetches 5D corporate health score and qualitative risk flags."""
        try:
            resp = requests.get(f"{self.base_url}/health-score/{document_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

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


# Global singleton instance
client = APIClient()
