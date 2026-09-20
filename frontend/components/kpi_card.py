import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = None, delta_color: str = "normal", confidence: str = None):
    """Renders a visual card containing metric data and confidence status."""
    with st.container(border=True):
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )
        if confidence:
            st.caption(f"**{confidence}** Confidence")