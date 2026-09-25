import streamlit as st
import pandas as pd
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from utils.api_client import client
from utils.workspace_state import render_workspace_sidebar_branding, set_active_doc_id

st.set_page_config(
    page_title="FININTEL — Document Ingestion",
    page_icon="frontend/assets/finintel_logo.png",
    layout="wide"
)

# Apply Pitch Dark & Wine Red styling
apply_theme()
render_workspace_sidebar_branding()

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
        financial_year = st.text_input("Fiscal Year (Optional)", placeholder="e.g. 2026 (Auto-detected if blank)")
    with col3:
        doc_type = st.selectbox(
            "Filing Type",
            options=["Annual Report / 10-K", "Quarterly Report (Q1-Q4)", "CSV Tabular Dataset", "Excel Workbook (.xlsx)", "Other"]
        )

    upload_btn = st.button("Ingest & Process Document", type="primary")

    if upload_btn:
        if uploaded_file is None:
            st.error("Please select a valid PDF, CSV, or Excel file first!")
        else:
            # Multi-stage progress tracking
            progress_bar = st.progress(0, text="Uploading document...")
            time.sleep(0.2)
            progress_bar.progress(35, text="Uploading document to secure repository...")
            
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

            progress_bar.progress(65, text="Processing financial document & vector indexing...")
            
            result = client.upload_document(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                company_name=company_name or None,
                fiscal_year=fy_num,
                fiscal_period=f_period,
            )
            progress_bar.progress(100, text="Complete")
            time.sleep(0.2)
            progress_bar.empty()

            if result.get("is_duplicate"):
                # Clean amber warning for duplicates without raw JSON
                render_html("""
<div style="
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.45);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 16px 0;
">
    <div style="display: flex; align-items: center; gap: 10px; color: #F59E0B; font-weight: 700; font-size: 1.05rem;">
        <span>⚠</span>
        <span>Document already exists</span>
    </div>
    <div style="color: #CBD5E1; font-size: 0.92rem; margin-top: 6px; line-height: 1.5;">
        This document has already been uploaded and processed. You can select it from your document workspace instead.
    </div>
</div>
""")
            elif result.get("success"):
                # Clean green success message
                fn_clean = uploaded_file.name
                render_html(f"""
<div style="
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.45);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 16px 0;
">
    <div style="display: flex; align-items: center; gap: 10px; color: #4ADE80; font-weight: 700; font-size: 1.05rem;">
        <span>✓</span>
        <span>Document uploaded successfully</span>
    </div>
    <div style="color: #CBD5E1; font-size: 0.92rem; margin-top: 6px; line-height: 1.5;">
        <b>"{fn_clean}"</b> has been added to your workspace.
    </div>
</div>
""")
                new_id = result.get("data", {}).get("document_id")
                if new_id:
                    set_active_doc_id(str(new_id))

                if st.button("Open in Executive Dashboard →", type="primary"):
                    st.switch_page("pages/1_Dashboard.py")
            else:
                # Clean friendly failure message
                err_text = result.get("user_message", "Something went wrong while uploading the document. Please try again.")
                st.error(err_text)

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
    
    # Format display columns cleanly
    rename_cols = {
        "company_name": "Company",
        "fiscal_year": "Fiscal Year",
        "fiscal_period": "Period",
        "filename": "Filing Document",
        "status": "Index Status",
        "created_at": "Ingestion Date",
    }
    cols_to_use = [c for c in ["company_name", "fiscal_year", "fiscal_period", "filename", "status", "created_at"] if c in df_docs.columns]
    df_clean = df_docs[cols_to_use].rename(columns=rename_cols)
    
    # Clean up Year display to avoid commas like 2,026
    if "Fiscal Year" in df_clean.columns:
        df_clean["Fiscal Year"] = df_clean["Fiscal Year"].apply(lambda y: f"{int(y)}" if pd.notna(y) else "")

    st.dataframe(df_clean, use_container_width=True, hide_index=True)

    # Document Deletion Utility
    with st.expander("Delete Filing Record"):
        del_options = {f"{d.get('company_name', 'Filing')} — {d.get('filename')}": str(d.get('id')) for d in live_docs}
        selected_del = st.selectbox("Select document to purge:", options=list(del_options.keys()))
        if st.button("Delete Selected Document", type="secondary"):
            target_id = del_options[selected_del]
            if client.delete_document(target_id):
                st.success("Document purged from database.")
                st.rerun()
else:
    with st.container(border=True):
        st.info("No documents currently uploaded. Use the form above to upload your first financial filing or dataset.")