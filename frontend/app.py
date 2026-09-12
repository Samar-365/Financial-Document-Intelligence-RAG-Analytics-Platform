import streamlit as st

st.set_page_config(
    page_title="FinIntel AI | Financial Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# Initialize shared document state globally if not already set
if "document_list" not in st.session_state:
    st.session_state["document_list"] = [
        {"Filename": "ABC_AR_2025.pdf", "Company": "ABC Ltd.", "Year": "FY2025", "Status": "PROCESSED"},
        {"Filename": "ABC_AR_2024.pdf", "Company": "ABC Ltd.", "Year": "FY2024", "Status": "PROCESSED"},
    ]
    
# Initialize chat messages store globally  
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "user", 
            "content": "What was the company's revenue in FY2025?"
        },
        {
            "role": "assistant",
            "content": "ABC Ltd reported total revenue of **₹11,450 crore** for FY2025, representing a year-over-year increase of 12.25% compared to ₹10,200 crore in FY2024.",
            "sources": [
                {"doc": "ABC_AR_2025.pdf", "page": 87, "section": "Consolidated Statement of Profit & Loss", "text": "Total Revenue from Operations stood at ₹11,450 Cr for the financial year ending March 31, 2025."},
                {"doc": "ABC_AR_2025.pdf", "page": 42, "section": "Management Discussion & Analysis", "text": "Revenue growth was primarily driven by strong domestic sales performance across core product lines."}
            ],
            "metrics": {"time": "2.1s", "chunks": 5}
        }
    ]

st.title("📊 FinIntel AI — Financial Document Intelligence Platform")
st.markdown("Welcome! Use the sidebar navigation menu on the left to switch between modules.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📁 Document Management")
        st.write("Upload new financial statements or annual reports (PDFs).")
        st.caption("Use **Upload** in the left sidebar to add files.")

with col2:
    with st.container(border=True):
        st.subheader("📑 Financial Statement Analysis")
        st.write("View income statements, balance sheets, and key ratios for uploaded documents.")
        st.caption("Use **Analysis** in the left sidebar to view analytics.")

st.divider()

st.subheader("📌 Currently Loaded Documents")
doc_count = len(st.session_state["document_list"])
st.info(f"**{doc_count}** document(s) available in current session.")

st.dataframe(st.session_state["document_list"], use_container_width=True, hide_index=True)