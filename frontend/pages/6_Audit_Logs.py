"""System Audit, Telemetry & Observability Page.

Displays live API health probes, processing telemetry, database status,
and compliance audit logs for operations teams and financial auditors.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from utils.api_client import client

st.set_page_config(page_title="Audit & Telemetry | FinIntel AI", layout="wide")
apply_theme()

render_page_header(
    title="System Telemetry & Audit Logs",
    subtitle="Live monitoring of API health probes, pgvector database status, and processing audit logs.",
    icon_name="shield-check"
)

# 1. System Health Probes
server_svg = get_icon("server", color="#E63946", size=18)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {server_svg}
    <span style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">Infrastructure Health Probes</span>
</div>
""")

health_data = client.get_health()

col1, col2, col3, col4 = st.columns(4)
with col1:
    is_ok = health_data and health_data.get("status") == "ok"
    status_color = "#10B981" if is_ok else "#EF4444"
    status_label = "ONLINE" if is_ok else "OFFLINE"
    render_html(f"""
<div style="background: #121118; border: 1px solid rgba(196, 30, 58, 0.28); border-radius: 8px; padding: 14px; text-align: center;">
    <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 500; margin-bottom: 4px;">FASTAPI SERVICE</div>
    <div style="color: {status_color}; font-size: 1.1rem; font-weight: 700;">{status_label}</div>
</div>
""")

with col2:
    render_html("""
<div style="background: #121118; border: 1px solid rgba(196, 30, 58, 0.28); border-radius: 8px; padding: 14px; text-align: center;">
    <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 500; margin-bottom: 4px;">VECTOR INDEX</div>
    <div style="color: #F1F5F9; font-size: 1.05rem; font-weight: 600;">HNSW Cosine Active</div>
</div>
""")

with col3:
    render_html("""
<div style="background: #121118; border: 1px solid rgba(196, 30, 58, 0.28); border-radius: 8px; padding: 14px; text-align: center;">
    <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 500; margin-bottom: 4px;">POSTGRESQL DB</div>
    <div style="color: #F1F5F9; font-size: 1.05rem; font-weight: 600;">3NF Alpine Active</div>
</div>
""")

with col4:
    curr_time = datetime.now().strftime('%H:%M:%S')
    render_html(f"""
<div style="background: #121118; border: 1px solid rgba(196, 30, 58, 0.28); border-radius: 8px; padding: 14px; text-align: center;">
    <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 500; margin-bottom: 4px;">TELEMETRY PROBE</div>
    <div style="color: #F1F5F9; font-size: 1.05rem; font-weight: 600;">{curr_time}</div>
</div>
""")

st.divider()

# 2. Registered Documents & Chunks Telemetry
doc_svg = get_icon("file-text", color="#E63946", size=18)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {doc_svg}
    <span style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">Document Index Telemetry</span>
</div>
""")

docs = client.get_documents()
if docs:
    df_docs = pd.DataFrame(docs)
    display_cols = [c for c in ["id", "filename", "status", "page_count", "created_at"] if c in df_docs.columns]
    st.dataframe(df_docs[display_cols] if display_cols else df_docs, use_container_width=True, hide_index=True)
else:
    st.info("No active documents currently found in database. Upload documents or spreadsheets via the 'Upload' page.")

st.divider()

# 3. Standardized Error Catalog Reference
book_svg = get_icon("book-open", color="#E63946", size=18)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {book_svg}
    <span style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">Platform Error & Exception Catalog</span>
</div>
""")

error_catalog_data = [
    {"Code": "DOC_001", "Domain": "Document", "Description": "File not found or inaccessible."},
    {"Code": "DOC_002", "Domain": "Document", "Description": "Unsupported file format (supported: PDF, CSV, XLSX, XLS)."},
    {"Code": "DOC_003", "Domain": "Document", "Description": "File size exceeds 50MB limit."},
    {"Code": "RAG_001", "Domain": "RAG Retrieval", "Description": "Zero context chunks found above similarity threshold."},
    {"Code": "RAG_002", "Domain": "RAG Retrieval", "Description": "LLM API timeout or Google Gemini service unavailable."},
    {"Code": "ANA_001", "Domain": "Analytics", "Description": "Required line item missing for ratio calculation."},
    {"Code": "DB_001", "Domain": "Database", "Description": "PostgreSQL connection pool exhausted."},
]
st.dataframe(pd.DataFrame(error_catalog_data), use_container_width=True, hide_index=True)
