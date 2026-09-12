import streamlit as st

def render_chat_message(role: str, content: str, sources: list = None, metrics: dict = None):
    """
    Renders an individual chat bubble with expandable citation sources and response metrics.
    """
    with st.chat_message(role):
        st.markdown(content)
        
        # Render assistant citations and performance metrics if available
        if role == "assistant" and sources:
            with st.expander("📚 View Citation Sources & Performance Metrics"):
                if metrics:
                    st.caption(
                        f"⏱️ **Response time:** {metrics.get('time', 'N/A')} | "
                        f"🔍 **Chunks retrieved:** {metrics.get('chunks', 'N/A')}"
                    )
                    st.divider()
                
                for idx, src in enumerate(sources, 1):
                    doc_name = src.get("doc", "Unknown Document")
                    page_num = src.get("page", "N/A")
                    section = src.get("section", "General")
                    text_snippet = src.get("text", "")
                    
                    st.markdown(f"**Source {idx}:** {doc_name} (Page {page_num}) — *{section}*")
                    st.info(f'"{text_snippet}"')