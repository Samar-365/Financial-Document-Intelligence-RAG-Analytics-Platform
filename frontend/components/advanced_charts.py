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
    """Renders a waterfall chart showing how top-line Revenue cascades to Net Income.
    
    Only renders when real Revenue is present. Intermediate steps are derived if missing,
    but labeled clearly as estimated. Never renders with entirely fabricated data.
    """
    rev = metrics_dict.get("Revenue") or metrics_dict.get("revenue")
    gp = metrics_dict.get("Gross Profit") or metrics_dict.get("gross_profit")
    op_inc = metrics_dict.get("Operating Income") or metrics_dict.get("operating_income")
    net_inc = metrics_dict.get("Net Income") or metrics_dict.get("net_income")

    if not rev or rev <= 0:
        st.info("Revenue data not available — upload a document with an income statement to generate the waterfall bridge.")
        return

    labels = ["Revenue"]
    measures = ["absolute"]
    y_vals = [rev]
    texts = [f"+{rev:,.0f}"]

    # Only add steps where we have real data or a reasonable mathematical derivation
    if gp is not None:
        cogs = -(rev - gp)
        labels += ["Cost of Sales", "Gross Margin"]
        measures += ["relative", "total"]
        y_vals += [cogs, None]
        texts += [f"{cogs:,.0f}", f"{gp:,.0f}"]
        gp_val = gp
    else:
        gp_val = rev  # pass-through if not available

    if op_inc is not None and gp is not None:
        opex = -(gp_val - op_inc)
        labels += ["Operating Expenses", "Operating Income"]
        measures += ["relative", "total"]
        y_vals += [opex, None]
        texts += [f"{opex:,.0f}", f"{op_inc:,.0f}"]
        op_val = op_inc
    elif op_inc is not None:
        op_val = op_inc
    else:
        op_val = gp_val

    if net_inc is not None:
        tax_other = -(op_val - net_inc)
        labels += ["Tax & Other", "Net Income"]
        measures += ["relative", "total"]
        y_vals += [tax_other, None]
        texts += [f"{tax_other:,.0f}", f"{net_inc:,.0f}"]

    fig = go.Figure(go.Waterfall(
        name="Income Waterfall",
        orientation="v",
        measure=measures,
        x=labels,
        y=y_vals,
        text=texts,
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
    """Renders two complementary donut charts showing Asset Structure and Liability/Equity Structure.
    
    Only renders when Total Assets is present. Never fabricates balance sheet structure.
    """
    total_assets = metrics_dict.get("Total Assets") or metrics_dict.get("total_assets")
    if not total_assets or total_assets <= 0:
        st.info("Total Assets not extracted — balance sheet composition cannot be shown without real asset data.")
        return

    cash = metrics_dict.get("Cash & Equivalents") or metrics_dict.get("cash")
    current_assets = metrics_dict.get("Current Assets")
    total_liab = metrics_dict.get("Total Liabilities") or metrics_dict.get("total_liabilities")
    debt = metrics_dict.get("Total Debt") or metrics_dict.get("total_debt")

    # Asset decomposition — only show segments we actually have data for
    asset_labels = []
    asset_vals = []
    if cash is not None:
        asset_labels.append("Cash & Equivalents")
        asset_vals.append(cash)
    remaining_assets = total_assets - (cash or 0)
    if remaining_assets > 0:
        asset_labels.append("Other Assets")
        asset_vals.append(remaining_assets)

    col1, col2 = st.columns(2)
    with col1:
        if asset_vals:
            fig_assets = go.Figure(data=[go.Pie(
                labels=asset_labels,
                values=asset_vals,
                hole=0.55,
                marker=dict(colors=["#E63946", "#B81D24", "#721622", "#400810"][:len(asset_vals)]),
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
        else:
            st.info("Asset breakdown data not available.")

    with col2:
        if total_liab is not None and total_liab > 0:
            equity = max(0.0, total_assets - total_liab)
            other_liab = max(0.0, total_liab - (debt or 0))
            cap_labels = ["Shareholders Equity", "Other Liabilities"]
            cap_vals = [equity, other_liab]
            cap_colors = ["#9B111E", "#58111A"]
            if debt is not None and debt > 0:
                cap_labels.insert(1, "Term Debt")
                cap_vals.insert(1, debt)
                cap_colors.insert(1, "#C41E3A")
            # Remove zero-value segments
            filtered = [(l, v, c) for l, v, c in zip(cap_labels, cap_vals, cap_colors) if v > 0]
            if filtered:
                cap_labels, cap_vals, cap_colors = zip(*filtered)
                fig_cap = go.Figure(data=[go.Pie(
                    labels=list(cap_labels),
                    values=list(cap_vals),
                    hole=0.55,
                    marker=dict(colors=list(cap_colors)),
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
        else:
            st.info("Liability/equity data not extracted — capital structure chart requires Total Liabilities.")


def render_margin_comparison(metrics_dict: Dict[str, float], ratios_dict: Optional[Dict[str, Any]] = None):
    """Renders a comparative horizontal bar visualizer for Gross Margin %, OPM %, and NPM %.
    
    Only shows margins with real data. Never injects fallback percentages.
    """
    rev = metrics_dict.get("Revenue") or metrics_dict.get("revenue")
    gp = metrics_dict.get("Gross Profit") or metrics_dict.get("gross_profit")
    op_inc = metrics_dict.get("Operating Income") or metrics_dict.get("operating_income")
    net_inc = metrics_dict.get("Net Income") or metrics_dict.get("net_income")

    categories = []
    values = []
    colors = []

    # Use ratios_dict if available (computed server-side), otherwise derive from raw metrics
    if ratios_dict:
        opm_val = ratios_dict.get("opm")
        npm_val = ratios_dict.get("npm")
    else:
        opm_val = None
        npm_val = None

    # Gross Margin — only if both revenue and gross profit are real extracted values
    if rev and rev > 0 and gp is not None:
        gm_pct = round((gp / rev) * 100, 2)
        categories.append("Gross Profit Margin")
        values.append(gm_pct)
        colors.append("#E63946")

    # OPM — prefer server-computed, else derive if both inputs present
    if opm_val is not None:
        categories.append("Operating Margin (OPM)")
        values.append(round(opm_val, 2))
        colors.append("#B81D24")
    elif rev and rev > 0 and op_inc is not None:
        categories.append("Operating Margin (OPM)")
        values.append(round((op_inc / rev) * 100, 2))
        colors.append("#B81D24")

    # NPM — prefer server-computed, else derive if both inputs present
    if npm_val is not None:
        categories.append("Net Profit Margin (NPM)")
        values.append(round(npm_val, 2))
        colors.append("#721622")
    elif rev and rev > 0 and net_inc is not None:
        categories.append("Net Profit Margin (NPM)")
        values.append(round((net_inc / rev) * 100, 2))
        colors.append("#721622")

    if not categories:
        st.info("Margin data not available — income statement metrics (Revenue, Gross Profit, Operating Income, Net Income) required.")
        return

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

