import streamlit as st
from components.theme import get_icon


def render_kpi_card(
    title: str,
    value: str,
    delta: str = None,
    delta_color: str = "normal",
    confidence: str = None,
    icon_name: str = "trending-up",
):
    """Renders a sleek Pitch Dark & Wine Red KPI card with Lucide vector icon."""
    with st.container(border=True):
        icon_svg = get_icon(icon_name, color="#E63946", size=16)
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
                <span style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8;">{title}</span>
                <span style="background: rgba(184, 29, 36, 0.15); border-radius: 6px; padding: 4px; display: flex; align-items: center;">{icon_svg}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric(
            label="",
            value=value,
            delta=delta,
            delta_color=delta_color,
            label_visibility="collapsed",
        )
        if confidence:
            st.caption(f"<span style='color: #64748B;'>Confidence: <b style='color: #E63946;'>{confidence}</b></span>", unsafe_allow_html=True)