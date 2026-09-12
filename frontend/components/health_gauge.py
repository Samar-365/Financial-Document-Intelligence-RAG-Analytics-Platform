import streamlit as st
import plotly.graph_objects as go

def render_health_gauge(score: int, title: str = "Financial Health Score"):
    """
    Renders a radial gauge chart for financial health scoring (0 - 100).
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#1f77b4"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#ff4b4b'},    # High Risk / Poor
                    {'range': [40, 70], 'color': '#ffa726'},   # Medium Risk / Fair
                    {'range': [70, 85], 'color': '#29b6f6'},   # Good
                    {'range': [85, 100], 'color': '#66bb6a'}   # Excellent
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        )
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)