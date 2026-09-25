import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.theme import apply_theme, render_page_header, get_icon, render_html
from components.advanced_charts import render_comparative_deltas_chart
from utils.api_client import client

st.set_page_config(page_title="Comparison | FinIntel AI", layout="wide")
apply_theme()

render_page_header(
    title="Document Comparison",
    subtitle="Compare two processed financial reports side-by-side with automated delta calculations and visual analytics.",
    icon_name="git-compare"
)

# Fetch live documents
live_docs = client.get_documents() or []

if len(live_docs) < 2:
    st.warning("At least two documents are required for comparison.")
    st.write(
        f"Currently, **{len(live_docs)}** document(s) exist in PostgreSQL. "
        "Please go to the **Upload** page and upload additional reports (e.g., FY2024 and FY2025, or a competitor statement) "
        "to run automated comparative delta analysis."
    )
    if st.button("Go to Upload Page", type="primary"):
        st.switch_page("pages/2_Upload.py")
    st.stop()

doc_options = {}
for d in live_docs:
    doc_id = d.get("id", "")
    filename = d.get("filename", "Document")
    company = d.get("company_name") or filename.rsplit(".", 1)[0]
    period = d.get("fiscal_period", "")
    year = d.get("fiscal_year", "")
    period_label = f"{period} FY{year}" if year else ""
    label = f"{company} — {period_label} ({filename[:30]})"
    doc_options[label] = d

options_list = list(doc_options.keys())

col_a, col_b = st.columns(2)
with col_a:
    label_a = st.selectbox("Document A (Baseline):", options=options_list, index=0)
with col_b:
    label_b = st.selectbox("Document B (Comparison):", options=options_list, index=min(1, len(options_list) - 1))

doc_a_info = doc_options[label_a]
doc_b_info = doc_options[label_b]
doc_a_id = doc_a_info.get("id")
doc_b_id = doc_b_info.get("id")

if st.button("Compare Documents", type="primary"):
    st.session_state["has_compared"] = True

st.divider()

# Comparison Logic & Validation
if st.session_state.get("has_compared", False):
    if doc_a_id == doc_b_id:
        st.warning("Please select two different documents to perform a comparative analysis.")
    else:
        bar_svg = get_icon("trending-up", color="#E63946", size=18)
        render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {bar_svg}
    <span style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">Metric Comparison & Delta Analysis</span>
</div>
""")
        
        with st.spinner("Computing comparative deltas across documents..."):
            comp_res = client.compare_documents([doc_a_id, doc_b_id])
            health_a = client.get_health_score(doc_a_id) if doc_a_id else None
            health_b = client.get_health_score(doc_b_id) if doc_b_id else None

        deltas = comp_res.get("deltas", []) if comp_res else []

        if deltas:
            # 1. Comparative Visual Bar Chart
            render_comparative_deltas_chart(
                deltas=deltas,
                doc_a_id=doc_a_id,
                doc_b_id=doc_b_id,
                doc_a_name=doc_a_info.get("filename", "Baseline"),
                doc_b_name=doc_b_info.get("filename", "Target")
            )
            
            # 2. Detailed Delta Table
            table_rows = []
            for delta in deltas:
                val_a = delta.get("values", {}).get(doc_a_id)
                val_b = delta.get("values", {}).get(doc_b_id)
                pct = delta.get("percent_delta", 0.0)
                
                trend_direction = "Expansion" if pct > 0 else ("Contraction" if pct < 0 else "Neutral")
                if "debt" in delta.get("metric_name", "").lower():
                    trend_direction = "Deleveraging" if pct < 0 else "Leverage Increase"
                
                table_rows.append({
                    "Financial Metric": delta.get("metric_name"),
                    f"{doc_a_info.get('filename')} (Baseline)": f"₹{val_a:,.1f} Cr" if val_a is not None else "N/A",
                    f"{doc_b_info.get('filename')} (Target)": f"₹{val_b:,.1f} Cr" if val_b is not None else "N/A",
                    "Change": f"{'+' if pct > 0 else ''}{pct:.2f}%",
                    "Variance Type": trend_direction,
                })
            
            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No common metrics were detected across these two filings to compute deltas.")

        st.divider()
        
        # Risk Profile Changes
        alert_svg = get_icon("alert-triangle", color="#E63946", size=18)
        render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {alert_svg}
    <span style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">Risk Profile & Health Trajectory</span>
</div>
""")
        
        score_a = (health_a or {}).get("overall_score")
        score_b = (health_b or {}).get("overall_score")
        flags_a = set((health_a or {}).get("risk_flags", []))
        flags_b = set((health_b or {}).get("risk_flags", []))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Health: {doc_a_info.get('filename')}",
                value=f"{score_a:.1f}/100" if score_a is not None else "N/A",
            )
        with col2:
            delta_str = f"{(score_b - score_a):+.1f} pts" if (score_a is not None and score_b is not None) else None
            st.metric(
                label=f"Health: {doc_b_info.get('filename')}",
                value=f"{score_b:.1f}/100" if score_b is not None else "N/A",
                delta=delta_str,
            )
        with col3:
            new_risks = flags_b - flags_a
            st.metric(label="Newly Emerged Risks", value=f"{len(new_risks)} detected")
        
        if new_risks:
            render_html("""
<div style="font-size: 0.9rem; font-weight: 600; color: #E63946; margin-top: 14px; margin-bottom: 6px;">
    Newly Emerged Risk Factors:
</div>
""")
            for r in new_risks:
                render_html(f"""
<div style="background: rgba(184, 29, 36, 0.12); border-left: 3px solid #E63946; padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; color: #CBD5E1; font-size: 0.88rem;">
    {r}
</div>
""")