import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload | FinIntel AI", layout="wide")

st.title("📁 Document Management")
st.write("Upload financial documents (PDFs) for analysis.")

# 1. Upload Section Container
with st.container(border=True):
    st.subheader("Upload New Document")
    
    uploaded_file = st.file_uploader(
        label="Choose a PDF file",
        type=["pdf"],
        help="Upload annual reports, quarterly filings, or financial statements."
    )

    # Metadata input fields
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

    # Upload & Process Action Button
    if st.button("Upload & Process", type="primary"):
        if uploaded_file is None:
            st.error("Please select a PDF file first!")
        else:  # further logic
            st.success(f"File '{uploaded_file.name}' submitted for processing!  /n  option selected = '{doc_type}'")
            company = company_name if company_name.strip() else "Unknown Corp"
            year = financial_year if financial_year.strip() else "N/A"

            # Construct new document item with default "PROCESSING" status
            new_doc = {
                "Filename": uploaded_file.name,
                "Company": company,
                "Year": year,
                "Status": "PROCESSING"
            }
            st.session_state["document_list"].append(new_doc)
            
            
st.divider()

# Uploaded docs table

st.subheader("Uploaded Documents")

if "document_list" not in st.session_state:
    st.session_state["document_list"] = [
        {"Filename": "ABC_AR_2024.pdf", "Company": "ABC Ltd.", "Year": "FY2025", "Status": "PROCESSED"},
        {"Filename": "ABC_AR_2025.pdf", "Company": "ABC Ltd.", "Year": "FY2024", "Status": "PROCESSING"},
        {"Filename": "XYZ_Q3_2025.pdf", "Company": "XYZ Corp", "Year": "Q3 '25", "Status": "PROCESSING"},
    ]
    
df_docs = pd.DataFrame(st.session_state["document_list"])

st.dataframe(
    df_docs,
    use_container_width=True,
    hide_index=True
)   