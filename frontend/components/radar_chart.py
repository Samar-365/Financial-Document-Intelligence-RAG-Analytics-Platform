"""5D Corporate Health Radar Visualizer Component (Developer 3 - Shreya).

Renders a dynamic Plotly polar radar chart visualizing corporate performance
across Growth (20%), Profitability (25%), Liquidity (20%), Leverage (20%), and Cash Flow (15%).
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


def render_radar_chart(health_data: Dict[str, float], title: str = "5-Dimension Corporate Health Radar"):
    """Renders an interactive Plotly radar (polar) chart for health dimension scores (0-100).
    
    None scores are plotted at 0 with a footnote. Never injects fabricated defaults.
    """
    dim_map = [
        ("Growth", "growth_score"),
        ("Profitability", "profitability_score"),
        ("Liquidity", "liquidity_score"),
        ("Leverage", "leverage_score"),
        ("Cash Flow", "cash_flow_score"),
    ]
    categories = [d[0] for d in dim_map]
    raw_scores = [health_data.get(d[1]) for d in dim_map]
    # Plot None as 0 so the radar renders; flag which are unavailable for the caption
    scores = [s if s is not None else 0.0 for s in raw_scores]
    unavailable = [categories[i] for i, s in enumerate(raw_scores) if s is None]

    # Close the radar polygon by appending the first value
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(196, 30, 58, 0.32)",
        line=dict(color="#E63946", width=2.5),
        marker=dict(size=7, color="#FFFFFF", line=dict(color="#E63946", width=2)),
        name="Health Score",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#121118",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#94A3B8"),
                gridcolor="rgba(184, 29, 36, 0.2)",
                linecolor="rgba(184, 29, 36, 0.3)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#F1F5F9"),
                gridcolor="rgba(184, 29, 36, 0.2)",
                linecolor="rgba(184, 29, 36, 0.3)",
            )
        ),
        showlegend=False,
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color="#FFFFFF"),
            x=0.5,
            xanchor="center",
        ),
        margin=dict(l=35, r=35, t=45, b=25),
        height=320,
        paper_bgcolor="#08080A",
        plot_bgcolor="#121118",
    )

    st.plotly_chart(fig, use_container_width=True)
    if unavailable:
        st.caption(f"⚠️ Dimensions not computable from current document: **{', '.join(unavailable)}** — shown as 0. Additional periods or balance-sheet data required.")
