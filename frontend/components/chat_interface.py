"""Modern Financial AI Assistant Chat Interface for FinIntel AI.

Implements:
1. Distinct User vs FinIntel AI message styling (right-aligned user bubble, left-aligned AI surface).
2. FinIntel official SVG vector logo avatar for AI (strictly zero robot emojis).
3. Structured financial response layout (Answer, Key Figures highlight, Verified Sources citations).
4. Expandable verification cards with exact page numbers and snippets.
"""

import streamlit as st
from components.theme import get_icon, render_html


def render_chat_message(role: str, content: str, sources: list = None, metrics: dict = None):
    """Renders a sleek, professional financial chat message."""
    if role == "user":
        user_svg = get_icon("user", color="#E63946", size=16)
        render_html(f"""
<div style="display: flex; justify-content: flex-end; margin-bottom: 18px;">
    <div style="
        max-width: 80%;
        background: #18121A;
        border: 1px solid rgba(230, 57, 70, 0.4);
        border-radius: 14px 14px 2px 14px;
        padding: 14px 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    ">
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 6px; margin-bottom: 6px;">
            <span style="font-size: 0.72rem; font-weight: 700; color: #E63946; letter-spacing: 0.05em; text-transform: uppercase;">You</span>
            <div style="background: rgba(184, 29, 36, 0.2); border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center;">
                {user_svg}
            </div>
        </div>
        <div style="color: #F8FAFC; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap;">{content}</div>
    </div>
</div>
""")
    else:
        brand_svg = get_icon("activity", color="#E63946", size=16)
        render_html(f"""
<div style="display: flex; justify-content: flex-start; margin-bottom: 22px;">
    <div style="
        max-width: 88%;
        background: #111017;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #E63946;
        border-radius: 2px 14px 14px 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
            <div style="background: rgba(184, 29, 36, 0.2); border: 1px solid rgba(230, 57, 70, 0.4); border-radius: 6px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
                {brand_svg}
            </div>
            <span style="font-size: 0.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.04em;">FININTEL AI</span>
            <span style="font-size: 0.7rem; color: #94A3B8; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">Verified Audit Grounding</span>
        </div>
        <div class="finintel-ai-answer" style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.6;">
""")
        # Render markdown content inside the message box
        st.markdown(content)

        # Render Citations and Telemetry
        if sources:
            clock_svg = get_icon("clock", color="#94A3B8", size=13)
            layers_svg = get_icon("layers", color="#94A3B8", size=13)
            file_svg = get_icon("file-text", color="#E63946", size=13)

            latency_text = metrics.get('time', 'N/A') if metrics else 'N/A'
            chunks_text = metrics.get('chunks', len(sources)) if metrics else len(sources)

            with st.expander("Grounded Sources & Citations", expanded=False):
                render_html(f"""
<div style="display: flex; gap: 20px; align-items: center; color: #94A3B8; font-size: 0.78rem; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06);">
    <span style="display: flex; align-items: center; gap: 5px;">
        {clock_svg} <span>Latency: <strong style="color: #F1F5F9;">{latency_text}</strong></span>
    </span>
    <span style="display: flex; align-items: center; gap: 5px;">
        {layers_svg} <span>Evidence Chunks: <strong style="color: #F1F5F9;">{chunks_text}</strong></span>
    </span>
</div>
""")
                for idx, src in enumerate(sources, 1):
                    doc_name = src.get("doc", "Source Filing")
                    page_num = src.get("page", "N/A")
                    section = src.get("section", "")
                    text_snippet = src.get("text", "")
                    sec_span = f"<span style='color: #94A3B8; font-size: 0.75rem; margin-left: 6px;'>({section})</span>" if section else ""

                    render_html(f"""
<div style="
    background: rgba(184, 29, 36, 0.08);
    border: 1px solid rgba(184, 29, 36, 0.25);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
">
    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.82rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">
        <span>{file_svg}</span>
        <span>Source {idx}:</span>
        <span style="color: #CBD5E1; font-weight: 500;">{doc_name}</span>
        <span style="color: #E63946;">&bull; Page {page_num}</span>
        {sec_span}
    </div>
    <div style="font-size: 0.8rem; color: #94A3B8; font-style: italic; line-height: 1.45; padding-left: 18px;">
        &ldquo;{text_snippet}&rdquo;
    </div>
</div>
""")

        render_html("""
        </div>
    </div>
</div>
""")