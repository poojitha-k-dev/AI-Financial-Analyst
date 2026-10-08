import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from frontend import api_client as api
from frontend.theme import page_header, rating_badge, risk_pill


def show():
    user = st.session_state.get("user", {})
    page_header(
        title=f"Good morning, {user.get('full_name', 'Analyst').split()[0]} 👋",
        subtitle="Here's your financial intelligence overview",
        icon="🏠",
    )

    companies = api.get_companies()

    # ── Platform Stats ──
    total_stmts = sum(c.get("statement_count", 0) for c in companies)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies Tracked", len(companies), help="Total companies in your portfolio")
    c2.metric("Financial Periods", total_stmts, help="Total uploaded statements")
    c3.metric("KPIs Available", "40+", help="Financial ratios calculated automatically")
    c4.metric("Risk Models", "3", help="Altman Z · Beneish M · Piotroski F")

    if not companies:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        _show_empty_state()
        return

    st.markdown("---")

    # ── Company Selector ──
    col1, col2 = st.columns([3, 1])
    with col1:
        company_map = {f"{c['name']} {'(' + c['ticker'] + ')' if c.get('ticker') else ''}".strip(): c["id"]
                       for c in companies}
        selected_label = st.selectbox("Select Company", list(company_map.keys()), label_visibility="collapsed")
        cid = company_map[selected_label]

    with col2:
        if st.button("🚀 Run Full Analysis", use_container_width=True, type="primary"):
            st.session_state.current_page = "AI Insights"
            st.session_state.prefill_company_id = cid
            st.rerun()

    stmts = api.get_statements(cid)
    kpi_resp = api.get_kpis(cid)
    reports = api.list_reports(cid)

    if not stmts:
        st.info("No financial data uploaded for this company yet. Head to **Upload** to get started.")
        return

    kpis = kpi_resp.get("kpis", {}) if kpi_resp else {}
    period = kpi_resp.get("period", "Latest") if kpi_resp else "N/A"
    composite = kpis.get("composite_scores", {})
    latest_report = reports[0] if reports else {}

    # ── Key Metrics Row ──
    st.markdown(f"<p class='section-title'>Latest Period: {period}</p>", unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    pr = kpis.get("profitability", {})
    liq = kpis.get("liquidity", {})
    lev = kpis.get("leverage", {})
    gr = kpis.get("growth", {})

    _metric(m1, "Gross Margin", pr.get("gross_margin"), "%")
    _metric(m2, "Net Margin", pr.get("net_margin"), "%")
    _metric(m3, "ROE", pr.get("return_on_equity"), "%")
    _metric(m4, "Current Ratio", liq.get("current_ratio"), "x")
    _metric(m5, "D/E Ratio", lev.get("debt_to_equity"), "x", invert=True)
    _metric(m6, "Revenue Growth", gr.get("revenue_growth"), "%")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Charts Row ──
    left, right = st.columns([2, 1])

    with left:
        if len(stmts) >= 2:
            _render_trend_chart(stmts)
        else:
            _render_single_period_bar(kpis)

    with right:
        _render_health_gauge(composite)

    # ── Latest Report Card ──
    if latest_report:
        st.markdown("---")
        st.markdown("<p class='section-title'>Latest Analysis Report</p>", unsafe_allow_html=True)
        rating = latest_report.get("overall_rating", "")
        _col1, _col2, _col3 = st.columns([3, 2, 1])
        with _col1:
            st.markdown(f"""
            <div class="fin-card fin-card-accent">
                <div style="font-size:0.8rem;color:var(--text-muted);">{latest_report.get('created_at','')[:16]}</div>
                <div style="font-weight:600;margin:4px 0;">{latest_report.get('title','Analysis')}</div>
                <div style="font-size:0.82rem;color:var(--text-secondary);">
                    {latest_report.get('executive_summary','Run AI Analysis to generate executive summary.')[:200]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
        with _col2:
            if rating:
                st.markdown(f"**Rating:** {rating_badge(rating)}", unsafe_allow_html=True)
            st.caption(f"Model: {latest_report.get('llm_provider','—')}")
        with _col3:
            if st.button("View →", use_container_width=True):
                st.session_state.current_page = "AI Insights"
                st.rerun()

    # ── Watchlist overview if multiple companies ──
    if len(companies) > 1:
        _render_portfolio_overview(companies)


def _render_trend_chart(stmts):
    st.markdown("<p class='section-title'>Revenue & Net Income Trend</p>", unsafe_allow_html=True)
    periods = [s["period"] for s in reversed(stmts)]
    revenues = [s.get("revenue") for s in reversed(stmts)]
    net_incomes = [s.get("net_income") for s in reversed(stmts)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Revenue", x=periods, y=revenues,
        marker=dict(color="rgba(59,130,246,0.7)", line=dict(color="#3b82f6", width=1)),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        name="Net Income", x=periods, y=net_incomes,
        line=dict(color="#10b981", width=2.5), mode="lines+markers",
        marker=dict(size=7, color="#10b981"),
        yaxis="y2",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        legend=dict(orientation="h", y=-0.2, font=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="rgba(31,45,69,0.8)", tickfont=dict(size=10)),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=0, t=10, b=30),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_single_period_bar(kpis):
    pr = kpis.get("profitability", {})
    items = {
        "Gross Margin": pr.get("gross_margin"),
        "Operating Margin": pr.get("operating_margin"),
        "Net Margin": pr.get("net_margin"),
        "ROE": pr.get("return_on_equity"),
        "ROA": pr.get("return_on_assets"),
    }
    items = {k: v for k, v in items.items() if v is not None}
    if not items:
        st.info("Upload financial data to see charts.")
        return
    fig = go.Figure(go.Bar(
        x=list(items.keys()), y=list(items.values()),
        marker_color=["#10b981" if v >= 0 else "#ef4444" for v in items.values()],
        text=[f"{v:.1f}%" for v in items.values()],
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_health_gauge(composite):
    st.markdown("<p class='section-title'>Financial Health Score</p>", unsafe_allow_html=True)
    overall = composite.get("overall_health")
    if overall is None:
        st.info("Run AI analysis to compute health score")
        return

    color = "#10b981" if overall >= 7 else "#f59e0b" if overall >= 4 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall,
        number={"suffix": "/10", "font": {"size": 36, "color": color}},
        gauge={
            "axis": {"range": [0, 10], "tickwidth": 1, "tickcolor": "#64748b", "tickfont": {"size": 9}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 4], "color": "rgba(239,68,68,0.12)"},
                {"range": [4, 7], "color": "rgba(245,158,11,0.12)"},
                {"range": [7, 10], "color": "rgba(16,185,129,0.12)"},
            ],
        },
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=240, margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_portfolio_overview(companies):
    st.markdown("---")
    st.markdown("<p class='section-title'>Portfolio Overview</p>", unsafe_allow_html=True)
    cols = st.columns(min(len(companies), 4))
    for i, co in enumerate(companies[:4]):
        with cols[i % 4]:
            name = co["name"][:18] + "…" if len(co["name"]) > 18 else co["name"]
            ticker = co.get("ticker") or "—"
            sector = co.get("sector") or "—"
            stmts = co.get("statement_count", 0)
            st.markdown(f"""
            <div class="fin-card" style="cursor:pointer;">
                <div style="font-weight:600;font-size:0.9rem;">{name}</div>
                <div style="color:var(--text-muted);font-size:0.75rem;">{ticker} · {sector}</div>
                <div style="color:var(--text-secondary);font-size:0.75rem;margin-top:6px;">
                    {stmts} period{'s' if stmts != 1 else ''}
                    {' · ' + co.get('latest_period','') if co.get('latest_period') else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)


def _metric(col, label, value, suffix="", invert=False):
    with col:
        if value is not None:
            # Delta coloring
            if not invert:
                delta_color = "normal"
            else:
                delta_color = "inverse"
            col.metric(label, f"{value:.2f}{suffix}")
        else:
            col.metric(label, "N/A")


def _show_empty_state():
    st.markdown("""
    <div style="text-align:center;padding:3rem 2rem;background:var(--bg-card);
                border-radius:var(--radius);border:1px solid var(--border);">
        <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
        <h3 style="margin:0 0 8px;color:var(--text-primary);">Start Your Financial Analysis</h3>
        <p style="color:var(--text-muted);max-width:400px;margin:0 auto 1.5rem;">
            Add a company and upload their financial statements to unlock 
            AI-powered insights, risk models, and forecasting.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.5, 1])
    with col2:
        if st.button("➕ Add First Company", use_container_width=True, type="primary"):
            st.session_state.current_page = "Companies"
            st.rerun()
