import streamlit as st
from frontend import api_client as api
from frontend.theme import page_header


def show():
    page_header("Profile & Settings", "Manage your account and preferences", "⚙️")

    user = st.session_state.get("user", {})

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔒 Security", "📊 Usage"])

    with tab1:
        _show_profile(user)

    with tab2:
        _show_security()

    with tab3:
        _show_usage(user)


def _show_profile(user: dict):
    st.markdown("<p class='section-title'>Account Details</p>", unsafe_allow_html=True)

    # Avatar placeholder
    initials = "".join([n[0] for n in user.get("full_name", "U").split()[:2]]).upper()
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;padding:1rem 0;
                border-bottom:1px solid var(--border);margin-bottom:1rem;">
        <div style="width:64px;height:64px;border-radius:50%;
                    background:linear-gradient(135deg,#3b82f6,#6366f1);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.5rem;font-weight:700;color:white;flex-shrink:0;">
            {initials}
        </div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;">{user.get('full_name','—')}</div>
            <div style="color:var(--text-muted);font-size:0.85rem;">{user.get('email','—')}</div>
            <span style="background:rgba(59,130,246,0.15);color:#3b82f6;
                         font-size:0.7rem;font-weight:600;padding:2px 10px;
                         border-radius:999px;text-transform:uppercase;letter-spacing:0.08em;">
                {user.get('plan','free').upper()} PLAN
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=user.get("full_name", ""))
            company_name = st.text_input("Company / Organization",
                                         value=user.get("company_name") or "")
        with col2:
            st.text_input("Email", value=user.get("email", ""), disabled=True,
                          help="Contact support to change your email")
            bio = st.text_area("Bio", value=user.get("bio") or "",
                               height=80, placeholder="Brief professional bio...")

        submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

    if submitted:
        result = api.update_profile(
            full_name=full_name or None,
            company_name=company_name or None,
            bio=bio or None,
        )
        if result:
            st.session_state.user = result.get("user", user)
            st.success("✅ Profile updated successfully.")
            st.rerun()


def _show_security():
    st.markdown("<p class='section-title'>Change Password</p>", unsafe_allow_html=True)

    with st.form("password_form"):
        current = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password",
                                 help="Minimum 8 characters")
        confirm  = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("🔒 Change Password", use_container_width=True)

    if submitted:
        if not current or not new_pass:
            st.error("All fields are required.")
        elif new_pass != confirm:
            st.error("New passwords do not match.")
        elif len(new_pass) < 8:
            st.error("New password must be at least 8 characters.")
        else:
            result = api.change_password(current, new_pass)
            if result:
                st.success("✅ Password changed successfully.")

    st.markdown("---")
    st.markdown("<p class='section-title'>Session</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class="fin-card">
        <div style="font-size:0.85rem;color:var(--text-secondary);">
            Your session is secured with JWT authentication. 
            Tokens expire after 24 hours and are stored only in your browser session.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=False):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def _show_usage(user: dict):
    st.markdown("<p class='section-title'>Platform Overview</p>", unsafe_allow_html=True)

    companies = api.get_companies()
    total_stmts = sum(c.get("statement_count", 0) for c in companies)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", len(companies))
    c2.metric("Periods Uploaded", total_stmts)
    c3.metric("Current Plan", user.get("plan", "free").title())
    c4.metric("Account Since", str(user.get("created_at", ""))[:10] or "—")

    st.markdown("---")
    st.markdown("<p class='section-title'>Plan Features</p>", unsafe_allow_html=True)

    plan = user.get("plan", "free")
    features = {
        "free": {
            "Companies": "Up to 3",
            "Periods": "Up to 5 per company",
            "AI Analyses": "10/month",
            "Chat Messages": "50/month",
            "Exports": "PDF only",
        },
        "pro": {
            "Companies": "Unlimited",
            "Periods": "Unlimited",
            "AI Analyses": "100/month",
            "Chat Messages": "500/month",
            "Exports": "PDF + Excel",
        },
        "enterprise": {
            "Companies": "Unlimited",
            "Periods": "Unlimited",
            "AI Analyses": "Unlimited",
            "Chat Messages": "Unlimited",
            "Exports": "PDF + Excel + API",
        },
    }

    plan_features = features.get(plan, features["free"])
    cols = st.columns(len(plan_features))
    for col, (k, v) in zip(cols, plan_features.items()):
        with col:
            st.markdown(f"""
            <div class="fin-card" style="text-align:center;">
                <div class="section-title">{k}</div>
                <div style="font-weight:600;color:var(--text-primary);">{v}</div>
            </div>
            """, unsafe_allow_html=True)
