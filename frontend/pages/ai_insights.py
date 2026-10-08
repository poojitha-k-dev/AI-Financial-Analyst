import streamlit as st
from frontend import api_client as api
from frontend.theme import page_header, rating_badge, risk_pill


def show():
    page_header("AI Financial Insights", "Full AI-powered analysis with GPT-4o or Gemini 1.5 Pro", "🤖")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        default_idx = 0
        if "prefill_company_id" in st.session_state:
            ids = [c["id"] for c in companies]
            try:
                default_idx = ids.index(st.session_state.pop("prefill_company_id"))
            except ValueError:
                default_idx = 0
        selected = st.selectbox("Company", list(company_map.keys()),
                                index=default_idx, label_visibility="collapsed")
    cid = company_map[selected]

    stmts = api.get_statements(cid)
    with col2:
        if stmts:
            stmt_map = {s["period"]: s["id"] for s in stmts}
            period = st.selectbox("Period", list(stmt_map.keys()), label_visibility="collapsed")
            stmt_id = stmt_map[period]
        else:
            st.warning("No statements available.")
            return

    with col3:
        run = st.button("🚀 Analyse", use_container_width=True, type="primary")

    # Show existing reports
    reports = api.list_reports(cid)
    if reports and not run:
        st.markdown("<p class='section-title'>Saved Analysis Reports</p>", unsafe_allow_html=True)
        for r in reports[:3]:
            rating = r.get("overall_rating", "")
            pinned = "📌 " if r.get("is_pinned") else ""
            with st.expander(
                f"{pinned}**{r['title']}** — {r.get('created_at','')[:10]} "
                f"{'| ' + rating if rating else ''}",
                expanded=(r == reports[0]),
            ):
                if r.get("executive_summary"):
                    st.markdown(r["executive_summary"])
                if rating:
                    st.markdown(f"**Rating:** {rating_badge(rating)}", unsafe_allow_html=True)
                if st.button("Load Full Report", key=f"load_{r['id']}"):
                    st.session_state["loaded_report"] = r
                    st.rerun()

    if run:
        with st.spinner("Running full AI analysis — this takes 15–30 seconds..."):
            result = api.run_full_analysis(cid, stmt_id)

        if result:
            st.session_state["last_analysis"] = result
            _render_result(result)

    elif "last_analysis" in st.session_state:
        _render_result(st.session_state["last_analysis"])


def _render_result(result: dict):
    insights = result.get("insights", "")
    kpis = result.get("kpis", {})
    risk = result.get("risk_analysis", {})
    rating = result.get("overall_rating", "")
    exec_summary = result.get("executive_summary", "")
    company = result.get("company", "")
    period = result.get("period", "")

    st.markdown("---")

    # ── Header strip ──
    col1, col2, col3, col4, col5 = st.columns(5)
    composite = kpis.get("composite_scores", {})
    risk_summary = risk.get("risk_summary", {})

    col1.metric("Company", company)
    col2.metric("Period", period)
    col3.metric("Health Score", f"{composite.get('overall_health', '—')}/10")
    col4.metric("Risk Level", risk_summary.get("overall_risk_level", "—"))
    with col5:
        if rating:
            st.markdown(f"**Rating**")
            st.markdown(rating_badge(rating), unsafe_allow_html=True)

    # ── Executive Summary card ──
    if exec_summary:
        st.markdown("""
        <p class='section-title' style='margin-top:1rem;'>Executive Summary</p>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="fin-card fin-card-accent">
            {exec_summary}
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Full Analysis", "📊 KPI Summary", "⚠️ Risk", "🔮 Forecasts"])

    with tab1:
        if insights:
            st.markdown(insights)
        else:
            st.info("No insights generated.")

    with tab2:
        _render_kpi_summary(kpis)

    with tab3:
        _render_risk_tab(risk)

    with tab4:
        forecasts = result.get("forecasts", {})
        _render_forecast_tab(forecasts)

    # ── Export buttons ──
    st.markdown("---")
    st.markdown("<p class='section-title'>Export Report</p>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        cid = None
        companies = api.get_companies()
        co_map = {c["name"]: c["id"] for c in companies}
        cid = co_map.get(company)
        if cid:
            pdf_bytes = api.export_pdf_bytes(cid)
            if pdf_bytes:
                st.download_button(
                    "📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{company}_{period}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    with c2:
        if cid:
            xl_bytes = api.export_excel_bytes(cid)
            if xl_bytes:
                st.download_button(
                    "📥 Download Excel",
                    data=xl_bytes,
                    file_name=f"{company}_{period}_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )


def _render_kpi_summary(kpis: dict):
    cats = [
        ("💰 Profitability", "profitability"),
        ("💧 Liquidity",     "liquidity"),
        ("🏦 Leverage",      "leverage"),
        ("💸 Cash Flow",     "cash_flow"),
    ]
    for label, key in cats:
        data = kpis.get(key, {})
        if not data:
            continue
        st.markdown(f"**{label}**")
        cols = st.columns(min(len(data), 5))
        for i, (k, v) in enumerate(data.items()):
            if v is not None:
                suffix = "%" if any(x in k for x in ["margin", "return", "growth", "rate"]) else "x"
                cols[i % 5].metric(k.replace("_", " ").title(), f"{v:.2f}{suffix}")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _render_risk_tab(risk: dict):
    altman = risk.get("altman_z_score", {})
    pio = risk.get("piotroski_f_score", {})
    custom = risk.get("custom_risk", {})
    summary = risk.get("risk_summary", {})

    level = summary.get("overall_risk_level", "—")
    st.markdown(f"**Overall Risk Level:** {risk_pill(level)}", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        z = altman.get("score")
        zone = altman.get("zone", "—")
        st.markdown(f"""
        <div class="fin-card">
            <div class="section-title">Altman Z-Score</div>
            <div style="font-size:2rem;font-weight:700;color:{'#10b981' if z and z > 2.99 else '#f59e0b' if z and z > 1.81 else '#ef4444'};">
                {f'{z:.2f}' if z else '—'}
            </div>
            <div style="font-size:0.78rem;color:var(--text-muted);">{zone}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        f_score = pio.get("score")
        strength = pio.get("strength", "—")
        st.markdown(f"""
        <div class="fin-card">
            <div class="section-title">Piotroski F-Score</div>
            <div style="font-size:2rem;font-weight:700;color:{'#10b981' if f_score and f_score >= 7 else '#f59e0b' if f_score and f_score >= 4 else '#ef4444'};">
                {f'{f_score}/9' if f_score is not None else '—'}
            </div>
            <div style="font-size:0.78rem;color:var(--text-muted);">{strength}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        r_score = custom.get("risk_score", 0)
        r_level = custom.get("risk_level", "—")
        color = "#10b981" if r_score <= 2 else "#f59e0b" if r_score <= 5 else "#ef4444"
        st.markdown(f"""
        <div class="fin-card">
            <div class="section-title">Custom Risk Score</div>
            <div style="font-size:2rem;font-weight:700;color:{color};">{r_score}/10</div>
            <div style="font-size:0.78rem;color:var(--text-muted);">{r_level}</div>
        </div>
        """, unsafe_allow_html=True)

    flags = custom.get("risk_factors", [])
    if flags:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("**Risk Flags:**")
        for f in flags:
            sev = f.get("severity", "medium")
            color = "#ef4444" if sev == "high" else "#f59e0b"
            icon = "🔴" if sev == "high" else "🟡"
            st.markdown(f"""
            <div style="padding:8px 12px;background:var(--bg-card);border-left:3px solid {color};
                        border-radius:4px;margin:4px 0;font-size:0.84rem;">
                {icon} <b>{f['factor']}</b> — {f['detail']}
            </div>
            """, unsafe_allow_html=True)


def _render_forecast_tab(forecasts: dict):
    import plotly.graph_objects as go
    available = [k for k, v in forecasts.items() if isinstance(v, dict) and "historical" in v]
    if not available:
        st.info("Need at least 2 periods of data for forecasting.")
        return

    metric = st.selectbox("Metric", available, format_func=lambda x: x.replace("_", " ").title(),
                           key="ai_forecast_metric")
    fdata = forecasts[metric]
    historical = fdata.get("historical", [])
    ensemble = fdata.get("ensemble_forecast", [])
    ci_lower = fdata.get("confidence_interval", {}).get("lower", [])
    ci_upper = fdata.get("confidence_interval", {}).get("upper", [])
    n = len(historical)
    hist_labels = [f"T-{n-i-1}" for i in range(n-1)] + ["T0"]
    future_labels = [f"T+{i+1}" for i in range(len(ensemble))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_labels, y=historical, mode="lines+markers", name="Historical",
        line=dict(color="#3b82f6", width=2),
    ))
    if ensemble:
        fig.add_trace(go.Scatter(
            x=future_labels, y=ensemble, mode="lines+markers", name="Forecast",
            line=dict(color="#10b981", width=2, dash="dash"),
            marker=dict(symbol="diamond", size=8),
        ))
    if ci_lower and ci_upper:
        fig.add_trace(go.Scatter(
            x=future_labels + future_labels[::-1],
            y=ci_upper + ci_lower[::-1],
            fill="toself", fillcolor="rgba(16,185,129,0.08)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI",
        ))
    fig.add_vline(x=hist_labels[-1], line_dash="dot", line_color="rgba(255,255,255,0.2)")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)", height=320,
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=0, r=0, t=10, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    trend = fdata.get("trend", {})
    cagr = fdata.get("cagr_pct")
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("Trend Direction", trend.get("direction", "—").title())
    tc2.metric("R² Fit", f"{trend.get('r_squared', 0):.3f}")
    tc3.metric("CAGR", f"{cagr:.1f}%" if cagr else "—")
