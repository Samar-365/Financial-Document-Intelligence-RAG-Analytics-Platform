import streamlit as st
import sys
from pathlib import Path

st.set_page_config(
    page_title="FinIntel AI | Financial Analytics Platform",
    page_icon="📊",
    layout="wide"
)

sys.path.append(str(Path(__file__).resolve().parent))
from utils.api_client import client

# Fetch live documents dynamically from backend
live_docs = client.get_documents() or []
st.session_state["document_list"] = [
    {
        "Filename": d.get("filename", "Unknown"),
        "Company": d.get("company_name", "Enterprise Corp"),
        "Year": f"FY{d.get('fiscal_year', '')}" if d.get('fiscal_year') else "N/A",
        "Status": d.get("status", "PROCESSED"),
        "Created": d.get("created_at", "")[:10] if d.get("created_at") else "",
    }
    for d in live_docs
]

# Initialize empty chat store
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

st.title("📊 FinIntel AI — Financial Document Intelligence Platform")
st.markdown("Enterprise automated extraction, 5D corporate health analysis, and grounded RAG powered by **Google Gemini**.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("📁 Upload Documents")
        st.write("Upload company annual reports or financial statements (PDF).")
        st.caption("Go to **Upload** in the left sidebar to add files.")

with col2:
    with st.container(border=True):
        st.subheader("📈 Financial Dashboard")
        st.write("Inspect 5-dimension corporate health gauges and radar charts.")
        st.caption("Go to **Dashboard** to view executive KPIs.")

with col3:
    with st.container(border=True):
        st.subheader("🤖 AI Financial Analyst")
        st.write("Query financial statements with strict citation provenance.")
        st.caption("Go to **AI Analyst** to begin conversational Q&A.")

st.divider()

st.subheader("📌 Currently Loaded Documents")

if st.session_state["document_list"]:
    doc_count = len(st.session_state["document_list"])
    st.success(f"**{doc_count}** document(s) registered in PostgreSQL.")
    st.dataframe(st.session_state["document_list"], use_container_width=True, hide_index=True)
else:
    with st.container(border=True):
        st.info("ℹ️ **No financial documents uploaded yet.**")
        st.write("The platform database is clean and ready. Upload your first annual report or 10-K filing to automatically trigger vector indexing, ratio calculation, and AI intelligence analysis.")
        if st.button("🚀 Go to Upload Page", type="primary"):
            st.switch_page("pages/2_Upload.py")