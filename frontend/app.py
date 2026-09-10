"""Main Streamlit Application Entrypoint."""

import streamlit as st

st.set_page_config(
    page_title="Financial Document Intelligence & RAG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Financial Document Intelligence & RAG Analytics Platform")
st.markdown(
    """
Welcome to the Financial Document Intelligence Platform. 
Please select an analytical module from the left sidebar navigation:
- **1. Executive Dashboard**: High-level KPIs, 5D corporate health scores, and radar charts.
- **2. Document Ingestion**: Upload annual reports, 10-K filings, and balance sheets.
- **3. Financial Analysis**: 12 core financial metrics and 8 deterministic ratio indicators.
- **4. Document Q&A**: Grounded conversational AI analyst with page-verified citations.
- **5. Comparative Analytics**: Multi-period YoY and QoQ variance and financial delta analysis.
"""
)
