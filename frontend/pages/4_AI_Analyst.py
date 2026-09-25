import streamlit as st
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.chat_interface import render_chat_message
from components.theme import apply_theme, render_page_header, get_icon, render_html
from utils.api_client import client

st.set_page_config(page_title="AI Analyst | FinIntel AI", layout="wide")
apply_theme()

render_page_header(
    title="AI Financial Analyst",
    subtitle="Ask questions about your uploaded financial documents with verifiable citations powered by Google Gemini.",
    icon_name="bot"
)

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Fetch live documents
live_docs = client.get_documents() or []

if not live_docs:
    st.warning("No documents available to query.")
    st.write("Please upload a financial statement, spreadsheet, or annual report in the **Upload** page before asking questions.")
    if st.button("Go to Upload Page", type="primary"):
        st.switch_page("pages/2_Upload.py")
    st.stop()

doc_options = {}
for d in live_docs:
    doc_id = d.get("id", "")
    filename = d.get("filename", "Document")
    company = d.get("company_name") or filename.rsplit(".", 1)[0]
    period = d.get("fiscal_period", "")
    year = d.get("fiscal_year", "")
    period_label = f"{period} FY{year}" if year else ""
    label = f"{company} — {period_label} ({filename[:30]})"
    doc_options[label] = d

# Restore cross-page persistent selection from Dashboard or Analysis by ID
target_id = st.session_state.get("selected_doc_id")
target_label = None
if target_id:
    for lbl, d in doc_options.items():
        if str(d.get("id")) == str(target_id):
            target_label = lbl
            break

if not target_label or target_label not in doc_options:
    target_label = st.session_state.get("selected_doc_label")
    if target_label not in doc_options:
        target_label = list(doc_options.keys())[0]

if st.session_state.get("ai_analyst_doc_select") != target_label:
    st.session_state["ai_analyst_doc_select"] = target_label

selected_label = st.selectbox(
    "Search Context / Document Target:",
    options=list(doc_options.keys()),
    key="ai_analyst_doc_select",
)
st.session_state["selected_doc_label"] = selected_label
st.session_state["selected_doc_id"] = doc_options[selected_label].get("id", "")

selected_doc_info = doc_options[selected_label]
selected_doc_id = selected_doc_info.get("id")
selected_doc_filename = selected_doc_info.get("filename", "Document")

# Reset chat session if document switched to avoid mixed-context answers
if st.session_state.get("last_chat_doc_id") != selected_doc_id:
    st.session_state["chat_messages"] = []
    st.session_state["last_chat_doc_id"] = selected_doc_id

# Document context banner
period_disp = selected_doc_info.get('fiscal_period', '')
year_disp = selected_doc_info.get('fiscal_year', '')
period_text = f"{period_disp} FY{year_disp}" if period_disp and period_disp != "FY" else (f"FY{year_disp}" if year_disp else "Active Filing")
st.markdown(
    f"<div style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;'>"
    f"Active: <b style='color: #FFFFFF;'>{selected_doc_info.get('company_name', selected_doc_filename)}</b> "
    f"— <span style='color: #E63946;'>{period_text}</span> "
    f"— Filename: <code style='color: #E63946; background: rgba(184, 29, 36, 0.15);'>{selected_doc_filename[:35]}</code>"
    f"</div>",
    unsafe_allow_html=True,
)
st.divider()

sparkles_svg = get_icon("sparkles", color="#E63946", size=18)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {sparkles_svg}
    <span style="font-size: 1.05rem; font-weight: 600; color: #F1F5F9;">Suggested Financial Queries</span>
</div>
""")

suggestions = [
    "What was the total revenue from operations?",
    "What were the major risks mentioned in the filing?",
    "What is the company's operating margin and EBITDA?",
    "What is the company's total debt and cash position?"
]

cols = st.columns(len(suggestions))
for idx, question in enumerate(suggestions):
    if cols[idx].button(question, key=f"sug_{idx}"):
        st.session_state["pending_prompt"] = question
        st.rerun()

st.divider()

msg_svg = get_icon("message-square", color="#E63946", size=18)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    {msg_svg}
    <span style="font-size: 1.05rem; font-weight: 600; color: #F1F5F9;">Conversation History</span>
</div>
""")

chat_container = st.container()

with chat_container:
    if not st.session_state["chat_messages"]:
        st.caption("No questions asked yet. Choose a suggested query above or type below.")
    for message in st.session_state["chat_messages"]:
        render_chat_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources"),
            metrics=message.get("metrics")
        )

prompt = st.chat_input("Ask a question about the selected document...")

if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    
    with chat_container:
        render_chat_message(role="user", content=prompt)
            
        with st.spinner("Retrieving grounded excerpts and generating answer via Gemini..."):
            t0 = time.time()
            rag_res = client.query_rag(document_id=selected_doc_id, question=prompt, top_k=5)
            elapsed = time.time() - t0

            if rag_res and rag_res.get("answer"):
                response_text = rag_res.get("answer")
                raw_citations = rag_res.get("citations", [])
                
                sources = []
                for c in raw_citations:
                    sources.append({
                        "doc": selected_doc_filename,
                        "page": c.get("page_number", 1),
                        "section": f"Relevance: {c.get('relevance_score', 0.0):.2f}",
                        "text": c.get("snippet", "")
                    })
                
                metrics = {
                    "time": f"{rag_res.get('latency_ms', int(elapsed * 1000))}ms",
                    "chunks": len(raw_citations)
                }
            else:
                response_text = (
                    f"No relevant excerpts found in **{selected_doc_filename}** answering: *{prompt}*.\n\n"
                    f"Please verify that the document contains disclosures on this topic, or ensure your `GEMINI_API_KEY` is configured."
                )
                sources = []
                metrics = {"time": f"{int(elapsed * 1000)}ms", "chunks": 0}
            
            # Render assistant message
            render_chat_message(
                role="assistant",
                content=response_text,
                sources=sources,
                metrics=metrics
            )
            
            # Save assistant response to session state
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": response_text,
                "sources": sources,
                "metrics": metrics
            })