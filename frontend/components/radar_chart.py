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
        fillcolor="rgba(31, 119, 180, 0.35)",
        line=dict(color="#1f77b4", width=2.5),
        marker=dict(size=6, color="#0d47a1"),
        name="Performance Score",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                color="#666",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, weight="bold"),
            )
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=16),
            x=0.5,
            xanchor="center",
        ),
        margin=dict(l=40, r=40, t=50, b=30),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)
