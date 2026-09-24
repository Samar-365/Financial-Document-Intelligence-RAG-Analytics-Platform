"""LaserFlow Component - Huly-Inspired Vertical Volumetric Laser Beam.

Implements a single centered vertical laser beam descending from top-center:
- Thin white-hot core extending downward
- Thick crimson atmospheric fog, soft diffusion, and bloom
- Floating photon particles and realistic volumetric depth
- Beam expands and forms an intensely bright focal bloom at the bottom-center
- NO horizontal waves, NO waterfall ribbons, NO crosshairs, NO multiple beams.
"""

import base64
from pathlib import Path
import streamlit.components.v1 as components

_ASSET_CACHE = {}


def _get_asset_b64(filename: str) -> str:
    """Reads and caches image assets as base64 data URIs."""
    if filename not in _ASSET_CACHE:
        asset_path = Path(__file__).resolve().parent.parent / "assets" / filename
        if asset_path.exists():
            with open(asset_path, "rb") as f:
                _ASSET_CACHE[filename] = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        else:
            _ASSET_CACHE[filename] = ""
    return _ASSET_CACHE[filename]


def render_hero_section(
    height: int = 900,
    background_color: str = "#08080A",
):
    """Renders the complete, cinematic FinIntel AI Hero Section with WebGL volumetric laser."""
    b64_balance_sheet = _get_asset_b64("Balance Sheet.png")
    b64_cash_flow = _get_asset_b64("Cash Flow Statement.png")
    b64_income_statement = _get_asset_b64("Income Statement.png")
    b64_auditor_report = _get_asset_b64("Independent Auditor's Report.png")

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>FinIntel AI</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body, html {{
    width: 100%;
    height: 100%;
    background-color: {background_color};
    color: #F1F5F9;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    overflow-x: hidden;
    overflow-y: hidden;
  }}

  /* ── Full Hero Stage Container ── */
  #hero-stage {{
    position: relative;
    width: 100%;
    height: 100vh;
    min-height: 820px;
    background-color: {background_color};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    overflow: hidden;
  }}

  /* ── WebGL Canvas (Behind all hero elements) ── */
  #laser-canvas-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    pointer-events: none;
  }}

  canvas {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100% !important;
    height: 100% !important;
    display: block;
    mix-blend-mode: screen;
  }}

  /* ── 1. Minimal Top Navigation ── */
  .top-nav {{
    position: relative;
    z-index: 20;
    width: 100%;
    max-width: 1280px;
    padding: 22px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .brand-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    cursor: pointer;
  }}

  .brand-icon {{
    background: rgba(184, 29, 36, 0.2);
    border: 1px solid rgba(230, 57, 70, 0.45);
    border-radius: 9px;
    padding: 6px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 16px rgba(184, 29, 36, 0.35);
  }}

  .brand-title {{
    font-size: 1.25rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.025em;
    line-height: 1.1;
  }}

  .brand-title span {{
    color: #E63946;
  }}

  .brand-subtitle {{
    font-size: 0.65rem;
    color: #94A3B8;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}

  .nav-menu {{
    display: flex;
    align-items: center;
    gap: 36px;
    list-style: none;
  }}

  .nav-link {{
    color: #94A3B8;
    font-size: 0.88rem;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.2s ease;
  }}

  .nav-link:hover {{
    color: #FFFFFF;
  }}

  .nav-btn {{
    background: linear-gradient(135deg, #7A121E 0%, #9B111E 50%, #B81D24 100%);
    color: #FFFFFF !important;
    border: 1px solid rgba(230, 57, 70, 0.55);
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    box-shadow: 0 4px 18px rgba(184, 29, 36, 0.35);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .nav-btn:hover {{
    background: linear-gradient(135deg, #9B111E 0%, #B81D24 50%, #E63946 100%);
    box-shadow: 0 6px 24px rgba(230, 57, 70, 0.55);
    transform: translateY(-1px);
  }}

  /* ── 2. Centered Hero Content ── */
  .hero-content {{
    position: relative;
    z-index: 10;
    text-align: center;
    max-width: 960px;
    padding: 0 24px;
    margin-top: 10px;
  }}

  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(184, 29, 36, 0.16);
    border: 1px solid rgba(230, 57, 70, 0.45);
    border-radius: 999px;
    padding: 6px 18px;
    margin-bottom: 22px;
    box-shadow: 0 0 20px rgba(184, 29, 36, 0.25);
  }}

  .badge-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #E63946;
    box-shadow: 0 0 10px #E63946;
  }}

  .badge-text {{
    font-size: 0.72rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}

  .hero-headline {{
    font-size: clamp(2.6rem, 5vw, 3.8rem);
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.035em;
    line-height: 1.12;
    margin-bottom: 20px;
    text-shadow: 0 4px 28px rgba(0, 0, 0, 0.95);
  }}

  /* Crisp, clean reddish gradient text with ZERO glow/shadow */
  .crimson-gradient {{
    background: linear-gradient(135deg, #FF455B 0%, #FF1C35 30%, #E6253B 70%, #FF5267 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    font-weight: 800;
    letter-spacing: -0.02em;
    filter: none !important;
    text-shadow: none !important;
  }}

  .hero-description {{
    font-size: clamp(0.98rem, 1.6vw, 1.15rem);
    color: #94A3B8;
    line-height: 1.62;
    max-width: 720px;
    margin: 0 auto 30px auto;
    font-weight: 400;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95);
  }}

  /* Primary CTA Button: Exact Same Component as Navbar Button */
  .primary-cta-btn {{
    background: linear-gradient(135deg, #7A121E 0%, #9B111E 50%, #B81D24 100%);
    color: #FFFFFF !important;
    border: 1px solid rgba(230, 57, 70, 0.55);
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    box-shadow: 0 4px 18px rgba(184, 29, 36, 0.35);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .primary-cta-btn:hover {{
    background: linear-gradient(135deg, #9B111E 0%, #B81D24 50%, #E63946 100%);
    box-shadow: 0 6px 24px rgba(230, 57, 70, 0.55);
    transform: translateY(-1px);
  }}

  /* ── 2.5 Floating Financial Document Sheets (4 Document Layout) ── */
  .floating-docs-wrapper {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 6;
  }}

  .floating-doc-anchor {{
    position: absolute;
    pointer-events: auto;
    width: clamp(170px, 13vw, 210px);
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  /* • Balance Sheet — upper-left, slightly rotated clockwise, facing inward toward center */
  .doc-balance-sheet {{
    top: 110px;
    left: calc(50% - 635px);
    transform: perspective(1200px) rotateY(15deg) rotateX(6deg) rotateZ(4.5deg);
  }}

  /* • Cash Flow Statement — upper-right, slightly rotated counterclockwise, facing inward */
  .doc-cash-flow {{
    top: 125px;
    right: calc(50% - 640px);
    transform: perspective(1200px) rotateY(-15deg) rotateX(6deg) rotateZ(-5deg);
  }}

  /* • Income Statement — lower-left, slightly rotated counterclockwise, facing inward */
  .doc-income-statement {{
    top: 410px;
    left: calc(50% - 655px);
    transform: perspective(1200px) rotateY(16deg) rotateX(-5deg) rotateZ(-3.5deg) scale(0.96);
  }}

  /* • Independent Auditor’s Report — lower-right, slightly rotated clockwise, facing inward */
  .doc-auditor-report {{
    top: 425px;
    right: calc(50% - 650px);
    transform: perspective(1200px) rotateY(-16deg) rotateX(-5deg) rotateZ(4deg) scale(0.96);
  }}

  /* Floating animations for gentle, desynchronized oscillation */
  .anim-1 {{ animation: floatAnim1 7.6s ease-in-out infinite; }}
  .anim-2 {{ animation: floatAnim2 8.4s ease-in-out infinite 0.7s; }}
  .anim-3 {{ animation: floatAnim3 8.8s ease-in-out infinite 1.4s; }}
  .anim-4 {{ animation: floatAnim4 8.0s ease-in-out infinite 2.1s; }}

  @keyframes floatAnim1 {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
  }}
  @keyframes floatAnim2 {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-12px); }}
  }}
  @keyframes floatAnim3 {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-8px); }}
  }}
  @keyframes floatAnim4 {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-11px); }}
  }}

  /* Physical floating document styling — Transparent background, No borders */
  .floating-doc-card {{
    position: relative;
    border-radius: 0;
    overflow: visible;
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: none !important;
    box-shadow: none !important;
    cursor: default;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  /* Subtle depth blur on documents positioned farther from center */
  .doc-income-statement .floating-doc-card,
  .doc-auditor-report .floating-doc-card {{
    opacity: 0.85;
    filter: blur(0.45px);
  }}

  .doc-balance-sheet .floating-doc-card,
  .doc-cash-flow .floating-doc-card {{
    opacity: 0.92;
  }}

  /* Hover micro-interactions */
  .floating-doc-anchor:hover .floating-doc-card {{
    opacity: 1 !important;
    filter: blur(0px) !important;
    border: none !important;
    box-shadow: none !important;
  }}

  .floating-doc-img {{
    display: block;
    width: 100%;
    height: auto;
    object-fit: cover;
    background: transparent !important;
    border: none !important;
    filter: drop-shadow(0 16px 35px rgba(0, 0, 0, 0.88)) brightness(0.96);
    transition: filter 0.35s ease, transform 0.35s ease;
  }}

  .floating-doc-anchor:hover .floating-doc-img {{
    filter: drop-shadow(0 22px 45px rgba(0, 0, 0, 0.96)) brightness(1.05);
  }}

  /* Responsive screen bounds protection to prevent ever overlapping the headline */
  @media (max-width: 1220px) {{
    .floating-docs-wrapper {{
      display: none !important;
    }}
  }}

  @media (min-width: 1221px) and (max-width: 1420px) {{
    .doc-balance-sheet {{ left: 16px !important; }}
    .doc-cash-flow {{ right: 16px !important; }}
    .doc-income-statement {{ left: 16px !important; }}
    .doc-auditor-report {{ right: 16px !important; }}
  }}

  /* ── 3. Partially Visible Workspace Preview Peeking at Bottom ── */
  .workspace-peek-container {{
    position: relative;
    z-index: 15;
    width: 100%;
    max-width: 1140px;
    padding: 0 24px;
    margin-bottom: -150px; /* Partial emergence at the bottom */
    transition: transform 0.4s ease;
  }}

  .workspace-peek-card {{
    background: #0D0C13;
    border: 1.5px solid rgba(230, 57, 70, 0.5);
    border-bottom: none;
    border-radius: 16px 16px 0 0;
    padding: 16px 20px 180px 20px;
    box-shadow: 0 -18px 60px rgba(184, 29, 36, 0.32), 0 0 100px rgba(0, 0, 0, 0.95);
    position: relative;
    overflow: hidden;
  }}

  /* Glowing focal contact line on the top border */
  .workspace-peek-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 320px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #FFFFFF, #E63946, transparent);
    box-shadow: 0 0 24px 6px rgba(230, 57, 70, 0.85);
  }}

  .window-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 12px;
    margin-bottom: 16px;
  }}

  .window-dots {{
    display: flex;
    gap: 6px;
  }}

  .dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }}
  .dot-red {{ background: #EF4444; }}
  .dot-yellow {{ background: #F59E0B; }}
  .dot-green {{ background: #10B981; }}

  .window-url {{
    background: #08080A;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 3px 22px;
    font-size: 0.72rem;
    color: #94A3B8;
    font-family: monospace;
  }}

  .window-tag {{
    color: #64748B;
    font-size: 0.72rem;
    font-weight: 500;
  }}

  /* Workspace Inner Layout */
  .workspace-layout {{
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 16px;
  }}

  .workspace-sidebar {{
    background: #09080E;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 12px 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .side-label {{
    font-size: 0.65rem;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.05em;
    padding-left: 8px;
    margin-bottom: 6px;
  }}

  .side-item {{
    font-size: 0.78rem;
    color: #94A3B8;
    padding: 6px 10px;
    border-radius: 5px;
  }}

  .side-item.active {{
    background: rgba(184, 29, 36, 0.28);
    color: #FFFFFF;
    font-weight: 600;
    border-left: 3px solid #E63946;
  }}

  .workspace-main {{
    background: #09080E;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  .main-headline-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .main-title {{
    color: #FFFFFF;
    font-size: 0.98rem;
    font-weight: 700;
  }}

  .main-sub {{
    color: #64748B;
    font-size: 0.74rem;
  }}

  .metric-strip {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }}

  .metric-box {{
    background: #12111A;
    border: 1px solid rgba(184, 29, 36, 0.2);
    border-radius: 6px;
    padding: 10px;
  }}

  .metric-label {{
    color: #94A3B8;
    font-size: 0.68rem;
    font-weight: 500;
  }}

  .metric-val {{
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.95rem;
    margin-top: 3px;
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

<div id="hero-stage">
  <!-- WebGL Volumetric Laser Canvas -->
  <div id="laser-canvas-container"></div>

  <!-- Floating Financial Document Sheets (Orbiting Hero) -->
  <div class="floating-docs-wrapper">
    <div class="floating-doc-anchor doc-balance-sheet">
      <div class="floating-doc-anim anim-1">
        <div class="floating-doc-card">
          <img src="{b64_balance_sheet}" alt="Balance Sheet" class="floating-doc-img" />
        </div>
      </div>
    </div>
    <div class="floating-doc-anchor doc-cash-flow">
      <div class="floating-doc-anim anim-2">
        <div class="floating-doc-card">
          <img src="{b64_cash_flow}" alt="Cash Flow Statement" class="floating-doc-img" />
        </div>
      </div>
    </div>
    <div class="floating-doc-anchor doc-income-statement">
      <div class="floating-doc-anim anim-3">
        <div class="floating-doc-card">
          <img src="{b64_income_statement}" alt="Income Statement" class="floating-doc-img" />
        </div>
      </div>
    </div>
    <div class="floating-doc-anchor doc-auditor-report">
      <div class="floating-doc-anim anim-4">
        <div class="floating-doc-card">
          <img src="{b64_auditor_report}" alt="Independent Auditor's Report" class="floating-doc-img" />
        </div>
      </div>
    </div>
  </div>

  <!-- 1. Minimal Top Navigation -->
  <nav class="top-nav">
    <a class="brand-logo" onclick="goToWorkspace()">
      <div class="brand-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E63946" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
      </div>
      <div>
        <div class="brand-title">FinIntel <span>AI</span></div>
        <div class="brand-subtitle">FINANCIAL INTELLIGENCE</div>
      </div>
    </a>

    <ul class="nav-menu">
      <li><a href="#platform" class="nav-link">Platform</a></li>
      <li><a href="#capabilities" class="nav-link">Capabilities</a></li>
      <li><a href="#workflow" class="nav-link">Workflow</a></li>
      <li><a href="#faq" class="nav-link">FAQ</a></li>
    </ul>

    <div>
      <button class="nav-btn" onclick="goToWorkspace()">
        Enter Workspace →
      </button>
    </div>
  </nav>

  <!-- 2. Centered Hero Content -->
  <div class="hero-content">
    <div class="hero-badge">
      <span class="badge-dot"></span>
      <span class="badge-text">FINANCIAL INTELLIGENCE, REDEFINED</span>
    </div>

    <h1 class="hero-headline">
      Turn Complex Financial Documents Into<br />
      <span class="crimson-gradient">Verifiable Intelligence.</span>
    </h1>

    <p class="hero-description">
      Understand financial information, uncover important signals, compare reporting periods, and explore evidence-backed insights from complex corporate filings.
    </p>

    <div style="margin-top: 8px;">
      <button class="primary-cta-btn" onclick="goToWorkspace()">
        Enter Workspace →
      </button>
    </div>
  </div>

  <!-- 3. Partially Visible Workspace Preview -->
  <div class="workspace-peek-container" onclick="goToWorkspace()" style="cursor: pointer;">
    <div class="workspace-peek-card">
      <div class="window-header">
        <div class="window-dots">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
        </div>
        <div class="window-url">app.finintel.ai / workspace / dashboard</div>
        <div class="window-tag">Enterprise SaaS</div>
      </div>

      <div class="workspace-layout">
        <div class="workspace-sidebar">
          <div class="side-label">WORKSPACE</div>
          <div class="side-item active">Dashboard</div>
          <div class="side-item">Upload</div>
          <div class="side-item">Analysis</div>
          <div class="side-item">AI Analyst</div>
          <div class="side-item">Comparison</div>
          <div class="side-item">Audit Logs</div>
        </div>

        <div class="workspace-main">
          <div class="main-headline-bar">
            <div>
              <div class="main-title">Corporate Intelligence Overview</div>
              <div class="main-sub">Multi-format financial extraction, solvency scoring, and verified RAG analysis.</div>
            </div>
          </div>

          <div class="metric-strip">
            <div class="metric-box">
              <div class="metric-label">Financial Indicators</div>
              <div class="metric-val">12 Core Line Items</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Health Dimensions</div>
              <div class="metric-val">5-Pillar Solvency</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Risk Disclosures</div>
              <div class="metric-val">Footnote Signals</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Evidence Citations</div>
              <div class="metric-val">Page-Level Sources</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function goToWorkspace() {{
  try {{
    if (window.parent && window.parent.location) {{
      window.parent.location.pathname = '/Dashboard';
    }} else {{
      window.location.href = '/Dashboard';
    }}
  }} catch (e) {{
    window.location.href = '/Dashboard';
  }}
}}

(function() {{
  const container = document.getElementById('laser-canvas-container');
  const width = container.clientWidth || window.innerWidth;
  const height = container.clientHeight || window.innerHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
  camera.position.z = 1;

  const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true, powerPreference: "high-performance" }});
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const VERT = `
    varying vec2 vUv;
    void main() {{
      vUv = uv;
      gl_Position = vec4(position, 1.0);
    }}
  `;

  // Huly-inspired single vertical laser beam descending from top-center
  // forming an intensely bright focal point bloom at the bottom-center
  const FRAG = `
    precision highp float;
    varying vec2 vUv;
    uniform float uTime;
    uniform vec2 uResolution;

    float hash(vec2 p) {{
      return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
    }}

    void main() {{
      vec2 uv = vUv;
      float t = uTime * 0.35;

      // Distance from vertical centerline
      float dx = abs(uv.x - 0.5);

      // Progress from top (0.0) to bottom (1.0)
      float progress = 1.0 - uv.y;

      // 1. Thin white-hot laser core running down the center
      float coreWidth = 0.0010 + progress * 0.0022;
      float coreDist = dx / coreWidth;
      float core = exp(-coreDist * coreDist * 16.0);

      // 2. Volumetric Beam Waist / Cone (gradually widens and intensifies towards bottom)
      float coneWidth = 0.0035 + pow(smoothstep(0.05, 0.95, progress), 2.1) * 0.24;
      float coneDist = dx / coneWidth;
      float coneGlow = exp(-coneDist * coneDist * 2.4);

      // 3. Intensely bright focal bloom right at the bottom-center contact point
      // Sits right at uv.y ≈ 0.18 where the workspace top border meets the beam
      vec2 focalPt = vec2(0.5, 0.19);
      vec2 dFocal = vec2((uv.x - focalPt.x) * 1.45, (uv.y - focalPt.y) * 2.8);
      float focalDist = length(dFocal);
      float focalBloom = exp(-focalDist * 4.2) * 1.5;

      // Broad ambient crimson glow around the focal strike
      float broadBloom = exp(-focalDist * 1.6) * 0.65;

      // 4. Subtle floating photon particles wafting in the beam
      vec2 pUv = vec2(floor(uv.x * 140.0), floor((uv.y + t * 0.25) * 90.0));
      float pRnd = hash(pUv);
      float particles = step(0.978, pRnd) * exp(-dx * 20.0) * smoothstep(0.1, 0.9, progress) * 0.6;

      // 5. Ambient deep crimson fog throughout the vertical corridor
      float fogCorridor = exp(-dx * 4.2) * (0.28 + 0.12 * sin(progress * 6.0 - t));

      // Color Mixing:
      vec3 deepCrimson = vec3(0.52, 0.04, 0.08);   // #850A14
      vec3 wineRed     = vec3(0.72, 0.11, 0.14);   // #B81D24
      vec3 brightRuby  = vec3(0.95, 0.22, 0.27);   // #F23845
      vec3 whiteHot    = vec3(1.0, 0.97, 0.98);

      // Edge fading to maintain clean framing
      float edgeMask = smoothstep(0.0, 0.06, uv.x) * (1.0 - smoothstep(0.94, 1.0, uv.x));

      vec3 col = vec3(0.0);
      col += deepCrimson * (fogCorridor + broadBloom * 0.8);
      col += wineRed * (coneGlow * 1.1 + focalBloom * 0.7);
      col += brightRuby * (core * 1.3 + focalBloom * 0.9 + particles);
      col += whiteHot * (pow(core, 2.6) * 1.1 + pow(focalBloom, 2.8) * 0.95);

      col *= edgeMask;

      float alpha = clamp(length(col) * 0.9, 0.0, 0.92);
      gl_FragColor = vec4(col, alpha);
    }}
  `;

  const uniforms = {{
    uTime: {{ value: 0.0 }},
    uResolution: {{ value: new THREE.Vector2(width, height) }}
  }};

  const material = new THREE.ShaderMaterial({{
    vertexShader: VERT,
    fragmentShader: FRAG,
    uniforms: uniforms,
    transparent: true,
    blending: THREE.AdditiveBlending
  }});

  const geometry = new THREE.PlaneGeometry(2, 2);
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  function onResize() {{
    const w = container.clientWidth || window.innerWidth;
    const h = container.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    uniforms.uResolution.value.set(w, h);
  }}
  window.addEventListener('resize', onResize);

  let startTime = Date.now();
  function animate() {{
    requestAnimationFrame(animate);
    const elapsed = (Date.now() - startTime) * 0.001;
    uniforms.uTime.value = elapsed;
    renderer.render(scene, camera);
  }}
  animate();
}})();
</script>
</body>
</html>
    """
    components.html(html_code, height=height, scrolling=False)
