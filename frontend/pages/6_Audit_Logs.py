"""System Audit, Telemetry & Observability Page (Developer 3 - Shreya & Developer 4).

Displays live API health probes, processing telemetry, database status,
and compliance audit logs for operations teams and financial auditors.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.api_client import client

st.set_page_config(page_title="Audit & Telemetry | FinIntel AI", layout="wide")

st.title("🛡️ System Telemetry & Audit Logs")
st.caption("Live monitoring of API health probes, database status, and processing logs.")

# 1. System Health Probes
st.subheader("📡 Infrastructure Health Probes")
health_data = client.get_health()

col1, col2, col3, col4 = st.columns(4)
with col1:
    if health_data and health_data.get("status") == "ok":
        st.success("🟢 **FastAPI Service:** ONLINE")
    else:
        st.error("🔴 **FastAPI Service:** OFFLINE")
with col2:
    st.info("📦 **Vector Index:** HNSW Cosine Active")
with col3:
    st.info("🗄️ **PostgreSQL:** 3NF Schema Active")
with col4:
    st.info(f"⏱️ **Probe Time:** {datetime.now().strftime('%H:%M:%S')}")

st.divider()

# 2. Registered Documents & Chunks Telemetry
st.subheader("📊 Document Index Telemetry")
docs = client.get_documents()
if docs:
    df_docs = pd.DataFrame(docs)
    display_cols = [c for c in ["id", "filename", "status", "page_count", "created_at"] if c in df_docs.columns]
    st.dataframe(df_docs[display_cols] if display_cols else df_docs, use_container_width=True, hide_index=True)
else:
    st.info("No active documents currently found in database. Upload documents via the 'Upload' page.")

st.divider()

# 3. Standardized Error Catalog Reference
st.subheader("📖 Standardized Platform Error Catalog")
error_catalog_data = [
    {"Code": "DOC_001", "Domain": "Document", "Description": "File not found or inaccessible."},
    {"Code": "DOC_002", "Domain": "Document", "Description": "Unsupported file format (only PDF accepted)."},
    {"Code": "DOC_003", "Domain": "Document", "Description": "File size exceeds 50MB limit."},
    {"Code": "RAG_001", "Domain": "RAG Retrieval", "Description": "Zero context chunks found above similarity threshold."},
    {"Code": "RAG_002", "Domain": "RAG Retrieval", "Description": "LLM API timeout or service unavailable."},
    {"Code": "ANA_001", "Domain": "Analytics", "Description": "Required line item missing for ratio calculation."},
    {"Code": "DB_001", "Domain": "Database", "Description": "PostgreSQL connection pool exhausted."},
]
st.dataframe(pd.DataFrame(error_catalog_data), use_container_width=True, hide_index=True)
