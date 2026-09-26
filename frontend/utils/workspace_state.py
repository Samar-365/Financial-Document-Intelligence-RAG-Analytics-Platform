"""Canonical Workspace State Management for FinIntel AI.

Provides:
1. Single source of truth for `active_doc_id` across Dashboard, Analysis, AI Analyst, and Comparison.
2. Controlled document switching flow that clears stale derived metrics and activates skeleton loaders.
3. Race-condition protection: ensures async/API responses belong to the currently active document.
4. Clean, unified document selector formatting (Company — Period — Currency • Status).
5. Clickable FinIntel sidebar branding with SVG logo navigating back to landing page.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from components.theme import get_icon, render_html

ACTIVE_DOC_KEY = "active_doc_id"
DOC_LOADING_KEY = "document_loading"
LAST_DOC_KEY = "last_rendered_doc_id"


def get_active_doc_id() -> Optional[str]:
    """Retrieves the single canonical active document ID from session state."""
    # Check both active_doc_id and legacy selected_doc_id
    doc_id = st.session_state.get(ACTIVE_DOC_KEY) or st.session_state.get("selected_doc_id")
    if doc_id:
        doc_id = str(doc_id)
        st.session_state[ACTIVE_DOC_KEY] = doc_id
        st.session_state["selected_doc_id"] = doc_id
    return doc_id


def set_active_doc_id(doc_id: str) -> None:
    """Sets active document ID, clears stale derived data, and triggers clean state transition."""
    if not doc_id:
        return
    doc_id = str(doc_id)
    prev_id = get_active_doc_id()

    if prev_id != doc_id:
        # Document switched: clear stale derived state across all workspace views
        st.session_state[ACTIVE_DOC_KEY] = doc_id
        st.session_state["selected_doc_id"] = doc_id
        
        # Clear stale metrics/ratios caches in session state
        st.session_state.pop("cached_metrics", None)
        st.session_state.pop("cached_ratios", None)
        st.session_state.pop("cached_health", None)
        
        # Invalidate API client cache to guarantee fresh fetch
        try:
            from utils.api_client import invalidate_financial_cache
            invalidate_financial_cache()
        except Exception:
            pass

        # Clear AI chat conversation to prevent cross-document hallucinations
        st.session_state["chat_messages"] = []
        st.session_state["last_chat_doc_id"] = doc_id
        
        # Flag loading state to display skeleton placeholders
        st.session_state[DOC_LOADING_KEY] = True


def mark_document_loaded(doc_id: str) -> None:
    """Marks document loading complete once data for doc_id is verified."""
    if str(doc_id) == str(get_active_doc_id()):
        st.session_state[DOC_LOADING_KEY] = False
        st.session_state[LAST_DOC_KEY] = str(doc_id)


def is_response_valid(response_doc_id: Optional[str]) -> bool:
    """Race condition guard: validates that response corresponds to the currently active document."""
    active_id = get_active_doc_id()
    if not active_id or not response_doc_id:
        return False
    return str(response_doc_id) == str(active_id)


def format_doc_label(doc: Dict[str, Any]) -> str:
    """Formats clean, informative selector label: Company — Period — Currency • Status."""
    filename = doc.get("filename", "Document.pdf")
    company = doc.get("company_name")
    if not company:
        company = filename.rsplit(".", 1)[0]
    
    # Format period
    period = doc.get("fiscal_period", "")
    year = doc.get("fiscal_year", "")
    if period and year and period != "FY":
        period_str = f"{period} FY{year}"
    elif year:
        period_str = f"FY{year}"
    elif period:
        period_str = period
    else:
        period_str = "Full Filing"

    # Detect currency hint
    currency_hint = "INR" if ("inr" in filename.lower() or "tcs" in filename.lower() or "infosys" in filename.lower()) else "USD"

    # Clean truncated filename
    clean_fn = filename[:22] + "..." if len(filename) > 22 else filename

    status = doc.get("status", "PROCESSED")
    status_display = "Processed" if status.upper() == "PROCESSED" else status.capitalize()

    return f"{company} — {period_str} — {currency_hint} • {status_display} ({clean_fn})"


def render_workspace_sidebar_branding():
    """Renders the official clickable FININTEL branding in the Streamlit sidebar."""
    with st.sidebar:
        icon_brand = get_icon("activity", color="#E63946", size=20)
        render_html(f"""
<div class="finintel-brand-container">
    <a href="/" target="_top" class="finintel-brand-link">
        <div class="finintel-brand-badge">
            {icon_brand}
        </div>
        <div class="finintel-brand-details">
            <div class="finintel-brand-name">FININTEL <span class="finintel-brand-red">AI</span></div>
            <div class="finintel-brand-sub">Financial Intelligence</div>
        </div>
    </a>
</div>
""")


def render_document_selector(documents: List[Dict[str, Any]], key_prefix: str = "workspace") -> Dict[str, Any]:
    """Renders unified document selector dropdown and synchronizes canonical state."""
    if not documents:
        return {}

    # Build options mapping
    options_map = {}
    id_to_label = {}
    for d in documents:
        lbl = format_doc_label(d)
        options_map[lbl] = d
        id_to_label[str(d.get("id"))] = lbl

    active_id = get_active_doc_id()
    default_label = None

    if active_id and active_id in id_to_label:
        default_label = id_to_label[active_id]
    elif documents:
        # Default to first document
        default_label = list(options_map.keys())[0]
        set_active_doc_id(str(documents[0].get("id")))

    options_list = list(options_map.keys())
    default_idx = options_list.index(default_label) if default_label in options_list else 0

    select_key = f"{key_prefix}_doc_selector"

    # CRITICAL: Keep select_key synchronized with canonical active_id across all pages
    if default_label and (select_key not in st.session_state or st.session_state.get(select_key) != default_label):
        st.session_state[select_key] = default_label

    # Callback when user changes selection
    def on_change():
        chosen_lbl = st.session_state.get(select_key)
        chosen_doc = options_map.get(chosen_lbl)
        if chosen_doc:
            set_active_doc_id(str(chosen_doc.get("id")))

    selected_label = st.selectbox(
        "Active Filing Workspace:",
        options=options_list,
        index=default_idx,
        key=select_key,
        on_change=on_change,
        help="Select a financial filing to synchronize metrics, health scores, and AI analyst context."
    )

    selected_doc = options_map.get(selected_label) or (documents[0] if documents else {})
    new_id = str(selected_doc.get("id"))
    
    if new_id != get_active_doc_id():
        set_active_doc_id(new_id)

    return selected_doc


def render_skeleton_kpis():
    """Renders sleek pitch-dark shimmering skeleton loaders for KPI cards."""
    cols = st.columns(5)
    labels = ["Revenue", "Operating Income", "Net Income", "Total Debt", "Operating Cash Flow"]
    for i, col in enumerate(cols):
        with col:
            render_html(f"""
<div style="
    background: #111017;
    border: 1px solid rgba(196, 30, 58, 0.2);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
">
    <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 500; margin-bottom: 8px;">{labels[i]}</div>
    <div class="skeleton-shimmer" style="width: 75%; height: 26px; border-radius: 6px; margin-bottom: 8px;"></div>
    <div class="skeleton-shimmer" style="width: 45%; height: 14px; border-radius: 4px;"></div>
</div>
""")


def render_skeleton_banner():
    """Renders shimmering skeleton loader for filing metadata banner."""
    render_html("""
<div style="
    background: #111017;
    border: 1px solid rgba(196, 30, 58, 0.2);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
">
    <div style="flex: 1;"><div class="skeleton-shimmer" style="width: 80%; height: 18px;"></div></div>
    <div style="flex: 1;"><div class="skeleton-shimmer" style="width: 60%; height: 18px;"></div></div>
    <div style="flex: 1;"><div class="skeleton-shimmer" style="width: 50%; height: 18px;"></div></div>
    <div style="flex: 1;"><div class="skeleton-shimmer" style="width: 70%; height: 18px;"></div></div>
</div>
""")


def render_skeleton_charts():
    """Renders sleek shimmering placeholder cards for charts and analysis views."""
    render_html("""
<div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px; margin-bottom: 24px;">
    <div style="background: #111017; border: 1px solid rgba(196, 30, 58, 0.2); border-radius: 12px; padding: 24px; text-align: center;">
        <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px;">Corporate Health Score</div>
        <div class="skeleton-shimmer" style="width: 160px; height: 160px; border-radius: 50%; margin: 0 auto 16px auto;"></div>
        <div class="skeleton-shimmer" style="width: 50%; height: 18px; margin: 0 auto;"></div>
    </div>
    <div style="background: #111017; border: 1px solid rgba(196, 30, 58, 0.2); border-radius: 12px; padding: 24px;">
        <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px;">5-Dimension Performance Radar</div>
        <div class="skeleton-shimmer" style="width: 100%; height: 210px; border-radius: 8px;"></div>
    </div>
</div>
<div style="background: #111017; border: 1px solid rgba(196, 30, 58, 0.2); border-radius: 12px; padding: 24px; margin-bottom: 20px;">
    <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px;">Financial Statement Visualization Bridge</div>
    <div class="skeleton-shimmer" style="width: 100%; height: 240px; border-radius: 8px;"></div>
</div>
""")
