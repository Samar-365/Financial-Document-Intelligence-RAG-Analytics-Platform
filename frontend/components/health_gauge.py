import streamlit as st
import plotly.graph_objects as go

def render_health_gauge(score: int, title: str = "Corporate Health Score"):
    """Renders a radial gauge chart for financial health scoring (0 - 100) with Wine Red aesthetics."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>{title}</b>", 'font': {'size': 15, 'color': '#FFFFFF'}},
            number={'font': {'size': 32, 'color': '#FFFFFF'}, 'suffix': " / 100"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(230, 57, 70, 0.4)", 'tickfont': {'color': '#94A3B8'}},
                'bar': {'color': "#E63946", 'thickness': 0.28},
                'bgcolor': "#16151F",
                'borderwidth': 1.5,
                'bordercolor': "rgba(184, 29, 36, 0.4)",
                'steps': [
                    {'range': [0, 45], 'color': '#58111A'},    # Deep Wine / High Risk
                    {'range': [45, 70], 'color': '#800020'},   # Burgundy / Moderate
                    {'range': [70, 85], 'color': '#B81D24'},   # Crimson / Good
                    {'range': [85, 100], 'color': '#1B4332'}   # Emerald Forest / Prime
                ],
                'threshold': {
                    'line': {'color': "#FFFFFF", 'width': 3},
                    'thickness': 0.8,
                    'value': score
                }
            }
        )
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=35, b=15),
        paper_bgcolor="#08080A",
        plot_bgcolor="#121118",
        font={'family': 'Inter, sans-serif', 'color': '#F1F5F9'},
    )
    
    st.plotly_chart(fig, use_container_width=True)