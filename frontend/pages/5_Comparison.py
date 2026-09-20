import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))

st.set_page_config(page_title="Comparison | FinIntel AI", layout="wide")

st.title("⚖️ Document Comparison")
st.caption("Compare two processed financial reports side-by-side.")

# Document Selectors

processed_docs = [
    doc["Filename"] for doc in st.session_state.get("document_list", [])
    if "PROCESSED" in doc["Status"]
]

col_a, col_b = st.columns(2)
with col_a:
    doc_a = st.selectbox("Document A (Baseline):", options=processed_docs, index=0)
with col_b:
    doc_b = st.selectbox("Document B (Comparison):", options=processed_docs, index=min(1, len(processed_docs) - 1))

if st.button("Compare Documents", type="primary"):
    st.session_state["has_compared"] = True

st.divider()

# Comparison Logic & Validation
if st.session_state.get("has_compared", False):
    if doc_a == doc_b:
        st.warning("⚠️ Please select two different documents to perform a comparison.")
    else:
        # 3. Metric Comparison Table
        st.subheader("📊 Metric Comparison")
        
        
        metrics_data = [
            {"Metric": "Revenue", "FY2024": "₹10,200 Cr", "FY2025": "₹11,450 Cr", "Change": "+12.25%", "Trend": "📈"},
            {"Metric": "EBITDA", "FY2024": "₹2,100 Cr", "FY2025": "₹2,340 Cr", "Change": "+11.43%", "Trend": "📈"},
            {"Metric": "Net Income", "FY2024": "₹1,200 Cr", "FY2025": "₹1,410 Cr", "Change": "+17.50%", "Trend": "📈"},
            {"Metric": "Total Debt", "FY2024": "₹4,200 Cr", "FY2025": "₹3,900 Cr", "Change": "-7.14%", "Trend": "📉"},
            {"Metric": "Cash & Equivalents", "FY2024": "₹1,800 Cr", "FY2025": "₹2,150 Cr", "Change": "+19.44%", "Trend": "📈"},
        ]
        
        st.dataframe(
            pd.DataFrame(metrics_data),
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        
        
        #  Risk Profile Changes
        
        st.subheader("⚠️ Risk Profile Changes")
        
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            with st.container(border=True):
                st.markdown("🆕 **New Risks**")
                st.write("• Data privacy compliance requirements")
                st.write("• New environmental regulatory deadlines")

        with risk_col2:
            with st.container(border=True):
                st.markdown("🔄 **Changed Risk Levels**")
                st.write("• Debt exposure: **High ➔ Medium**")
                st.write("• Supply chain constraints: **Medium ➔ Low**")

        with risk_col3:
            with st.container(border=True):
                st.markdown("❌ **Removed Risks**")
                st.write("• Foreign exchange volatility (Hedging active)")

        st.divider()
        
        
        #5. AI Comparison Summary Narrative
        
        st.subheader("🤖 AI Comparison Summary")
        
        with st.container(border=True):
            st.markdown(
                f"""
                ABC Ltd. demonstrated strong overall financial performance when comparing **{doc_a}** to **{doc_b}**:
                
                * **Top-line Growth:** Revenue increased by **12.25%**, expanding from ₹10,200 Cr to ₹11,450 Cr.
                * **Margin Expansion:** Net income outpaced revenue growth at **17.50%**, indicating improving operational efficiency and profitability.
                * **Balance Sheet De-risking:** Total debt reduced by **7.14%** alongside a **19.44%** build-up in cash reserves, shifting total leverage risk from High to Medium.
                """
            )
            st.caption("📍 **Sources:** AR 2024 (pp. 87, 103) | AR 2025 (pp. 87, 103)")