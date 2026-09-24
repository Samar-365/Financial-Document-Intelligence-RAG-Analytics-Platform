import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from components.kpi_card import render_kpi_card
from components.health_gauge import render_health_gauge
from components.radar_chart import render_radar_chart
from components.advanced_charts import render_revenue_waterfall, render_margin_comparison, render_balance_sheet_composition
from utils.api_client import client

st.set_page_config(page_title="Dashboard | FinIntel AI", layout="wide")

# Apply Pitch Dark & Wine Red styling
apply_theme()

render_page_header(
    title="Executive Financial Dashboard",
    subtitle="Continuous extraction, 5-dimension corporate health monitoring, and interactive financial performance bridges.",
    icon_name="dashboard",
)

# 1. Header Metadata & Active Document Selection
live_docs = client.get_documents() or []

if not live_docs:
    with st.container(border=True):
        icon_alert = get_icon("alert-triangle", color="#E63946", size=26)
        render_html(f"""
<div style="display: flex; gap: 14px; align-items: flex-start; padding: 10px;">
    <div>{icon_alert}</div>
    <div>
        <b style="color: #FFFFFF; font-size: 1.05rem;">No documents available in PostgreSQL database.</b>
        <p style="margin: 6px 0 12px 0; color: #94A3B8; font-size: 0.9rem;">
            The workspace is clean. Upload an Annual Report, 10-K, CSV dataset, or Excel sheet (.xlsx) to view executive financial intelligence.
        </p>
    </div>
</div>
""")
        if st.button("Upload Filings", type="primary"):
            st.switch_page("pages/2_Upload.py")
    st.stop()

# Build options dictionary from real documents
doc_options = {}
for d in live_docs:
    doc_id = d.get("id", "")
    filename = d.get("filename", "Document")
    year = f"FY{d.get('fiscal_year', '')}" if d.get('fiscal_year') else ""
    label = f"{filename} {year} (ID: {doc_id[:8]}...)"
    doc_options[label] = d

selected_label = st.selectbox("Active Document Context:", options=list(doc_options.keys()))
selected_doc_info = doc_options[selected_label]
selected_doc_id = selected_doc_info.get("id")

# Header Information Banner
with st.container(border=True):
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    icon_check = get_icon("check-circle", color="#4ADE80", size=16)
    col_h1.markdown(f"<span style='color: #94A3B8;'>Company:</span> <b style='color: #FFFFFF;'>{selected_doc_info.get('company_name', 'Corporate Entity')}</b>", unsafe_allow_html=True)
    col_h2.markdown(f"<span style='color: #94A3B8;'>Period:</span> <b style='color: #FFFFFF;'>FY{selected_doc_info.get('fiscal_year', 'N/A')} {selected_doc_info.get('fiscal_period', '')}</b>", unsafe_allow_html=True)
    col_h3.markdown(f"<span style='color: #94A3B8;'>Status:</span> <span style='color: #4ADE80; font-weight: 600;'>{icon_check} {selected_doc_info.get('status', 'PROCESSED')}</span>", unsafe_allow_html=True)
    col_h4.markdown(f"<span style='color: #94A3B8;'>File:</span> <code style='color: #E63946; background: rgba(184, 29, 36, 0.15);'>{selected_doc_info.get('filename')}</code>", unsafe_allow_html=True)

st.divider()

# 2. Fetch Live Health Scores and Metrics
health_res = client.get_health_score(selected_doc_id) if selected_doc_id else None
raw_metrics = client.get_financial_metrics(selected_doc_id) if selected_doc_id else []
ratios_res = client.get_financial_ratios(selected_doc_id) if selected_doc_id else None

overall_score = float(health_res.get("overall_score", 70.0)) if health_res else 70.0
growth_score = float(health_res.get("growth_score", 70.0)) if health_res else 70.0
profit_score = float(health_res.get("profitability_score", 70.0)) if health_res else 70.0
liq_score = float(health_res.get("liquidity_score", 70.0)) if health_res else 70.0
lev_score = float(health_res.get("leverage_score", 70.0)) if health_res else 70.0
cf_score = float(health_res.get("cash_flow_score", 70.0)) if health_res else 70.0
risk_flags = health_res.get("risk_flags", ["Active in Vector Database"]) if health_res else ["Active in Vector Database"]

# 3. Key Performance Indicators (KPIs)
icon_trend = get_icon("trending-up", color="#E63946", size=20)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 10px;'><span>{icon_trend}</span><span style='font-size: 1.15rem; font-weight: 700; color: #FFFFFF;'>Key Financial Indicators</span></div>", unsafe_allow_html=True)

metrics_map = {}
currency_symbol = "$"
for m in raw_metrics:
    m_name = m.get("metric_name", "")
    m_val = m.get("value")
    if m_val is not None:
        metrics_map[m_name] = float(m_val)
    if "inr" in m.get("unit", "").lower():
        currency_symbol = "₹"

def format_curr(val_key: str):
    for k, v in metrics_map.items():
        if val_key.lower() in k.lower():
            return f"{currency_symbol}{v:,.0f} M"
    return "N/A"

rev_val = format_curr("revenue")
ebit_val = format_curr("ebitda") if format_curr("ebitda") != "N/A" else format_curr("operating income")
net_val = format_curr("net income")
debt_val = format_curr("debt")
cf_val = format_curr("cash flow") if format_curr("cash flow") != "N/A" else format_curr("cash")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
with kpi_col1:
    render_kpi_card("Revenue", rev_val, "Detected" if rev_val != "N/A" else "N/A", icon_name="dollar-sign")
with kpi_col2:
    render_kpi_card("EBITDA / EBIT", ebit_val, "Detected" if ebit_val != "N/A" else "N/A", icon_name="activity")
with kpi_col3:
    render_kpi_card("Net Income", net_val, "Detected" if net_val != "N/A" else "N/A", icon_name="trending-up")
with kpi_col4:
    render_kpi_card("Total Debt", debt_val, "Detected" if debt_val != "N/A" else "N/A", icon_name="layers")
with kpi_col5:
    render_kpi_card("Operating Cash", cf_val, "Detected" if cf_val != "N/A" else "N/A", icon_name="pie-chart")

st.divider()

# 4. Financial Health Score Overview: Gauge & 5D Radar
icon_activity = get_icon("activity", color="#E63946", size=20)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 10px;'><span>{icon_activity}</span><span style='font-size: 1.15rem; font-weight: 700; color: #FFFFFF;'>5-Dimension Corporate Health Assessment</span></div>", unsafe_allow_html=True)

score_col1, score_col2 = st.columns([1, 1.2])

with score_col1:
    with st.container(border=True):
        render_health_gauge(int(overall_score), "Overall Health Score")
        render_html(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 6px;">
    <span style="color: #94A3B8; font-size: 0.85rem;">Status: <b style="color: {'#4ADE80' if overall_score >= 70 else '#E63946'};">{'Strong / Solvency Cushion' if overall_score >= 70 else 'Moderate / Monitoring'}</b></span>
    <span style="color: #E63946; font-weight: 700; font-size: 0.9rem;">{overall_score:.1f}%</span>
</div>
""")

with score_col2:
    with st.container(border=True):
        render_radar_chart({
            "growth_score": growth_score,
            "profitability_score": profit_score,
            "liquidity_score": liq_score,
            "leverage_score": lev_score,
            "cash_flow_score": cf_score,
        }, title="5D Performance Radar (Wine Red System)")

st.divider()

# 5. Advanced Financial Visualizations
icon_pie = get_icon("pie-chart", color="#E63946", size=20)
render_html(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 10px;'><span>{icon_pie}</span><span style='font-size: 1.15rem; font-weight: 700; color: #FFFFFF;'>Advanced Financial Visualizations</span></div>")

tab_waterfall, tab_margins, tab_balance = st.tabs(["Waterfall Bridge", "Profitability Margins", "Asset & Capital Allocation"])

with tab_waterfall:
    with st.container(border=True):
        render_revenue_waterfall(metrics_map, title=f"{selected_doc_info.get('company_name', 'Company')} Income Statement Waterfall")

with tab_margins:
    with st.container(border=True):
        render_margin_comparison(metrics_map, ratios_res)

with tab_balance:
    with st.container(border=True):
        render_balance_sheet_composition(metrics_map)

st.divider()

# 6. Qualitative Risks & AI Insights
risk_col, insights_col = st.columns(2)

with risk_col:
    icon_shield = get_icon("shield-check", color="#E63946", size=20)
    render_html(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_shield}</span><span style='font-weight: 700; color: #FFFFFF;'>Qualitative Risk Disclosures</span></div>")
    with st.container(border=True):
        if risk_flags:
            for rf in risk_flags:
                render_html(f"""
<div style="background: rgba(184, 29, 36, 0.12); border-left: 3px solid #E63946; padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; font-size: 0.9rem; color: #F1F5F9;">
    {rf}
</div>
""")
        else:
            st.write("No qualitative risk disclosures flagged.")

with insights_col:
    icon_bot = get_icon("bot", color="#E63946", size=20)
    st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_bot}</span><span style='font-weight: 700; color: #FFFFFF;'>Filing Metadata & Ingestion Provenance</span></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            * **Filing Document:** <code style='color: #E63946; background: rgba(184, 29, 36, 0.15);'>{selected_doc_info.get('filename')}</code>
            * **Composite Health Score:** **{overall_score:.1f} / 100**
            * **Database Engine:** PostgreSQL 16 Alpine with native `pgvector` index.
            * **AI Intelligence:** Ask queries on the **AI Analyst** page powered by **Google Gemini 2.5 Flash**.
            """,
            unsafe_allow_html=True,
        )

# 7. One-Click Executive PDF Briefing Exporter
st.divider()
icon_export = get_icon("file-text", color="#E63946", size=20)
st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'><span>{icon_export}</span><span style='font-weight: 700; color: #FFFFFF;'>Executive Report Export</span></div>", unsafe_allow_html=True)

try:
    from app.services.report_generator import generate_executive_pdf_report
    ratios = {
        "opm": ratios_res.get("opm", 0.0) if ratios_res else 0.0,
        "npm": ratios_res.get("npm", 0.0) if ratios_res else 0.0,
        "roe": ratios_res.get("roe", 0.0) if ratios_res else 0.0,
        "current_ratio": ratios_res.get("current_ratio", 0.0) if ratios_res else 0.0,
        "debt_to_equity": ratios_res.get("debt_to_equity", 0.0) if ratios_res else 0.0,
        "interest_coverage": ratios_res.get("interest_coverage", 0.0) if ratios_res else 0.0,
    }
    pdf_bytes = generate_executive_pdf_report(
        company_name=selected_doc_info.get("company_name", "Corporate Entity"),
        fiscal_period=f"FY{selected_doc_info.get('fiscal_year', '2025')}",
        document_filename=selected_doc_info.get("filename", "Report.pdf"),
        health_score=overall_score,
        dimension_scores={
            "growth_score": growth_score,
            "profitability_score": profit_score,
            "liquidity_score": liq_score,
            "leverage_score": lev_score,
            "cash_flow_score": cf_score,
        },
        metrics=raw_metrics,
        ratios=ratios,
        risks=risk_flags,
    )
    st.download_button(
        label="Download Executive Briefing PDF",
        data=pdf_bytes,
        file_name=f"Executive_Briefing_{selected_doc_info.get('filename', 'Report')}.pdf",
        mime="application/pdf",
        type="primary",
    )
except Exception as e:
    st.caption(f"PDF generator status: {e}")