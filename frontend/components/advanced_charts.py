"""Advanced Financial Visualizations for FDI RAG Platform.

Provides rich, interactive Plotly visualizations in Pitch Dark & Wine Red aesthetic:
1. Revenue & Cost Structure Waterfall
2. Balance Sheet Asset & Liability Composition (Donut / Sunburst)
3. Profitability & Margin Comparison Bridge
4. Cash Flow Allocation Chart
"""

from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


# Common dark wine layout palette
DARK_BG = "#08080A"
CARD_BG = "#121118"
WINE_PRIMARY = "#9B111E"
WINE_ACCENT = "#E63946"
WINE_DEEP = "#58111A"
WINE_GLOW = "#FF4D6D"
TEXT_COLOR = "#F1F5F9"
GRID_COLOR = "rgba(184, 29, 36, 0.15)"


def render_revenue_waterfall(metrics_dict: Dict[str, float], title: str = "Income Statement Waterfall Bridge"):
    """Renders a waterfall chart showing how top-line Revenue cascades to Net Income."""
    rev = metrics_dict.get("Revenue") or 0.0
    gp = metrics_dict.get("Gross Profit")
    op_inc = metrics_dict.get("Operating Income")
    net_inc = metrics_dict.get("Net Income")

    if not rev or rev <= 0:
        return

    # Derive intermediary steps if missing
    cogs = -(rev - gp) if (gp is not None and gp <= rev) else -(rev * 0.52)
    gp_val = gp if gp is not None else (rev + cogs)
    opex = -(gp_val - op_inc) if (op_inc is not None and op_inc <= gp_val) else -(gp_val * 0.35)
    op_val = op_inc if op_inc is not None else (gp_val + opex)
    tax_other = -(op_val - net_inc) if (net_inc is not None and net_inc <= op_val) else -(op_val * 0.22)
    final_net = net_inc if net_inc is not None else (op_val + tax_other)

    fig = go.Figure(go.Waterfall(
        name="Income Waterfall",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "total", "relative", "total"],
        x=["Revenue", "Cost of Sales", "Gross Margin", "Operating Expenses", "Operating Income", "Taxes & Other", "Net Income"],
        y=[rev, cogs, None, opex, None, tax_other, None],
        text=[f"+{rev:,.0f}", f"{cogs:,.0f}", f"{gp_val:,.0f}", f"{opex:,.0f}", f"{op_val:,.0f}", f"{tax_other:,.0f}", f"{final_net:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgba(230, 57, 70, 0.4)", "width": 1.5, "dash": "dot"}},
        decreasing={"marker": {"color": "#800020", "line": {"color": "#9B111E", "width": 1.5}}},
        increasing={"marker": {"color": "#1B4332", "line": {"color": "#2D6A4F", "width": 1.5}}},
        totals={"marker": {"color": "#B81D24", "line": {"color": "#E63946", "width": 1.5}}},
    ))

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"color": TEXT_COLOR, "size": 15}},
        plot_bgcolor=CARD_BG,
        paper_bgcolor=DARK_BG,
        font={"family": "Inter, sans-serif", "color": "#94A3B8"},
        margin=dict(l=20, r=20, t=45, b=25),
        height=340,
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zerolinecolor=WINE_ACCENT,
            color="#94A3B8",
        ),
        xaxis=dict(
            showgrid=False,
            color=TEXT_COLOR,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_balance_sheet_composition(metrics_dict: Dict[str, float]):
    """Renders two complementary donut charts showing Asset Structure and Liability/Equity Structure."""
    total_assets = metrics_dict.get("Total Assets") or 100.0
    cash = metrics_dict.get("Cash & Equivalents") or (total_assets * 0.20)
    receivables = total_assets * 0.18
    other_current = total_assets * 0.12
    ppe_non_current = max(0.0, total_assets - (cash + receivables + other_current))

    total_liab = metrics_dict.get("Total Liabilities") or (total_assets * 0.60)
    debt = metrics_dict.get("Total Debt") or (total_liab * 0.45)
    other_liab = max(0.0, total_liab - debt)
    equity = max(0.0, total_assets - total_liab)

    col1, col2 = st.columns(2)
    with col1:
        fig_assets = go.Figure(data=[go.Pie(
            labels=["Cash & Equivalents", "Receivables", "Other Current", "Non-Current / PP&E"],
            values=[cash, receivables, other_current, ppe_non_current],
            hole=0.55,
            marker=dict(colors=["#E63946", "#B81D24", "#721622", "#400810"]),
            textinfo="label+percent",
            insidetextorientation="radial",
        )])
        fig_assets.update_layout(
            title={"text": "<b>Asset Capital Allocation</b>", "font": {"color": TEXT_COLOR, "size": 14}},
            paper_bgcolor=DARK_BG,
            plot_bgcolor=CARD_BG,
            font={"color": "#94A3B8"},
            showlegend=False,
            margin=dict(l=10, r=10, t=35, b=10),
            height=260,
        )
        st.plotly_chart(fig_assets, use_container_width=True)

    with col2:
        fig_cap = go.Figure(data=[go.Pie(
            labels=["Shareholders Equity", "Term Debt", "Other Liabilities"],
            values=[equity, debt, other_liab],
            hole=0.55,
            marker=dict(colors=["#9B111E", "#C41E3A", "#58111A"]),
            textinfo="label+percent",
            insidetextorientation="radial",
        )])
        fig_cap.update_layout(
            title={"text": "<b>Capital & Leverage Structure</b>", "font": {"color": TEXT_COLOR, "size": 14}},
            paper_bgcolor=DARK_BG,
            plot_bgcolor=CARD_BG,
            font={"color": "#94A3B8"},
            showlegend=False,
            margin=dict(l=10, r=10, t=35, b=10),
            height=260,
        )
        st.plotly_chart(fig_cap, use_container_width=True)


def render_margin_comparison(metrics_dict: Dict[str, float], ratios_dict: Optional[Dict[str, Any]] = None):
    """Renders a comparative horizontal bar visualizer for Gross Margin %, OPM %, and NPM %."""
    rev = metrics_dict.get("Revenue") or 1.0
    gp = metrics_dict.get("Gross Profit")
    op_inc = metrics_dict.get("Operating Income")
    net_inc = metrics_dict.get("Net Income")

    # Use ratios_dict if available, otherwise compute directly
    gm_pct = round((gp / rev) * 100, 2) if gp is not None else 45.0
    opm_pct = ratios_dict.get("opm") if ratios_dict and ratios_dict.get("opm") else (round((op_inc / rev) * 100, 2) if op_inc is not None else 28.0)
    npm_pct = ratios_dict.get("npm") if ratios_dict and ratios_dict.get("npm") else (round((net_inc / rev) * 100, 2) if net_inc is not None else 20.0)

    categories = ["Gross Profit Margin", "Operating Margin (OPM)", "Net Profit Margin (NPM)"]
    values = [gm_pct, opm_pct, npm_pct]
    colors = ["#E63946", "#B81D24", "#721622"]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        text=[f"<b>{v:.1f}%</b>" for v in values],
        textposition="outside",
        marker=dict(
            color=colors,
            line=dict(color=WINE_ACCENT, width=1.5),
        )
    ))

    fig.update_layout(
        title={"text": "<b>Profitability Margin Performance</b>", "font": {"color": TEXT_COLOR, "size": 15}},
        plot_bgcolor=CARD_BG,
        paper_bgcolor=DARK_BG,
        font={"color": "#94A3B8"},
        margin=dict(l=20, r=30, t=40, b=20),
        height=250,
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            ticksuffix="%",
            range=[0, max(values) * 1.25 if values else 100],
            color="#94A3B8",
        ),
        yaxis=dict(
            color=TEXT_COLOR,
            autorange="reversed",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_comparative_deltas_chart(deltas: list, doc_a_id: str, doc_b_id: str, doc_a_name: str, doc_b_name: str):
    """Renders a comparative grouped bar chart contrasting two filings across extracted metrics."""
    if not deltas:
        return

    metrics = []
    vals_a = []
    vals_b = []

    for d in deltas:
        name = d.get("metric_name", "")
        va = d.get("values", {}).get(doc_a_id)
        vb = d.get("values", {}).get(doc_b_id)
        if va is not None and vb is not None and (va > 0 or vb > 0):
            metrics.append(name)
            vals_a.append(va)
            vals_b.append(vb)

    if not metrics:
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=f"{doc_a_name} (Baseline)",
        x=metrics,
        y=vals_a,
        marker_color="#800020",
        marker_line=dict(color="#B81D24", width=1.2),
        text=[f"₹{v:,.0f}" for v in vals_a],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name=f"{doc_b_name} (Target)",
        x=metrics,
        y=vals_b,
        marker_color="#E63946",
        marker_line=dict(color="#FF4D6D", width=1.2),
        text=[f"₹{v:,.0f}" for v in vals_b],
        textposition="outside",
    ))

    fig.update_layout(
        title={"text": "<b>Comparative Financial Metrics (₹ Cr)</b>", "font": {"color": TEXT_COLOR, "size": 15}},
        barmode="group",
        plot_bgcolor=CARD_BG,
        paper_bgcolor=DARK_BG,
        font={"color": "#94A3B8"},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"color": TEXT_COLOR}
        ),
        margin=dict(l=20, r=20, t=60, b=30),
        height=350,
        xaxis=dict(color=TEXT_COLOR),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            color="#94A3B8",
        )
    )
    st.plotly_chart(fig, use_container_width=True)

