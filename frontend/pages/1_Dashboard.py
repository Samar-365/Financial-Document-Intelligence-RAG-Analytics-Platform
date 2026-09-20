import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.kpi_card import render_kpi_card
from components.health_gauge import render_health_gauge

st.set_page_config(page_title="Dashboard | FinIntel AI", layout="wide")

st.title("📊 Financial Intelligence Dashboard")

# Header Metadata & Selection Bar

processed_docs = [
    doc["Filename"] for doc in st.session_state.get("document_list", [])
    if "PROCESSED" in doc["Status"]
]

if not processed_docs:
    processed_docs = ["ABC_AR_2025.pdf"]

selected_doc = st.selectbox("Active Document Context:", options=processed_docs)

# Render Document Header Info Banner

with st.container(border=True):
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    col_h1.markdown("**Company:** ABC Ltd.")
    col_h2.markdown("**Period:** FY2025")
    col_h3.markdown("**Status:** 🟢 PROCESSED")
    col_h4.markdown(f"**Source File:** `{selected_doc}`")

st.divider()

# Financial Health Score Overview

st.subheader("🏥 Financial Health Score")

score_col1, score_col2 = st.columns([1, 2])

with score_col1:
    with st.container(border=True):
        render_health_gauge(78, "Overall Health Score")
        st.caption("Status: **Strong / Low Default Risk**")

with score_col2:
    with st.container(border=True):
        st.markdown("**Dimension Performance Scores**")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.write("📈 **Growth:** 86/100")
            st.progress(0.86)
            st.write("💰 **Profitability:** 82/100")
            st.progress(0.82)
            st.write("💧 **Liquidity:** 71/100")
            st.progress(0.71)
        with d_col2:
            st.write("⚖️ **Leverage:** 74/100")
            st.progress(0.74)
            st.write("💵 **Cash Flow:** 77/100")
            st.progress(0.77)

st.divider()

# Key Financial Performance Indicators (KPIs)

st.subheader("📌 Key Metrics Overview")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    render_kpi_card("Revenue", "₹11,450 Cr", "+12.4% YoY")
with kpi_col2:
    render_kpi_card("EBITDA", "₹2,340 Cr", "+11.4% YoY")
with kpi_col3:
    render_kpi_card("Net Income", "₹1,410 Cr", "+17.5% YoY")
with kpi_col4:
    render_kpi_card("Total Debt", "₹3,900 Cr", "-7.1% YoY", delta_color="inverse")
with kpi_col5:
    render_kpi_card("Cash Flow", "₹2,680 Cr", "+15.2% YoY")

st.divider()


#  Interactive Financial Trends

st.subheader("📈 Financial Performance Trends")

trend_data = pd.DataFrame({
    "Period": ["FY2022", "FY2023", "FY2024", "FY2025"],
    "Revenue": [8500, 9400, 10200, 11450],
    "Net Profit": [950, 1080, 1200, 1410],
    "Total Debt": [4500, 4300, 4200, 3900]
})

fig_trend = px.line(
    trend_data, 
    x="Period", 
    y=["Revenue", "Net Profit", "Total Debt"],
    markers=True,
    title="Multi-Year Performance Trends (₹ Cr)"
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()


# Risk Summary & AI Insights (2-Column Layout)

risk_col, insights_col = st.columns(2)

with risk_col:
    st.subheader("⚠️ Identified Risk Factors")
    with st.container(border=True):
        st.error("🔴 **HIGH:** Increasing interest expenses (+18% YoY)")
        st.warning("🟡 **MEDIUM:** New environmental compliance requirements")
        st.info("🔵 **LOW:** Increased domestic market competition")

with insights_col:
    st.subheader("🤖 Key AI Insights")
    with st.container(border=True):
        st.markdown(
            """
            * **Revenue Expansion:** Revenue grew by **12.4%**, driven by elevated domestic market demand.
            * **De-leveraging:** Total Debt dropped by **7.1%**, significantly strengthening balance sheet leverage.
            * **Cash Generation:** Operating cash flow improved by **15.2%** YoY.
            * **Regulatory Constraint:** Compliance milestone deadline set for **FY2027**.
            """
        )
        st.caption("📍 **Sources:** Pages 42, 87, 103, 156")