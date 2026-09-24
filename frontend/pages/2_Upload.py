import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from utils.api_client import client

st.set_page_config(page_title="Upload | FinIntel AI", layout="wide")

# Apply Pitch Dark & Wine Red styling
apply_theme()

render_page_header(
    title="Document & Dataset Ingestion",
    subtitle="Upload corporate filings and spreadsheet datasets across PDF, CSV, and Excel (.xlsx) formats for vector indexing and financial intelligence.",
    icon_name="upload",
)

# 1. Upload Section Container
with st.container(border=True):
    icon_file = get_icon("file-text", color="#E63946", size=20)
    render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    <span>{icon_file}</span>
    <span style="font-weight: 700; font-size: 1.1rem; color: #FFFFFF;">Upload New Filing or Spreadsheet</span>
</div>
""")
    
    uploaded_file = st.file_uploader(
        label="Select a financial filing (PDF) or tabular dataset (CSV, XLSX)",
        type=["pdf", "csv", "xlsx", "xls"],
        help="Supports Annual Reports, 10-K/10-Q filings, CSV balance sheets, and Excel workbooks up to 50MB."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        company_name = st.text_input("Company Name (Optional)", placeholder="e.g. Apple Inc. (Auto-detected if blank)")
    with col2:
        financial_year = st.text_input("Fiscal Year (Optional)", placeholder="e.g. 2025 (Auto-detected if blank)")
    with col3:
        doc_type = st.selectbox(
            "Filing Type",
            options=["Annual Report / 10-K", "Quarterly Report (Q1-Q4)", "CSV Tabular Dataset", "Excel Workbook (.xlsx)", "Other"]
        )

    if st.button("Ingest & Process Document", type="primary"):
        if uploaded_file is None:
            st.error("Please select a valid PDF, CSV, or Excel file first!")
        else:
            with st.spinner(f"Ingesting '{uploaded_file.name}' into vector database pipeline..."):
                file_bytes = uploaded_file.read()
                import re
                fy_num = None
                if financial_year:
                    m_fy = re.search(r"(\d{4})", financial_year)
                    if m_fy:
                        fy_num = int(m_fy.group(1))

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
                    st.success(f"File '{uploaded_file.name}' uploaded successfully! Processing initiated.")
                    st.rerun()

st.divider()

# 2. Uploaded docs table
icon_db = get_icon("database", color="#E63946", size=20)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
    <span>{icon_db}</span>
    <span style="font-weight: 700; font-size: 1.15rem; color: #FFFFFF;">Indexed Filing Inventory</span>
</div>
""")

# Fetch from live backend API
live_docs = client.get_documents()

if live_docs:
    df_docs = pd.DataFrame(live_docs)
    display_cols = [c for c in ["id", "filename", "company_name", "fiscal_year", "fiscal_period", "status", "created_at"] if c in df_docs.columns]
    st.dataframe(df_docs[display_cols] if display_cols else df_docs, use_container_width=True, hide_index=True)

    # Document Deletion Utility
    with st.expander("Delete Filing Record"):
        del_options = {f"{d.get('filename')} (ID: {d.get('id')[:8]}...)": d.get('id') for d in live_docs}
        selected_del = st.selectbox("Select document to purge:", options=list(del_options.keys()))
        if st.button("Delete Selected Document", type="secondary"):
            target_id = del_options[selected_del]
            if client.delete_document(target_id):
                st.success("Document purged from database.")
                st.rerun()
else:
    with st.container(border=True):
        st.info("No documents currently uploaded. Use the form above to upload your first financial filing or dataset.")