"""5D Corporate Health Radar Visualizer Component (Developer 3 - Shreya).

Renders a dynamic Plotly polar radar chart visualizing corporate performance
across Growth (20%), Profitability (25%), Liquidity (20%), Leverage (20%), and Cash Flow (15%).
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


def render_radar_chart(health_data: Dict[str, float], title: str = "5-Dimension Corporate Health Radar"):
    """Renders an interactive Plotly radar (polar) chart for health dimension scores (0-100)."""
    categories = ["Growth", "Profitability", "Liquidity", "Leverage", "Cash Flow"]
    scores = [
        health_data.get("growth_score", 75.0),
        health_data.get("profitability_score", 80.0),
        health_data.get("liquidity_score", 70.0),
        health_data.get("leverage_score", 72.0),
        health_data.get("cash_flow_score", 76.0),
    ]

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
