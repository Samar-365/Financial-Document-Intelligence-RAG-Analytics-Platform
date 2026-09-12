import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.kpi_card import render_kpi_card

st.set_page_config(page_title="Financial Analysis | FinIntel AI", layout="wide")

st.title(" Financial Statement Analysis")

# Top Bar Selection
processed_docs = [
    doc["Filename"] for doc in st.session_state.get("document_list", [])
    if "PROCESSED" in doc["Status"]
]
if not processed_docs:
    processed_docs = ["ABC_AR_2025.pdf", "ABC_AR_2024.pdf"]

selected_doc = st.selectbox("Select Analyzed Document:", options=processed_docs)
st.caption(f"Showing extracted metrics for: **{selected_doc}**")
st.divider()

# 1. Income Statement Cards
st.subheader(" Income Statement Metrics")
inc_row1_col1, inc_row1_col2, inc_row1_col3, inc_row1_col4 = st.columns(4)

with inc_row1_col1:
    render_kpi_card("Revenue", "₹11,450 Cr", "+12.4% YoY", confidence="99%")
with inc_row1_col2:
    render_kpi_card("Gross Profit", "₹4,580 Cr", "+14.1% YoY", confidence="97%")
with inc_row1_col3:
    render_kpi_card("EBITDA", "₹2,340 Cr", "+11.4% YoY", confidence="95%")
with inc_row1_col4:
    render_kpi_card("Operating Income", "₹1,890 Cr", "+10.2% YoY", confidence="96%")

inc_row2_col1, inc_row2_col2, _, _ = st.columns(4)
with inc_row2_col1:
    render_kpi_card("Net Income", "₹1,410 Cr", "+17.5% YoY", confidence="98%")
with inc_row2_col2:
    render_kpi_card("EPS", "₹28.20", "+18.3% YoY", confidence="94%")

st.divider()

# 2. Balance Sheet Cards
st.subheader(" Balance Sheet Metrics")
bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)

with bal_col1:
    render_kpi_card("Total Assets", "₹18,500 Cr", "+8.5% YoY", confidence="99%")
with bal_col2:
    render_kpi_card("Total Liabilities", "₹9,800 Cr", "+3.1% YoY", confidence="96%")
with bal_col3:
    render_kpi_card("Total Debt", "₹3,900 Cr", "-7.1% YoY", delta_color="inverse", confidence="98%")
with bal_col4:
    render_kpi_card("Cash & Equivalents", "₹2,150 Cr", "+19.4% YoY", confidence="97%")

st.divider()

# 3. Cash Flow Cards
st.subheader(" Cash Flow Metrics")
cf_col1, cf_col2, _, _ = st.columns(4)

with cf_col1:
    render_kpi_card("Operating Cash Flow", "₹2,680 Cr", "+15.2% YoY", confidence="98%")
with cf_col2:
    render_kpi_card("Free Cash Flow", "₹1,850 Cr", "+22.1% YoY", confidence="93%")

st.divider()

# 4. Ratios Table
st.subheader(" Financial Ratios")
ratio_data = [
    {"Ratio": "Revenue Growth", "Value": "12.25%", "Interpretation": "Strong growth"},
    {"Ratio": "Profit Margin", "Value": "12.31%", "Interpretation": "Healthy profitability"},
    {"Ratio": "EBITDA Margin", "Value": "20.44%", "Interpretation": "Good operating profit"},
    {"Ratio": "Current Ratio", "Value": "1.65x", "Interpretation": "Adequate liquidity"},
    {"Ratio": "Debt-to-Equity", "Value": "0.45x", "Interpretation": "Conservative leverage"},
    {"Ratio": "Return on Assets", "Value": "7.62%", "Interpretation": "Efficient asset use"},
    {"Ratio": "Return on Equity", "Value": "16.21%", "Interpretation": "Good shareholder return"},
    {"Ratio": "OCF Ratio", "Value": "1.12x", "Interpretation": "Strong cash coverage"}
]
st.dataframe(pd.DataFrame(ratio_data), use_container_width=True, hide_index=True)

st.divider()

# 5. Trend Charts
st.subheader(" Trend Charts")
trend_data = pd.DataFrame({
    "Period": ["FY2022", "FY2023", "FY2024", "FY2025"],
    "Revenue": [8500, 9400, 10200, 11450],
    "Profit Margin (%)": [10.8, 11.2, 11.8, 12.31],
    "Total Debt": [4500, 4300, 4200, 3900],
    "Cash": [1200, 1500, 1800, 2150]
})

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig_rev = px.bar(trend_data, x="Period", y="Revenue", title="Revenue by Period (₹ Cr)", text_auto=True)
    st.plotly_chart(fig_rev, use_container_width=True)

with chart_col2:
    fig_margin = px.line(trend_data, x="Period", y="Profit Margin (%)", title="Profit Margins Over Time", markers=True)
    st.plotly_chart(fig_margin, use_container_width=True)

fig_debt_cash = px.bar(trend_data, x="Period", y=["Total Debt", "Cash"], barmode="group", title="Debt vs Cash Comparison (₹ Cr)")
st.plotly_chart(fig_debt_cash, use_container_width=True)