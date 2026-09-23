import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.kpi_card import render_kpi_card
from utils.api_client import client

st.set_page_config(page_title="Financial Analysis | FinIntel AI", layout="wide")

st.title("📊 Financial Statement Analysis")

# Top Bar Selection - Fetch live documents
live_docs = client.get_documents() or []

if not live_docs:
    st.info("ℹ️ **No documents available in the database.**")
    st.write("Please upload a financial report (PDF) via the **Upload** page to generate dynamic financial statement analytics.")
    if st.button("🚀 Go to Upload Page", type="primary"):
        st.switch_page("pages/2_Upload.py")
    st.stop()

doc_options = {}
for d in live_docs:
    doc_id = d.get("id", "")
    filename = d.get("filename", "Document")
    year = f"FY{d.get('fiscal_year', '')}" if d.get('fiscal_year') else ""
    label = f"{filename} {year} (ID: {doc_id[:8]}...)"
    doc_options[label] = d

selected_label = st.selectbox("Select Analyzed Document:", options=list(doc_options.keys()))
selected_doc_info = doc_options[selected_label]
selected_doc_id = selected_doc_info.get("id")

st.caption(f"Showing extracted metrics for: **{selected_doc_info.get('filename')}** (ID: `{selected_doc_id}`)")
st.divider()

# Fetch live metrics & ratios from API
raw_metrics = client.get_financial_metrics(selected_doc_id) if selected_doc_id else []
ratios_resp = client.get_financial_ratios(selected_doc_id) if selected_doc_id else None

# Helper to look up metric value by common names without fake mocks
def find_metric(name_patterns):
    for m in raw_metrics:
        m_name = m.get("metric_name", "").lower()
        for p in name_patterns:
            if p.lower() in m_name:
                val = m.get("value")
                unit = m.get("unit", "Cr")
                conf = f"{int(m.get('confidence', 1.0) * 100)}%"
                if val is not None:
                    formatted_val = f"₹{val:,.1f} {unit}" if unit else f"₹{val:,.1f}"
                    return formatted_val, conf, "Extracted"
    return "N/A", "—", "Not Detected"

# 1. Income Statement Cards
st.subheader("📋 Income Statement Metrics")
inc_row1_col1, inc_row1_col2, inc_row1_col3, inc_row1_col4 = st.columns(4)

rev_val, rev_conf, rev_sub = find_metric(["revenue", "sales", "turnover"])
gp_val, gp_conf, gp_sub = find_metric(["gross profit", "gross margin"])
ebitda_val, ebitda_conf, ebitda_sub = find_metric(["ebitda"])
op_val, op_conf, op_sub = find_metric(["operating income", "ebit", "operating profit"])

with inc_row1_col1:
    render_kpi_card("Revenue", rev_val, rev_sub, confidence=rev_conf)
with inc_row1_col2:
    render_kpi_card("Gross Profit", gp_val, gp_sub, confidence=gp_conf)
with inc_row1_col3:
    render_kpi_card("EBITDA", ebitda_val, ebitda_sub, confidence=ebitda_conf)
with inc_row1_col4:
    render_kpi_card("Operating Income", op_val, op_sub, confidence=op_conf)

inc_row2_col1, inc_row2_col2, _, _ = st.columns(4)
net_val, net_conf, net_sub = find_metric(["net income", "pat", "profit after tax"])
eps_val, eps_conf, eps_sub = find_metric(["eps", "earnings per share"])

with inc_row2_col1:
    render_kpi_card("Net Income", net_val, net_sub, confidence=net_conf)
with inc_row2_col2:
    render_kpi_card("EPS", eps_val, eps_sub, confidence=eps_conf)

st.divider()

# 2. Balance Sheet Cards
st.subheader("🏛️ Balance Sheet Metrics")
bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)

assets_val, assets_conf, assets_sub = find_metric(["total assets", "assets"])
liab_val, liab_conf, liab_sub = find_metric(["total liabilities", "liabilities"])
debt_val, debt_conf, debt_sub = find_metric(["total debt", "borrowings", "debt"])
cash_val, cash_conf, cash_sub = find_metric(["cash", "cash & equivalents", "cash equivalents"])

with bal_col1:
    render_kpi_card("Total Assets", assets_val, assets_sub, confidence=assets_conf)
with bal_col2:
    render_kpi_card("Total Liabilities", liab_val, liab_sub, confidence=liab_conf)
with bal_col3:
    render_kpi_card("Total Debt", debt_val, debt_sub, confidence=debt_conf)
with bal_col4:
    render_kpi_card("Cash & Equivalents", cash_val, cash_sub, confidence=cash_conf)

st.divider()

# 3. Cash Flow Cards
st.subheader("💵 Cash Flow Metrics")
cf_col1, cf_col2, _, _ = st.columns(4)

ocf_val, ocf_conf, ocf_sub = find_metric(["operating cash flow", "cash flow from operations", "cfo"])
fcf_val, fcf_conf, fcf_sub = find_metric(["free cash flow"])

with cf_col1:
    render_kpi_card("Operating Cash Flow", ocf_val, ocf_sub, confidence=ocf_conf)
with cf_col2:
    render_kpi_card("Free Cash Flow", fcf_val, fcf_sub, confidence=fcf_conf)

st.divider()

# 4. Computed Ratios
st.subheader("📐 Key Financial Ratios")

if ratios_resp:
    r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns(6)
    with r_col1:
        opm = ratios_resp.get("opm")
        st.metric("Operating Margin", f"{opm:.2f}%" if opm is not None else "N/A")
    with r_col2:
        npm = ratios_resp.get("npm")
        st.metric("Net Margin", f"{npm:.2f}%" if npm is not None else "N/A")
    with r_col3:
        roe = ratios_resp.get("roe")
        st.metric("ROE", f"{roe:.2f}%" if roe is not None else "N/A")
    with r_col4:
        cr = ratios_resp.get("current_ratio")
        st.metric("Current Ratio", f"{cr:.2f}x" if cr is not None else "N/A")
    with r_col5:
        dte = ratios_resp.get("debt_to_equity")
        st.metric("Debt-to-Equity", f"{dte:.2f}x" if dte is not None else "N/A")
    with r_col6:
        ic = ratios_resp.get("interest_coverage")
        st.metric("Interest Coverage", f"{ic:.2f}x" if ic is not None else "N/A")
else:
    st.info("Ratios will be computed automatically once financial statements are extracted.")

st.divider()

# 5. Raw Extracted Line Items Table
st.subheader("📑 All Extracted Metric Line Items")

if raw_metrics:
    df_metrics = pd.DataFrame(raw_metrics)
    display_cols = [c for c in ["metric_name", "value", "unit", "fiscal_year", "confidence", "source_page"] if c in df_metrics.columns]
    st.dataframe(df_metrics[display_cols] if display_cols else df_metrics, use_container_width=True, hide_index=True)
else:
    st.write("No specific line items extracted for this document yet.")