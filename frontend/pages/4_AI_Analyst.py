import streamlit as st
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.chat_interface import render_chat_message

st.set_page_config(page_title="AI Analyst | FinIntel AI", layout="wide")

st.title("🤖 AI Financial Analyst")
st.caption("Ask questions about your uploaded financial documents.")

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

processed_docs = [
    doc["Filename"] for doc in st.session_state.get("document_list", [])
    if "PROCESSED" in doc["Status"]
]
doc_options = ["All Documents"] + processed_docs

selected_scope = st.selectbox("Search Context / Document Target:", options=doc_options)
st.divider()

st.subheader("💡 Suggested Questions")

suggestions = [
    "What was the company's revenue in FY2025?",
    "What were the major risks mentioned?",
    "How did EBITDA change compared to last year?",
    "What is the company's debt position?"
]

cols = st.columns(len(suggestions))
for idx, question in enumerate(suggestions):
    if cols[idx].button(question, key=f"sug_{idx}"):
        st.session_state["pending_prompt"] = question
        st.rerun()

st.divider()

st.subheader("💬 Conversation History")

chat_container = st.container()

with chat_container:
    for message in st.session_state["chat_messages"]:
        render_chat_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources"),
            metrics=message.get("metrics")
        )

prompt = st.chat_input("Ask a question about the documents...")

if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    
    with chat_container:
        render_chat_message(role="user", content=prompt)
            
        with st.spinner("Analyzing document context and computing response..."):
            time.sleep(1.2)
            
            mock_response = f"Based on **{selected_scope}**, here is the information regarding '{prompt}': The company maintains a strong financial cushion with stable performance metrics observed."
            mock_sources = [
                {
                    "doc": selected_scope if selected_scope != "All Documents" else "ABC_AR_2025.pdf",
                    "page": 42,
                    "section": "Financial Highlights",
                    "text": "The key operational drivers reflected sustained resilience across operating business units."
                }
            ]
            mock_metrics = {"time": "1.2s", "chunks": 3}
            
            # Render single assistant bubble using modular component
            render_chat_message(
                role="assistant",
                content=mock_response,
                sources=mock_sources,
                metrics=mock_metrics
            )
            
            # Save assistant response to session state
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": mock_response,
                "sources": mock_sources,
                "metrics": mock_metrics
            })