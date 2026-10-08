import streamlit as st
from frontend import api_client as api
from frontend.theme import inject_css


def show():
    inject_css()

    # Center the auth form
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        # Logo
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1.5rem;">
            <div style="background:linear-gradient(135deg,#3b82f6,#6366f1);border-radius:18px;
                        width:64px;height:64px;display:inline-flex;align-items:center;
                        justify-content:center;font-size:2rem;margin-bottom:1rem;
                        box-shadow:0 8px 32px rgba(59,130,246,0.35);">📊</div>
            <h1 style="margin:0;font-size:1.8rem;font-weight:700;
                       background:linear-gradient(135deg,#3b82f6,#6366f1);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                FinanceAI
            </h1>
            <p style="color:var(--text-muted);margin:6px 0 0;font-size:0.85rem;">
                Intelligent Financial Analysis Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["  Sign In  ", "  Create Account  "])

        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="analyst@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter email and password")
                else:
                    with st.spinner("Authenticating..."):
                        result = api.login(email, password)
                    if result:
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.success(f"Welcome back, {result['user']['full_name']}!")
                        st.rerun()

        with tab_register:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="Jane Smith")
                reg_email = st.text_input("Work Email", placeholder="jane@company.com")
                company_name = st.text_input("Company / Organization", placeholder="Acme Corp (optional)")
                reg_pass = st.text_input("Password", type="password", placeholder="Min. 8 characters")
                reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                reg_submitted = st.form_submit_button("Create Free Account →", use_container_width=True)

            if reg_submitted:
                if not full_name or not reg_email or not reg_pass:
                    st.error("All fields except company are required")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match")
                elif len(reg_pass) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    with st.spinner("Creating your account..."):
                        result = api.register(reg_email, full_name, reg_pass, company_name or None)
                    if result:
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.success(f"Welcome to FinanceAI, {result['user']['full_name']}!")
                        st.rerun()

        # Features teaser
        st.markdown("""
        <div style="margin-top:1.5rem;padding:1rem;background:var(--bg-card);
                    border-radius:var(--radius);border:1px solid var(--border);">
            <p style="font-size:0.72rem;color:var(--text-muted);text-align:center;
                      text-transform:uppercase;letter-spacing:0.1em;margin:0 0 0.75rem;">
                What's included
            </p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;font-size:0.78rem;color:var(--text-secondary);">
                <div>✅ 40+ Financial KPIs</div>
                <div>✅ Altman Z-Score</div>
                <div>✅ AI Insights (GPT-4o)</div>
                <div>✅ Beneish M-Score</div>
                <div>✅ Trend Forecasting</div>
                <div>✅ Industry Benchmarks</div>
                <div>✅ PDF & Excel Export</div>
                <div>✅ Chat Analyst</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
