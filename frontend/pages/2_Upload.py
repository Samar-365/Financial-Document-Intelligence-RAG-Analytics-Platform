import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.api_client import client

st.set_page_config(page_title="Upload | FinIntel AI", layout="wide")

st.title("📁 Document Management")
st.write("Upload financial documents (PDFs) for automated ingestion, analytics, and vector indexing.")

# 1. Upload Section Container
with st.container(border=True):
    st.subheader("Upload New Document")
    
    uploaded_file = st.file_uploader(
        label="Choose a PDF file",
        type=["pdf"],
        help="Upload annual reports, quarterly filings, or financial statements."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. ABC Ltd.")
    with col2:
        financial_year = st.text_input("Financial Year", placeholder="e.g. FY2025")
    with col3:
        doc_type = st.selectbox(
            "Document Type",
            options=["Annual Report", "Quarterly Report (Q1-Q4)", "Investor Presentation", "Other"]
        )

    if st.button("Upload & Process", type="primary"):
        if uploaded_file is None:
            st.error("Please select a PDF file first!")
        else:
            with st.spinner(f"Uploading '{uploaded_file.name}' to backend pipeline..."):
                file_bytes = uploaded_file.read()
                # Parse numeric year if user typed "FY2025" or "2025"
                import re
                fy_num = None
                if financial_year:
                    m_fy = re.search(r"(\d{4})", financial_year)
                    if m_fy:
                        fy_num = int(m_fy.group(1))

                # Determine period from doc_type
                f_period = "FY"
                if "Q1" in doc_type:
                    f_period = "Q1"
                elif "Q2" in doc_type:
                    f_period = "Q2"
                elif "Q3" in doc_type:
                    f_period = "Q3"
                elif "Q4" in doc_type:
                    f_period = "Q4"

                result = client.upload_document(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    company_name=company_name or None,
                    fiscal_year=fy_num,
                    fiscal_period=f_period,
                )
                if result:
                    st.success(f"✓ File '{uploaded_file.name}' uploaded successfully! Status: {result.get('status')}")
                    st.info("Document queued for background parsing, chunking, and financial metrics extraction.")
                    st.rerun()

st.divider()

# 2. Uploaded docs table
st.subheader("Registered Documents")

# Fetch from live backend API
live_docs = client.get_documents()

if live_docs:
    df_docs = pd.DataFrame(live_docs)
    display_cols = [c for c in ["id", "filename", "status", "page_count", "created_at"] if c in df_docs.columns]
    st.dataframe(df_docs[display_cols] if display_cols else df_docs, use_container_width=True, hide_index=True)
else:
    st.info("No documents currently uploaded. Use the form above to upload your first financial filing.")