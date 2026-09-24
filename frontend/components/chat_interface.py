import streamlit as st
from components.theme import get_icon, render_html

def render_chat_message(role: str, content: str, sources: list = None, metrics: dict = None):
    """
    Renders an individual chat bubble with expandable citation sources and response metrics,
    using Lucide SVG vector icons instead of emojis.
    """
    with st.chat_message(role):
        st.markdown(content)
        
        # Render assistant citations and performance metrics if available
        if role == "assistant" and sources:
            clock_svg = get_icon("clock", color="#94A3B8", size=14)
            layers_svg = get_icon("layers", color="#94A3B8", size=14)
            
            with st.expander("Citation Sources & Performance Telemetry"):
                if metrics:
                    render_html(f"""
<div style="display: flex; gap: 20px; align-items: center; color: #94A3B8; font-size: 0.82rem; margin-bottom: 8px;">
    <span style="display: flex; align-items: center; gap: 6px;">
        {clock_svg} <span>Latency: <strong style="color: #F1F5F9;">{metrics.get('time', 'N/A')}</strong></span>
    </span>
    <span style="display: flex; align-items: center; gap: 6px;">
        {layers_svg} <span>Chunks Retrieved: <strong style="color: #F1F5F9;">{metrics.get('chunks', 'N/A')}</strong></span>
    </span>
</div>
""")
                    st.divider()
                
                for idx, src in enumerate(sources, 1):
                    doc_name = src.get("doc", "Unknown Document")
                    page_num = src.get("page", "N/A")
                    section = src.get("section", "General")
                    text_snippet = src.get("text", "")
                    
                    render_html(f"""
<div style="background: rgba(184, 29, 36, 0.08); border-left: 3px solid #E63946; border-radius: 4px; padding: 8px 12px; margin-bottom: 10px;">
    <div style="font-size: 0.85rem; font-weight: 600; color: #F8FAFC; margin-bottom: 4px;">
        Source {idx}: {doc_name} &bull; Page {page_num} <span style="color: #94A3B8; font-weight: 400; font-size: 0.78rem;">({section})</span>
    </div>
    <div style="font-size: 0.82rem; color: #CBD5E1; font-style: italic; line-height: 1.4;">
        "{text_snippet}"
    </div>
</div>
""")