import streamlit as st
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.chat_interface import render_chat_message
from components.theme import apply_theme, render_page_header, get_icon, render_html
from utils.api_client import client
from utils.workspace_state import (
    render_workspace_sidebar_branding,
    render_document_selector,
    get_active_doc_id,
    is_response_valid,
)

st.set_page_config(
    page_title="FININTEL — AI Analyst",
    page_icon="frontend/assets/finintel_logo.png",
    layout="wide"
)

# Apply Pitch Dark & Wine Red styling and official sidebar branding
apply_theme()
render_workspace_sidebar_branding()

render_page_header(
    title="AI Financial Analyst",
    subtitle="Financial intelligence for the selected document with verifiable page-level citations.",
    icon_name="bot"
)

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Fetch live documents from API
live_docs = client.get_documents() or []

if not live_docs:
    st.warning("No documents available to query.")
    st.write("Please upload a financial statement, spreadsheet, or annual report in the **Upload** page before asking questions.")
    if st.button("Go to Upload Page", type="primary"):
        st.switch_page("pages/2_Upload.py")
    st.stop()

# Canonical Document Selector across all workspace pages
selected_doc_info = render_document_selector(live_docs, key_prefix="ai_analyst")
selected_doc_id = str(selected_doc_info.get("id"))
selected_doc_filename = selected_doc_info.get("filename", "Document.pdf")
company_name = selected_doc_info.get("company_name") or selected_doc_filename.rsplit(".", 1)[0]

# Detect currency
currency_label = "INR" if ("inr" in selected_doc_filename.lower() or "tcs" in selected_doc_filename.lower() or "infosys" in selected_doc_filename.lower()) else "USD"

# Automatic conversation reset on document switch to prevent context poisoning
if st.session_state.get("last_chat_doc_id") != selected_doc_id:
    st.session_state["chat_messages"] = []
    st.session_state["last_chat_doc_id"] = selected_doc_id

# 1. Document Context Banner
period_disp = selected_doc_info.get('fiscal_period', '')
year_disp = selected_doc_info.get('fiscal_year', '')
period_text = f"{period_disp} FY{year_disp}" if period_disp and period_disp != "FY" else (f"FY{year_disp}" if year_disp else "Active Filing")

brand_icon_svg = get_icon("activity", color="#E63946", size=18)
render_html(f"""
<div style="
    background: #111017;
    border: 1px solid rgba(196, 30, 58, 0.28);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="
            background: rgba(184, 29, 36, 0.2);
            border: 1px solid rgba(230, 57, 70, 0.45);
            border-radius: 8px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            {brand_icon_svg}
        </div>
        <div>
            <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">ANALYZING FILING</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">
                {company_name} <span style="color: #64748B;">&bull;</span> <span style="color: #E63946;">{period_text}</span> <span style="color: #64748B;">&bull;</span> {currency_label}
            </div>
        </div>
    </div>
    <div>
        <code style="color: #E63946; background: rgba(184, 29, 36, 0.15); border: 1px solid rgba(184, 29, 36, 0.3); padding: 5px 12px; border-radius: 6px; font-size: 0.82rem;">
            {selected_doc_filename[:36]}
        </code>
    </div>
</div>
""")

# 2. Suggested Questions Chips
sparkles_svg = get_icon("sparkles", color="#E63946", size=16)
render_html(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
    {sparkles_svg}
    <span style="font-size: 0.95rem; font-weight: 600; color: #CBD5E1;">Suggested Inquiries</span>
</div>
""")

suggestions = [
    "What was the total revenue?",
    "What is the operating margin?",
    "What were the major risks?",
    "How much debt does the company have?",
    "How did revenue change YoY?",
    "Summarize the financial highlights.",
]

chip_cols = st.columns(len(suggestions))
for idx, question in enumerate(suggestions):
    if chip_cols[idx].button(question, key=f"sug_chip_{idx}"):
        st.session_state["pending_prompt"] = question
        st.rerun()

st.divider()

# 3. Conversation Thread
chat_container = st.container()

with chat_container:
    if not st.session_state["chat_messages"]:
        render_html(f"""
<div style="text-align: center; padding: 40px 20px; color: #64748B;">
    <div style="font-size: 0.95rem; margin-bottom: 6px; color: #94A3B8;">No questions asked yet for this document.</div>
    <div style="font-size: 0.85rem;">Select an inquiry chip above or ask a custom question below.</div>
</div>
""")
    for message in st.session_state["chat_messages"]:
        render_chat_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources"),
            metrics=message.get("metrics")
        )

# 4. Sticky Chat Input
prompt = st.chat_input("Ask about this financial document...")

if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    
    with chat_container:
        render_chat_message(role="user", content=prompt)
            
        with st.spinner("FinIntel AI is analyzing financial disclosures..."):
            t0 = time.time()
            rag_res = client.query_rag(document_id=selected_doc_id, question=prompt, top_k=5)
            elapsed = time.time() - t0

            # Race condition verification: ensure document hasn't changed during async processing
            if not is_response_valid(selected_doc_id):
                st.stop()

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
                    "**AI analysis is temporarily unavailable.** "
                    "Please check that the document has completed processing, or try asking about specific line items."
                )
                sources = []
                metrics = {"time": f"{int(elapsed * 1000)}ms", "chunks": 0}
            
            # Render and store assistant response
            render_chat_message(
                role="assistant",
                content=response_text,
                sources=sources,
                metrics=metrics
            )
            
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": response_text,
                "sources": sources,
                "metrics": metrics
            })