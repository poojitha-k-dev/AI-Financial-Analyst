"""
Global CSS theme for FinanceAI — dark, professional, Bloomberg-inspired.
"""

GLOBAL_CSS = """
<style>
/* ── Google Fonts ──────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ────────────────────────────────────────────────── */
:root {
    --bg-primary:    #060b17;
    --bg-secondary:  #0d1526;
    --bg-card:       #111827;
    --bg-card-hover: #1a2333;
    --border:        #1f2d45;
    --border-bright: #2d4060;
    --accent:        #3b82f6;
    --accent-2:      #6366f1;
    --accent-green:  #10b981;
    --accent-red:    #ef4444;
    --accent-yellow: #f59e0b;
    --accent-purple: #8b5cf6;
    --text-primary:  #f1f5f9;
    --text-secondary:#94a3b8;
    --text-muted:    #64748b;
    --gradient-main: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    --gradient-green:linear-gradient(135deg, #10b981 0%, #059669 100%);
    --gradient-red:  linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    --shadow-card:   0 4px 24px rgba(0,0,0,0.4);
    --radius:        12px;
    --radius-sm:     8px;
}

/* ── Base ───────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Hide Streamlit branding ─────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Metric cards ───────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-card) !important;
    transition: border-color 0.2s, transform 0.15s !important;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-bright) !important;
    transform: translateY(-1px) !important;
}
[data-testid="metric-container"] label {
    color: var(--text-secondary) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.55rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Buttons ────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--gradient-main) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.2rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiselect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius) var(--radius) 0 0 !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* ── Expander ───────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── DataFrames ─────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────── */
.stSuccess { background: rgba(16,185,129,0.1) !important; border-left: 3px solid var(--accent-green) !important; }
.stError   { background: rgba(239,68,68,0.1)  !important; border-left: 3px solid var(--accent-red)   !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border-left: 3px solid var(--accent-yellow) !important; }
.stInfo    { background: rgba(59,130,246,0.1) !important; border-left: 3px solid var(--accent)       !important; }

/* ── Divider ────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Sidebar radio ──────────────────────────────────────────────────── */
.stRadio > label { display: none !important; }
.stRadio > div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.stRadio > div > label {
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 0.9rem !important;
    cursor: pointer !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    color: var(--text-secondary) !important;
    transition: background 0.15s, color 0.15s !important;
}
.stRadio > div > label:hover {
    background: rgba(59,130,246,0.08) !important;
    color: var(--text-primary) !important;
}
.stRadio > div > label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* ── Progress bar ───────────────────────────────────────────────────── */
.stProgress > div > div > div { background: var(--gradient-main) !important; }

/* ── Spinner ────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── File uploader ──────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-bright); }

/* ── Custom utility classes ─────────────────────────────────────────── */
.fin-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-card);
    margin-bottom: 0.75rem;
}
.fin-card-accent {
    border-left: 3px solid var(--accent);
}
.fin-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-green  { background: rgba(16,185,129,0.15); color: #10b981; }
.badge-red    { background: rgba(239,68,68,0.15);  color: #ef4444; }
.badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; }
.badge-blue   { background: rgba(59,130,246,0.15); color: #3b82f6; }
.badge-purple { background: rgba(139,92,246,0.15); color: #8b5cf6; }
.badge-grey   { background: rgba(100,116,139,0.15);color: #94a3b8; }

.page-header {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid var(--accent);
}
.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}
.risk-pill-high   { background:rgba(239,68,68,0.15);  color:#ef4444; padding:3px 12px; border-radius:999px; font-weight:600; font-size:0.8rem; }
.risk-pill-medium { background:rgba(245,158,11,0.15); color:#f59e0b; padding:3px 12px; border-radius:999px; font-weight:600; font-size:0.8rem; }
.risk-pill-low    { background:rgba(16,185,129,0.15); color:#10b981; padding:3px 12px; border-radius:999px; font-weight:600; font-size:0.8rem; }
.risk-pill-critical{ background:rgba(220,38,38,0.2);  color:#dc2626; padding:3px 12px; border-radius:999px; font-weight:700; font-size:0.8rem; }

.chat-bubble-user {
    background: linear-gradient(135deg, #1e3a5f, #1e40af);
    border-radius: 16px 16px 4px 16px;
    padding: 10px 15px;
    max-width: 75%;
    margin: 4px 0 4px auto;
    font-size: 0.875rem;
    line-height: 1.5;
}
.chat-bubble-ai {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 10px 15px;
    max-width: 82%;
    margin: 4px auto 4px 0;
    font-size: 0.875rem;
    line-height: 1.5;
}
.typing-indicator {
    display: inline-flex;
    gap: 4px;
    padding: 8px 12px;
    background: var(--bg-card);
    border-radius: 12px;
    border: 1px solid var(--border);
}
.typing-dot {
    width: 7px; height: 7px;
    background: var(--accent);
    border-radius: 50%;
    animation: bounce 1.4s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%,80%,100% { transform: scale(0.6); opacity:0.4; }
    40%          { transform: scale(1);   opacity:1;   }
}

/* ── KPI benchmark comparison bars ─────────────────────────────────── */
.benchmark-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.82rem;
}
.benchmark-label { flex: 0 0 160px; color: var(--text-secondary); }
.benchmark-bar-bg {
    flex: 1;
    height: 6px;
    background: var(--bg-secondary);
    border-radius: 3px;
    position: relative;
    overflow: visible;
}
.benchmark-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 0.6s ease;
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def rating_badge(rating: str) -> str:
    color_map = {
        "Excellent":  "badge-green",
        "Good":       "badge-blue",
        "Fair":       "badge-yellow",
        "Weak":       "badge-red",
        "Critical":   "badge-red",
    }
    cls = color_map.get(rating, "badge-grey")
    return f'<span class="fin-badge {cls}">{rating}</span>'


def risk_pill(level: str) -> str:
    cls_map = {
        "Low":      "risk-pill-low",
        "Medium":   "risk-pill-medium",
        "High":     "risk-pill-high",
        "Critical": "risk-pill-critical",
    }
    cls = cls_map.get(level, "risk-pill-medium")
    return f'<span class="{cls}">{level}</span>'


def page_header(title: str, subtitle: str = "", icon: str = ""):
    import streamlit as st
    st.markdown(f"""
    <div class="page-header">
        <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.8rem;">{icon}</span>
            <div>
                <h2 style="margin:0;font-size:1.4rem;font-weight:700;color:var(--text-primary);">{title}</h2>
                {f'<p style="margin:2px 0 0 0;font-size:0.82rem;color:var(--text-muted);">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
