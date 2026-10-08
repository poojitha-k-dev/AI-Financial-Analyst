"""
FinanceAI — Professional Streamlit Frontend
"""
import streamlit as st

st.set_page_config(
    page_title="FinanceAI — Intelligent Financial Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.theme import inject_css
inject_css()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if "access_token" not in st.session_state:
    from frontend.pages import auth_page
    auth_page.show()
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
user = st.session_state.get("user", {})

with st.sidebar:
    # Logo & branding
    st.markdown("""
    <div style="padding:1.25rem 0.5rem 1rem;border-bottom:1px solid var(--border);margin-bottom:0.5rem;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="background:linear-gradient(135deg,#3b82f6,#6366f1);border-radius:10px;
                        width:36px;height:36px;display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;">📊</div>
            <div>
                <div style="font-size:1.05rem;font-weight:700;color:var(--text-primary);line-height:1;">FinanceAI</div>
                <div style="font-size:0.68rem;color:var(--text-muted);letter-spacing:0.08em;text-transform:uppercase;">
                    Intelligent Analysis
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    NAV_ITEMS = [
        ("🏠", "Dashboard",         "Overview of all companies"),
        ("🏢", "Companies",         "Manage your portfolio"),
        ("📤", "Upload",            "Import financial statements"),
        ("📈", "KPI Analysis",      "40+ financial ratios"),
        ("⚠️", "Risk Analysis",     "Altman · Piotroski · Beneish"),
        ("🔮", "Forecasting",       "Trend & scenario analysis"),
        ("🤖", "AI Insights",       "Full AI-powered analysis"),
        ("📊", "Benchmarking",      "Industry comparison"),
        ("💬", "Chat Analyst",      "Ask anything about your data"),
        ("📄", "Reports",           "Export PDF & Excel"),
    ]

    st.markdown('<p class="section-title" style="padding:0 0.5rem;">Navigation</p>', unsafe_allow_html=True)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    for icon, name, desc in NAV_ITEMS:
        is_active = st.session_state.current_page == name
        bg = "rgba(59,130,246,0.12)" if is_active else "transparent"
        color = "#3b82f6" if is_active else "var(--text-secondary)"
        border = "1px solid rgba(59,130,246,0.3)" if is_active else "1px solid transparent"

        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}",
            use_container_width=True,
            help=desc,
        ):
            st.session_state.current_page = name
            st.rerun()

    st.markdown("<div style='margin-top:auto;padding-top:1rem;border-top:1px solid var(--border);'>", unsafe_allow_html=True)

    # User info
    plan_colors = {"free": "#64748b", "pro": "#3b82f6", "enterprise": "#8b5cf6"}
    plan = user.get("plan", "free")
    st.markdown(f"""
    <div style="padding:0.75rem 0.5rem;">
        <div style="font-size:0.8rem;font-weight:600;color:var(--text-primary);">
            {user.get('full_name', 'User')}
        </div>
        <div style="font-size:0.7rem;color:var(--text-muted);">{user.get('email', '')}</div>
        <span style="background:{plan_colors.get(plan,'#64748b')}22;color:{plan_colors.get(plan,'#94a3b8')};
                     font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                     padding:2px 8px;border-radius:999px;display:inline-block;margin-top:4px;">
            {plan.upper()} PLAN
        </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ Profile", use_container_width=True, key="nav_profile"):
            st.session_state.current_page = "Profile"
            st.rerun()
    with col2:
        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:0.5rem 0;font-size:0.65rem;color:var(--text-muted);">
        Powered by GPT-4o · Gemini 1.5 Pro
    </div>
    """, unsafe_allow_html=True)


# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "Dashboard":
    from frontend.pages import dashboard; dashboard.show()
elif page == "Companies":
    from frontend.pages import companies; companies.show()
elif page == "Upload":
    from frontend.pages import upload; upload.show()
elif page == "KPI Analysis":
    from frontend.pages import kpi_analysis; kpi_analysis.show()
elif page == "Risk Analysis":
    from frontend.pages import risk_analysis; risk_analysis.show()
elif page == "Forecasting":
    from frontend.pages import forecasting; forecasting.show()
elif page == "AI Insights":
    from frontend.pages import ai_insights; ai_insights.show()
elif page == "Benchmarking":
    from frontend.pages import benchmarking; benchmarking.show()
elif page == "Chat Analyst":
    from frontend.pages import chat; chat.show()
elif page == "Reports":
    from frontend.pages import reports; reports.show()
elif page == "Profile":
    from frontend.pages import profile; profile.show()
