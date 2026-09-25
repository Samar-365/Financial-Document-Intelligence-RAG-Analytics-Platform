import streamlit as st
import sys
from pathlib import Path

st.set_page_config(
    page_title="FinIntel AI — Enterprise Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

sys.path.append(str(Path(__file__).resolve().parent))
from components.theme import apply_theme, get_icon, render_html
from components.laser_flow import render_hero_section

# Apply Pitch Dark & Wine Red styling in Landing Page mode (Zero Sidebar)
apply_theme(is_landing_page=True)

# ─────────────────────────────────────────────────────────────
# 1. FININTEL AI — CINEMATIC ENTERPRISE HERO SECTION
# ─────────────────────────────────────────────────────────────
render_hero_section(
    height=860,
    background_color="#08080A",
)

# ─────────────────────────────────────────────────────────────
# 2. LANDING PAGE CONTENT (BELOW 100vh FIRST VIEWPORT FOLD)
# ─────────────────────────────────────────────────────────────
render_html('<div class="landing-content-container">')

render_html("""<div id="capabilities" style="margin-top: 10px;"></div>""")

render_html("""
<div style="text-align: center; margin-bottom: 36px;">
    <div style="font-size: 0.74rem; font-weight: 700; color: #E63946; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px;">
        CORE CAPABILITIES
    </div>
    <h2 style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; margin: 0 0 10px 0;">
        One intelligence layer for complex financial filings.
    </h2>
    <p style="color: #94A3B8; font-size: 0.98rem; max-width: 680px; margin: 0 auto; line-height: 1.55;">
        Transform lengthy disclosures and spreadsheets into structured indicators, solvency ratings, and verifiable answers.
    </p>
</div>
""")

cap_c1, cap_c2, cap_c3 = st.columns(3)

icon_ingest = get_icon("file-text", color="#E63946", size=22)
with cap_c1:
    render_html(f"""
    <div style="background: #111017; border: 1px solid rgba(184, 29, 36, 0.22); border-radius: 14px; padding: 26px; height: 100%;">
        <div style="background: rgba(184, 29, 36, 0.15); border: 1px solid rgba(184, 29, 36, 0.3); border-radius: 8px; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px;">
            {icon_ingest}
        </div>
        <div style="color: #E63946; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">INGESTION</div>
        <h3 style="font-size: 1.18rem; font-weight: 700; color: #FFFFFF; margin: 0 0 10px 0;">Multi-Format Ingestion</h3>
        <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.6; margin: 0;">
            Ingest corporate PDFs, annual reports, 10-K/10-Q filings, spreadsheets (CSV, Excel), and balance sheets into clean, structured tables without manual re-keying.
        </p>
    </div>
    """)

icon_health = get_icon("pie-chart", color="#E63946", size=22)
with cap_c2:
    render_html(f"""
    <div style="background: #111017; border: 1px solid rgba(184, 29, 36, 0.22); border-radius: 14px; padding: 26px; height: 100%;">
        <div style="background: rgba(184, 29, 36, 0.15); border: 1px solid rgba(184, 29, 36, 0.3); border-radius: 8px; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px;">
            {icon_health}
        </div>
        <div style="color: #E63946; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">EVALUATION</div>
        <h3 style="font-size: 1.18rem; font-weight: 700; color: #FFFFFF; margin: 0 0 10px 0;">5D Financial Health</h3>
        <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.6; margin: 0;">
            Automatically extract 12 core line items, compute ratios, and assess corporate solvency across Growth, Profitability, Liquidity, Leverage, and Cash Flow.
        </p>
    </div>
    """)

icon_ai = get_icon("bot", color="#E63946", size=22)
with cap_c3:
    render_html(f"""
    <div style="background: #111017; border: 1px solid rgba(184, 29, 36, 0.22); border-radius: 14px; padding: 26px; height: 100%;">
        <div style="background: rgba(184, 29, 36, 0.15); border: 1px solid rgba(184, 29, 36, 0.3); border-radius: 8px; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px;">
            {icon_ai}
        </div>
        <div style="color: #E63946; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">VERIFICATION</div>
        <h3 style="font-size: 1.18rem; font-weight: 700; color: #FFFFFF; margin: 0 0 10px 0;">Audit-Grounded Inquiry</h3>
        <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.6; margin: 0;">
            Explore questions conversationally with exact page-level citations and verbatim excerpts from source filings for complete transparency.
        </p>
    </div>
    """)

# ─────────────────────────────────────────────────────────────
# 3. THE WORKFLOW (MINIMAL 4-STAGE PIPELINE)
# ─────────────────────────────────────────────────────────────
render_html("""<div id="workflow" style="margin-top: 50px;"></div>""")

render_html("""
<div style="background: #0D0C13; border: 1px solid rgba(184, 29, 36, 0.2); border-radius: 14px; padding: 32px 28px; margin-bottom: 50px;">
    <div style="text-align: center; margin-bottom: 24px;">
        <span style="font-size: 0.74rem; font-weight: 700; color: #E63946; letter-spacing: 0.08em; text-transform: uppercase;">THE WORKFLOW</span>
        <div style="color: #FFFFFF; font-size: 1.35rem; font-weight: 800; margin-top: 4px;">From raw filings to verifiable understanding.</div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
        <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.06); padding-right: 12px;">
            <div style="color: #E63946; font-size: 0.75rem; font-weight: 800; margin-bottom: 4px;">01</div>
            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Upload Filings</div>
            <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">Ingest corporate PDFs, CSV, or spreadsheets.</div>
        </div>
        <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.06); padding-right: 12px;">
            <div style="color: #E63946; font-size: 0.75rem; font-weight: 800; margin-bottom: 4px;">02</div>
            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Extract Line Items</div>
            <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">Automated extraction of revenue, margins, and debt.</div>
        </div>
        <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.06); padding-right: 12px;">
            <div style="color: #E63946; font-size: 0.75rem; font-weight: 800; margin-bottom: 4px;">03</div>
            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Analyze &amp; Compare</div>
            <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">5D health scoring and period-over-period variance.</div>
        </div>
        <div style="text-align: center;">
            <div style="color: #E63946; font-size: 0.75rem; font-weight: 800; margin-bottom: 4px;">04</div>
            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Verifiable Insights</div>
            <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">Grounded analysis backed by exact page citations.</div>
        </div>
    </div>
</div>
""")

# ─────────────────────────────────────────────────────────────
# 4. TRACEABLE INTELLIGENCE PREVIEW (EVIDENCE CHAIN)
# ─────────────────────────────────────────────────────────────
render_html("""
<div style="background: #111017; border: 1px solid rgba(184, 29, 36, 0.25); border-radius: 14px; padding: 28px; margin-bottom: 50px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 24px; margin-bottom: 20px;">
        <div>
            <div style="font-size: 0.74rem; font-weight: 700; color: #E63946; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;">TRACEABILITY</div>
            <h3 style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin: 0;">Intelligence you can trace back to the source.</h3>
        </div>
        <div style="color: #94A3B8; font-size: 0.85rem; max-width: 440px; line-height: 1.5;">
            Every response generated in the workspace links directly to filing chapters, footnote disclosures, and verified page numbers.
        </div>
    </div>

    <div style="background: #0B0A0F; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 18px;">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px; margin-bottom: 12px;">
            <span style="color: #FFFFFF; font-size: 0.86rem; font-weight: 600;">Sample Query: Liquidity &amp; Debt Risk Overview</span>
            <span style="background: rgba(184, 29, 36, 0.2); color: #E63946; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Citations Grounded</span>
        </div>
        <div style="color: #CBD5E1; font-size: 0.82rem; line-height: 1.5; margin-bottom: 14px;">
            Core liquidity reserves comfortably exceed short-term maturities, supported by positive operational cash flows. Disclosed risks highlight interest rate sensitivities on floating-rate credit facilities.
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <div style="background: #14131D; border: 1px solid rgba(184, 29, 36, 0.25); border-radius: 6px; padding: 6px 12px; font-size: 0.75rem; color: #CBD5E1;">
                Source: <b>Annual Report — Liquidity Disclosures</b> <span style="color: #E63946; margin-left: 6px;">Page 72</span>
            </div>
            <div style="background: #14131D; border: 1px solid rgba(184, 29, 36, 0.25); border-radius: 6px; padding: 6px 12px; font-size: 0.75rem; color: #CBD5E1;">
                Source: <b>Consolidated Statements — Note 14: Debt</b> <span style="color: #E63946; margin-left: 6px;">Page 85</span>
            </div>
            <div style="background: #14131D; border: 1px solid rgba(184, 29, 36, 0.25); border-radius: 6px; padding: 6px 12px; font-size: 0.75rem; color: #CBD5E1;">
                Source: <b>MD&amp;A Financial Condition</b> <span style="color: #E63946; margin-left: 6px;">Page 102</span>
            </div>
        </div>
    </div>
</div>
""")

# ─────────────────────────────────────────────────────────────
# 5. FOCUSED ENTERPRISE FAQ
# ─────────────────────────────────────────────────────────────
render_html("""<div id="faq"></div>""")

render_html("""
<div style="margin-bottom: 20px;">
    <div style="font-size: 0.74rem; font-weight: 700; color: #E63946; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">
        FAQ
    </div>
    <h2 style="font-size: 1.85rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; margin: 0 0 16px 0;">
        Frequently asked questions.
    </h2>
</div>
""")

faq_col1, faq_col2 = st.columns(2)

with faq_col1:
    with st.expander("What types of financial documents can FinIntel AI analyze?"):
        st.write(
            "FinIntel AI analyzes corporate financial reports, including annual reports, quarterly filings (10-K, 10-Q), "
            "earnings releases, financial schedules, as well as structured spreadsheet files (CSV and Microsoft Excel workbooks). "
            "Tables and narratives are parsed into structured formats for automated indicator extraction."
        )

    with st.expander("How does the platform support evidence-backed analysis?"):
        st.write(
            "Every analytical statement and metric extracted by FinIntel AI is grounded in the underlying source material. "
            "When exploring questions through the AI Analyst, each answer provides direct citations pointing to the specific "
            "document title, section heading, and page number from which the information was derived."
        )

with faq_col2:
    with st.expander("How does financial health analysis work?"):
        st.write(
            "Financial health is evaluated across five fundamental dimensions: Growth, Profitability, Liquidity, Leverage, "
            "and Cash Flow. These dimensions synthesize audited line items (such as operating margins, current ratio, and debt-to-equity) "
            "into a structured analytical assessment to understand stability."
        )

    with st.expander("Can I compare different reporting periods?"):
        st.write(
            "Yes. The platform includes a dedicated comparative analysis module where you can select two reporting periods "
            "(such as FY2024 vs FY2025). The system calculates percentage variances across revenue, margins, debt, and cash flow, "
            "highlighting operational evolution between periods."
        )

# ─────────────────────────────────────────────────────────────
# 6. FINAL SPACIOUS CALL-TO-ACTION
# ─────────────────────────────────────────────────────────────
render_html("""
<div style="background: radial-gradient(circle at center, #1B0C11 0%, #0B0A0F 80%); border: 1px solid rgba(196, 30, 58, 0.35); border-radius: 14px; padding: 44px 20px; text-align: center; margin: 50px 0 34px 0; box-shadow: 0 10px 40px rgba(0,0,0,0.6);">
    <h2 style="font-size: 2.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; margin: 0 0 10px 0;">
        Turn financial complexity into clarity.
    </h2>
    <p style="color: #94A3B8; font-size: 0.98rem; max-width: 680px; margin: 0 auto 24px auto; line-height: 1.55;">
        Explore financial documents, understand the numbers, investigate important signals, and follow insights back to their source.
    </p>
</div>
""")

cta_sp1, cta_btn_col, cta_sp2 = st.columns([4.2, 3.6, 4.2])
with cta_btn_col:
    render_html("""
    <div style="text-align: center;">
        <a href="/Dashboard" target="_top" style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            background: linear-gradient(180deg, #E62538 0%, #B81424 45%, #850B17 100%);
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 175, 190, 0.75);
            border-radius: 9px;
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: -0.01em;
            padding: 11px 24px;
            text-decoration: none;
            box-shadow: 
                inset 0 1px 2px rgba(255, 255, 255, 0.75),
                inset 0 -2px 5px rgba(0, 0, 0, 0.55),
                0 0 32px rgba(255, 35, 60, 0.5),
                0 8px 24px rgba(0, 0, 0, 0.7);
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        ">
            Enter Workspace →
        </a>
    </div>
    """)

# ─────────────────────────────────────────────────────────────
# 7. MINIMAL ENTERPRISE FOOTER
# ─────────────────────────────────────────────────────────────
render_html("<div style='height: 24px;'></div>")

footer_c1, footer_c2 = st.columns([6, 5])

icon_brand_small = get_icon("activity", color="#E63946", size=18)
with footer_c1:
    render_html(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
        <div style="background: rgba(184, 29, 36, 0.2); border: 1px solid rgba(230, 57, 70, 0.4); border-radius: 6px; padding: 4px; display: flex; align-items: center; justify-content: center;">
            {icon_brand_small}
        </div>
        <div>
            <span style="font-size: 1.0rem; font-weight: 800; color: #FFFFFF;">FinIntel AI</span>
        </div>
    </div>
    <div style="color: #64748B; font-size: 0.75rem;">
        Enterprise Financial Intelligence &amp; Audit-Grade Analytics
    </div>
    """)

with footer_c2:
    render_html("""
    <div style="display: flex; justify-content: flex-end; gap: 28px; font-size: 0.85rem; padding-top: 10px;">
        <a href="#capabilities" style="color: #94A3B8; text-decoration: none;">Capabilities</a>
        <a href="#workflow" style="color: #94A3B8; text-decoration: none;">Workflow</a>
        <a href="#faq" style="color: #94A3B8; text-decoration: none;">FAQ</a>
    </div>
    """)

render_html("""
<div style="border-top: 1px solid rgba(255,255,255,0.06); margin-top: 20px; padding-top: 16px; display: flex; justify-content: space-between; color: #64748B; font-size: 0.75rem;">
    <div>&copy; 2026 FinIntel AI. All rights reserved.</div>
    <div>Financial intelligence for complex documents.</div>
</div>
""")

render_html('</div>')

# Explicitly terminate execution: the landing page strictly ends here.
st.stop()