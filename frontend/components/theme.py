"""Pitch Dark & Wine Red Theme with Modern Lucide SVG Icon System.

Delivers a state-of-the-art luxury dark aesthetic with deep wine/burgundy accents
and clean, professional Lucide vector icons to completely eliminate generic OS emojis.
"""

import re
import streamlit as st

# ─────────────────────────────────────────────────────────────
# LUCIDE SVG ICONS REGISTRY
# ─────────────────────────────────────────────────────────────
LUCIDE_ICONS = {
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "upload": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>',
    "file-text": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    "bot": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>',
    "git-compare": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><path d="M11 18H8a2 2 0 0 1-2-2V9"/></svg>',
    "shield-check": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    "trending-up": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "dollar-sign": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "pie-chart": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "layers": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-9.17 4.16a2 2 0 0 1-1.66 0L2 12.5"/><path d="m22 17.5-9.17 4.16a2 2 0 0 1-1.66 0L2 17.5"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>',
    "check-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "alert-triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "message-square": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>',
    "arrow-up-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>',
    "arrow-down-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 7 10 10"/><path d="M17 7v10H7"/></svg>',
    "minus": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>',
    "book-open": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "bar-chart": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
    "target": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "waveform": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10v4"/><path d="M6 7v10"/><path d="M10 4v16"/><path d="M14 8v8"/><path d="M18 5v14"/><path d="M22 11v2"/></svg>',
}


def get_icon(name: str, color: str = "#E63946", size: int = 20) -> str:
    """Returns an inline Lucide SVG string with specified color and size."""
    template = LUCIDE_ICONS.get(name.lower(), LUCIDE_ICONS["activity"])
    return template.format(color=color, size=size)


def render_html(html_code: str):
    """Renders HTML in Streamlit ensuring no leading indentation or comments cause markdown code block parsing."""
    # Strip HTML comments entirely
    no_comments = re.sub(r'<!--.*?-->', '', html_code, flags=re.DOTALL)
    # Strip leading/trailing spaces from each line, skip empty lines
    cleaned_lines = [line.strip() for line in no_comments.splitlines() if line.strip()]
    cleaned_html = " ".join(cleaned_lines)
    st.markdown(cleaned_html, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "", icon_name: str = "activity"):
    """Renders a luxurious Pitch Dark & Wine Red header with vector Lucide icon."""
    svg = get_icon(icon_name, color="#E63946", size=26)
    sub_tag = f'<div style="margin: 4px 0 16px 0; color: #94A3B8; font-size: 0.95rem; font-weight: 400; line-height: 1.5;">{subtitle}</div>' if subtitle else ""
    header_html = f"""
<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 4px; padding-top: 2px;">
    <div style="background: rgba(184, 29, 36, 0.15); border: 1px solid rgba(196, 30, 58, 0.4); border-radius: 10px; padding: 8px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(184, 29, 36, 0.2);">
        {svg}
    </div>
    <div style="margin: 0; font-size: 1.85rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
        {title}
    </div>
</div>
{sub_tag}
"""
    render_html(header_html)


# ─────────────────────────────────────────────────────────────
# PITCH DARK & WINE RED GLOBAL CSS INJECTION
# ─────────────────────────────────────────────────────────────
def apply_theme(is_landing_page: bool = False):
    """Injects high-fidelity Pitch Dark and Wine Red CSS across the Streamlit app.
    
    If is_landing_page=True:
        Hides the Streamlit sidebar, top navigation, and header entirely for a full-width public SaaS presentation.
    If is_landing_page=False:
        Shows the sidebar containing exactly the 6 authenticated workspace tabs, hiding any 'app' root links.
    """
    sidebar_landing_css = """
    /* Hide Streamlit Sidebar entirely on the public landing page */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    header[data-testid="stHeader"],
    .stApp > header {
        display: none !important;
        visibility: hidden !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1340px !important;
        margin: 0 auto !important;
    }
    """ if is_landing_page else """
    /* Authenticated Workspace: Show sidebar with 6 navigation items, hide root app */
    [data-testid="stSidebar"] {
        background-color: #0D0C12 !important;
        border-right: 1px solid rgba(184, 29, 36, 0.25) !important;
        display: block !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    
    /* Ensure the root 'app.py' doesn't show in the workspace navigation */
    [data-testid="stSidebarNav"] li:has(a[href="/"]),
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    """

    css = f"""
    <style>
    /* 1. Global Page Backgrounds */
    .stApp {{
        background-color: #08080A !important;
        color: #F1F5F9 !important;
    }}
    
    {sidebar_landing_css}
    
    /* 2. Containers & Cards (Pitch Dark with Wine Red Accents) */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #111017 !important;
        border: 1px solid rgba(196, 30, 58, 0.24) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.2s ease-in-out;
    }}

    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: rgba(230, 57, 70, 0.45) !important;
        box-shadow: 0 6px 24px rgba(184, 29, 36, 0.18) !important;
    }}

    /* 3. Primary & Secondary Buttons with Metallic Flare Finish */
    button[kind="primary"], button[data-testid="baseButton-primary"] {{
        background: linear-gradient(180deg, #E62538 0%, #B81424 45%, #850B17 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 175, 190, 0.75) !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        box-shadow: 
            inset 0 1px 2px rgba(255, 255, 255, 0.75),
            inset 0 -2px 5px rgba(0, 0, 0, 0.55),
            0 0 32px rgba(255, 35, 60, 0.5),
            0 8px 24px rgba(0, 0, 0, 0.7) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
        background: linear-gradient(180deg, #FF384D 0%, #D41A2D 45%, #9E0F1D 100%) !important;
        box-shadow: 
            inset 0 1px 3px rgba(255, 255, 255, 0.95),
            inset 0 -2px 6px rgba(0, 0, 0, 0.5),
            0 0 42px rgba(255, 42, 66, 0.8),
            0 10px 30px rgba(0, 0, 0, 0.85) !important;
        transform: translateY(-2px) !important;
        border-color: rgba(255, 210, 225, 0.95) !important;
    }}

    button[kind="secondary"], button[data-testid="baseButton-secondary"] {{
        background-color: #14131D !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(184, 29, 36, 0.32) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}

    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {{
        border-color: #E63946 !important;
        color: #FFFFFF !important;
        background-color: #1C1A27 !important;
    }}

    /* 4. Inputs, TextAreas, and Selectboxes */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    .stTextInput input,
    .stNumberInput input,
    input[type="text"],
    textarea {{
        background-color: #14131D !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(184, 29, 36, 0.35) !important;
        border-radius: 8px !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }}

    div[data-baseweb="input"] input:focus,
    div[data-baseweb="base-input"] input:focus,
    .stTextInput input:focus,
    textarea:focus {{
        border-color: #E63946 !important;
        box-shadow: 0 0 12px rgba(230, 57, 70, 0.35) !important;
        background-color: #181724 !important;
    }}

    /* Selectbox containers & Dropdown Menus */
    div[data-baseweb="select"] > div {{
        background-color: #14131D !important;
        border: 1px solid rgba(184, 29, 36, 0.35) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }}

    ul[role="listbox"],
    div[role="listbox"],
    div[data-baseweb="popover"] > div {{
        background-color: #14131D !important;
        border: 1px solid rgba(196, 30, 58, 0.35) !important;
        color: #F8FAFC !important;
    }}

    li[role="option"] {{
        background-color: #14131D !important;
        color: #F8FAFC !important;
    }}

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: rgba(184, 29, 36, 0.25) !important;
        color: #FFFFFF !important;
    }}

    /* 5. Metrics & Numbers Styling */
    div[data-testid="stMetricValue"] {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 0 12px rgba(230, 57, 70, 0.25);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #94A3B8 !important;
        font-weight: 500 !important;
    }}

    /* 6. Tabs & Badges */
    button[data-baseweb="tab"] {{
        color: #94A3B8 !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #E63946 !important;
        border-bottom-color: #E63946 !important;
        font-weight: 600 !important;
    }}

    /* 7. File Uploader Container */
    div[data-testid="stFileUploader"] section {{
        background-color: #111018 !important;
        border: 2px dashed rgba(184, 29, 36, 0.45) !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stFileUploader"] section:hover {{
        border-color: #E63946 !important;
        background-color: #171522 !important;
    }}

    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small {{
        color: #CBD5E1 !important;
    }}

    /* 8. Dataframe Table Styling */
    .stDataFrame, [data-testid="stDataFrame"], [data-testid="stTable"] {{
        background-color: #111017 !important;
        border: 1px solid rgba(184, 29, 36, 0.28) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}

    [data-testid="stDataFrame"] * {{
        background-color: transparent;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background-color: #111017 !important;
        border: 1px solid rgba(184, 29, 36, 0.22) !important;
        border-radius: 10px !important;
    }}

    details summary {{
        color: #F1F5F9 !important;
        font-weight: 600 !important;
    }}

    /* Dividers */
    hr {{
        border-color: rgba(184, 29, 36, 0.18) !important;
        margin: 28px 0 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
