import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from components.kpi_card import render_kpi_card
from components.advanced_charts import render_balance_sheet_composition, render_margin_comparison
from utils.api_client import client

st.set_page_config(page_title="Financial Analysis | FinIntel AI", layout="wide")

# Apply Pitch Dark & Wine Red styling
apply_theme()

render_page_header(
    title="Financial Statement Analysis",
    subtitle="Line-item statement extraction, balance sheet structure diagnostics, and audited accounting metrics.",
    icon_name="file-text",
)

# Top Bar Selection - Fetch live documents
live_docs = client.get_documents() or []

if not live_docs:
    with st.container(border=True):
        icon_alert = get_icon("alert-triangle", color="#E63946", size=24)
        render_html(f"""
<div style="display: flex; gap: 12px; align-items: flex-start; padding: 8px;">
    <div>{icon_alert}</div>
    <div>
        <b style="color: #FFFFFF; font-size: 1rem;">No financial filings available in the database.</b>
        <p style="margin: 4px 0 10px 0; color: #94A3B8; font-size: 0.9rem;">
            Upload an Annual Report, 10-K, or CSV/Excel spreadsheet to generate statement analytics.
        </p>
    </div>
</div>
""")
        if st.button("Upload Filings", type="primary"):
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

st.markdown(
    f"<div style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;'>Active Document Context: <b style='color: #FFFFFF;'>{selected_doc_info.get('filename')}</b> (ID: <code style='color: #E63946;'>{selected_doc_id}</code>)</div>",
    unsafe_allow_html=True,
)
st.divider()

# Fetch live metrics & ratios from API
raw_metrics = client.get_financial_metrics(selected_doc_id) if selected_doc_id else []
ratios_resp = client.get_financial_ratios(selected_doc_id) if selected_doc_id else None

metrics_map = {m.get("metric_name", ""): float(m.get("value")) for m in raw_metrics if m.get("value") is not None}
currency_sym = "$"
for m in raw_metrics:
    if "inr" in m.get("unit", "").lower():
        currency_sym = "₹"

def find_metric(name_patterns):
    for m in raw_metrics:
        m_name = m.get("metric_name", "").lower()
        for p in name_patterns:
            if p.lower() in m_name:
                val = m.get("value")
                unit = m.get("unit", "M")
                conf = f"{int(m.get('confidence', 1.0) * 100)}%"
                if val is not None:
                    return f"{currency_sym}{val:,.1f} {unit}", conf, "Detected"
    return "N/A", "—", "Not Detected"

# 1. Income Statement Cards
icon_inc = get_icon("dollar-sign", color="#E63946", size=18)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_inc}</span><span style='font-weight: 700; color: #FFFFFF;'>Income Statement Metrics</span></div>", unsafe_allow_html=True)

inc_row1_col1, inc_row1_col2, inc_row1_col3, inc_row1_col4 = st.columns(4)

rev_val, rev_conf, rev_sub = find_metric(["revenue", "sales", "turnover"])
gp_val, gp_conf, gp_sub = find_metric(["gross profit", "gross margin"])
ebitda_val, ebitda_conf, ebitda_sub = find_metric(["ebitda"])
op_val, op_conf, op_sub = find_metric(["operating income", "ebit", "operating profit"])

with inc_row1_col1:
    render_kpi_card("Revenue", rev_val, rev_sub, confidence=rev_conf, icon_name="dollar-sign")
with inc_row1_col2:
    render_kpi_card("Gross Profit / Margin", gp_val, gp_sub, confidence=gp_conf, icon_name="trending-up")
with inc_row1_col3:
    render_kpi_card("EBITDA", ebitda_val, ebitda_sub, confidence=ebitda_conf, icon_name="activity")
with inc_row1_col4:
    render_kpi_card("Operating Income", op_val, op_sub, confidence=op_conf, icon_name="layers")

inc_row2_col1, inc_row2_col2, _, _ = st.columns(4)
net_val, net_conf, net_sub = find_metric(["net income", "pat", "profit after tax"])
eps_val, eps_conf, eps_sub = find_metric(["eps", "earnings per share"])

with inc_row2_col1:
    render_kpi_card("Net Income", net_val, net_sub, confidence=net_conf, icon_name="trending-up")
with inc_row2_col2:
    render_kpi_card("Diluted EPS", eps_val, eps_sub, confidence=eps_conf, icon_name="pie-chart")

st.divider()

# 2. Balance Sheet Cards
icon_bal = get_icon("pie-chart", color="#E63946", size=18)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_bal}</span><span style='font-weight: 700; color: #FFFFFF;'>Balance Sheet Metrics</span></div>", unsafe_allow_html=True)

bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)

assets_val, assets_conf, assets_sub = find_metric(["total assets", "assets"])
liab_val, liab_conf, liab_sub = find_metric(["total liabilities", "liabilities"])
debt_val, debt_conf, debt_sub = find_metric(["total debt", "borrowings", "debt"])
cash_val, cash_conf, cash_sub = find_metric(["cash", "cash & equivalents", "cash equivalents"])

with bal_col1:
    render_kpi_card("Total Assets", assets_val, assets_sub, confidence=assets_conf, icon_name="layers")
with bal_col2:
    render_kpi_card("Total Liabilities", liab_val, liab_sub, confidence=liab_conf, icon_name="layers")
with bal_col3:
    render_kpi_card("Total Debt", debt_val, debt_sub, confidence=debt_conf, icon_name="alert-triangle")
with bal_col4:
    render_kpi_card("Cash & Equivalents", cash_val, cash_sub, confidence=cash_conf, icon_name="dollar-sign")

# Balance Sheet Composition Visualizer
with st.container(border=True):
    render_balance_sheet_composition(metrics_map)

st.divider()

# 3. Cash Flow Cards
icon_cf = get_icon("activity", color="#E63946", size=18)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_cf}</span><span style='font-weight: 700; color: #FFFFFF;'>Cash Flow & Solvency Metrics</span></div>", unsafe_allow_html=True)

cf_col1, cf_col2, _, _ = st.columns(4)
ocf_val, ocf_conf, ocf_sub = find_metric(["operating cash flow", "cash flow from operations", "cfo", "cash generated by operating activities"])
fcf_val, fcf_conf, fcf_sub = find_metric(["free cash flow"])

with cf_col1:
    render_kpi_card("Operating Cash Flow", ocf_val, ocf_sub, confidence=ocf_conf, icon_name="trending-up")
with cf_col2:
    render_kpi_card("Free Cash Flow", fcf_val, fcf_sub, confidence=fcf_conf, icon_name="dollar-sign")

st.divider()

# 4. Computed Ratios & Margins
icon_ratios = get_icon("trending-up", color="#E63946", size=18)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_ratios}</span><span style='font-weight: 700; color: #FFFFFF;'>Key Financial Ratios & Margins</span></div>", unsafe_allow_html=True)

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

    # Margin comparison visualizer
    with st.container(border=True):
        render_margin_comparison(metrics_map, ratios_resp)
else:
    st.info("Ratios will be computed automatically once financial statements are extracted.")

st.divider()

# 5. Raw Extracted Line Items Table
icon_table = get_icon("database", color="#E63946", size=18)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_table}</span><span style='font-weight: 700; color: #FFFFFF;'>All Extracted Metric Line Items</span></div>", unsafe_allow_html=True)

if raw_metrics:
    df_metrics = pd.DataFrame(raw_metrics)
    display_cols = [c for c in ["metric_name", "value", "unit", "fiscal_year", "fiscal_period", "confidence"] if c in df_metrics.columns]
    st.dataframe(df_metrics[display_cols] if display_cols else df_metrics, use_container_width=True, hide_index=True)
else:
    st.write("No specific line items extracted for this document yet.")