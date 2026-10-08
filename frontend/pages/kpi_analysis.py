import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend import api_client as api
from frontend.theme import page_header


KPI_BENCHMARKS = {
    "gross_margin":       {"good": 40, "warn": 20,  "unit": "%", "invert": False},
    "operating_margin":   {"good": 15, "warn": 5,   "unit": "%", "invert": False},
    "net_margin":         {"good": 10, "warn": 2,   "unit": "%", "invert": False},
    "return_on_equity":   {"good": 15, "warn": 8,   "unit": "%", "invert": False},
    "return_on_assets":   {"good": 8,  "warn": 3,   "unit": "%", "invert": False},
    "current_ratio":      {"good": 2,  "warn": 1,   "unit": "x", "invert": False},
    "quick_ratio":        {"good": 1,  "warn": 0.7, "unit": "x", "invert": False},
    "debt_to_equity":     {"good": 1,  "warn": 2,   "unit": "x", "invert": True},
    "interest_coverage":  {"good": 5,  "warn": 2,   "unit": "x", "invert": False},
}


def show():
    page_header("KPI Analysis", "40+ financial ratios across all categories", "📈")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    with col2:
        chart_style = st.selectbox("View", ["Cards", "Bar Chart", "Radar", "Table"],
                                   label_visibility="collapsed")
    cid = company_map[selected]

    kpi_resp = api.get_kpis(cid)
    if not kpi_resp:
        st.warning("No KPI data available. Upload a financial statement first.")
        return

    kpis = kpi_resp.get("kpis", {})
    period = kpi_resp.get("period", "Latest")
    composite = kpis.get("composite_scores", {})

    # ── Summary scores ──
    st.markdown(f"<p class='section-title'>Period: {period}</p>", unsafe_allow_html=True)
    _render_score_strip(composite)

    st.markdown("---")

    # ── Category tabs ──
    tabs = st.tabs(["💰 Profitability", "💧 Liquidity", "🏦 Leverage",
                    "⚙️ Efficiency", "💸 Cash Flow", "📈 Growth", "🎯 Quality"])

    cat_configs = [
        ("profitability", tabs[0]),
        ("liquidity",     tabs[1]),
        ("leverage",      tabs[2]),
        ("efficiency",    tabs[3]),
        ("cash_flow",     tabs[4]),
        ("growth",        tabs[5]),
        ("quality",       tabs[6]),
    ]

    for cat_key, tab in cat_configs:
        with tab:
            cat_data = kpis.get(cat_key, {})
            if not cat_data:
                st.info(f"No {cat_key.replace('_',' ')} data available.")
                continue
            if chart_style == "Cards":
                _render_kpi_cards(cat_data, cat_key)
            elif chart_style == "Bar Chart":
                _render_bar(cat_data, cat_key.replace("_", " ").title())
            elif chart_style == "Radar":
                _render_radar(cat_data, cat_key)
            elif chart_style == "Table":
                _render_table(cat_data)

    # ── Multi-period trend ──
    stmts = api.get_statements(cid)
    if len(stmts) >= 2:
        st.markdown("---")
        _render_trend(stmts, period)


def _render_score_strip(composite):
    if not composite:
        return
    scores = [
        ("Profitability", "profitability_score", "💰"),
        ("Liquidity",     "liquidity_score",     "💧"),
        ("Leverage",      "leverage_score",      "🏦"),
        ("Overall Health","overall_health",      "❤️"),
    ]
    cols = st.columns(4)
    for col, (label, key, icon) in zip(cols, scores):
        val = composite.get(key)
        if val is None:
            continue
        color = "#10b981" if val >= 7 else "#f59e0b" if val >= 4 else "#ef4444"
        with col:
            st.markdown(f"""
            <div class="fin-card" style="text-align:center;border-top:3px solid {color};">
                <div style="font-size:1.5rem;">{icon}</div>
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;
                             letter-spacing:0.08em;margin:4px 0;">{label}</div>
                <div style="font-size:1.8rem;font-weight:700;color:{color};">{val:.1f}</div>
                <div style="font-size:0.7rem;color:var(--text-muted);">/ 10</div>
            </div>
            """, unsafe_allow_html=True)


def _render_kpi_cards(data: dict, cat_key: str):
    items = [(k, v) for k, v in data.items() if v is not None]
    if not items:
        st.info("No data for this category.")
        return

    cols = st.columns(4)
    for i, (key, val) in enumerate(items):
        label = key.replace("_", " ").title()
        cfg = KPI_BENCHMARKS.get(key, {})
        unit = cfg.get("unit", "")
        invert = cfg.get("invert", False)
        good = cfg.get("good")
        warn = cfg.get("warn")

        if good and warn:
            if not invert:
                color = "#10b981" if val >= good else "#f59e0b" if val >= warn else "#ef4444"
            else:
                color = "#10b981" if val <= warn else "#f59e0b" if val <= good else "#ef4444"
        else:
            color = "var(--text-primary)"

        with cols[i % 4]:
            st.markdown(f"""
            <div class="fin-card" style="border-left:3px solid {color};">
                <div style="font-size:0.68rem;color:var(--text-muted);text-transform:uppercase;
                             letter-spacing:0.07em;margin-bottom:6px;">{label}</div>
                <div style="font-size:1.5rem;font-weight:700;color:{color};">{val:.2f}<span style="font-size:0.8rem;font-weight:400;color:var(--text-muted);">{unit}</span></div>
            </div>
            """, unsafe_allow_html=True)


def _render_bar(data: dict, title: str):
    items = {k.replace("_", " ").title(): v for k, v in data.items() if v is not None}
    if not items:
        return
    colors = ["#10b981" if v >= 0 else "#ef4444" for v in items.values()]
    fig = go.Figure(go.Bar(
        x=list(items.keys()), y=list(items.values()),
        marker_color=colors,
        text=[f"{v:.2f}" for v in items.values()],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        title=title, template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
        height=360, margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(tickangle=-25, gridcolor="rgba(31,45,69,0.5)"),
        yaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_radar(data: dict, cat_key: str):
    items = {k.replace("_", " ").title(): v for k, v in data.items() if v is not None}
    if len(items) < 3:
        _render_bar(data, cat_key.replace("_", " ").title())
        return

    vals = list(items.values())
    max_v = max(abs(v) for v in vals) or 1
    norm = [min(abs(v) / max_v * 10, 10) for v in vals]
    keys = list(items.keys())

    fig = go.Figure(go.Scatterpolar(
        r=norm + [norm[0]], theta=keys + [keys[0]],
        fill="toself",
        line=dict(color="#3b82f6", width=2),
        fillcolor="rgba(59,130,246,0.15)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(31,45,69,0.8)"),
            angularaxis=dict(gridcolor="rgba(31,45,69,0.8)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_table(data: dict):
    rows = []
    for k, v in data.items():
        if v is None:
            continue
        label = k.replace("_", " ").title()
        cfg = KPI_BENCHMARKS.get(k, {})
        unit = cfg.get("unit", "")
        good = cfg.get("good")
        warn = cfg.get("warn")
        invert = cfg.get("invert", False)

        if good and warn:
            if not invert:
                status = "🟢 Strong" if v >= good else "🟡 Adequate" if v >= warn else "🔴 Weak"
            else:
                status = "🟢 Strong" if v <= warn else "🟡 Adequate" if v <= good else "🔴 Weak"
        else:
            status = "—"

        rows.append({"KPI": label, "Value": f"{v:.2f}{unit}", "Status": status})

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={
                         "KPI": st.column_config.TextColumn(width="large"),
                         "Value": st.column_config.TextColumn(width="medium"),
                         "Status": st.column_config.TextColumn(width="medium"),
                     })


def _render_trend(stmts, current_period):
    st.markdown("<p class='section-title'>Multi-Period Trend</p>", unsafe_allow_html=True)
    metric = st.selectbox(
        "Metric", ["revenue", "net_income", "gross_profit", "operating_income",
                   "ebitda", "total_assets", "total_equity", "free_cash_flow"],
        format_func=lambda x: x.replace("_", " ").title(),
        key="kpi_trend_metric",
    )

    periods = [s["period"] for s in reversed(stmts)]
    values = [s.get(metric) for s in reversed(stmts)]
    valid = [(p, v) for p, v in zip(periods, values) if v is not None]
    if not valid:
        st.info("No trend data for this metric.")
        return

    ps, vs = zip(*valid)
    # Growth annotation
    if len(vs) >= 2:
        growth = ((vs[-1] - vs[0]) / abs(vs[0])) * 100 if vs[0] else 0
        col1, col2 = st.columns([4, 1])
        with col2:
            arrow = "↑" if growth >= 0 else "↓"
            color = "#10b981" if growth >= 0 else "#ef4444"
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:var(--bg-card);
                        border-radius:var(--radius);border:1px solid var(--border);">
                <div style="font-size:0.7rem;color:var(--text-muted);">Total Change</div>
                <div style="font-size:1.4rem;font-weight:700;color:{color};">{arrow} {abs(growth):.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        col1 = st

    with col1 if len(vs) >= 2 else st:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(ps), y=list(vs),
            mode="lines+markers+text",
            line=dict(color="#3b82f6", width=2.5),
            marker=dict(size=8, color="#3b82f6", line=dict(color="white", width=2)),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.06)",
            text=[f"{v/1e9:.1f}B" if abs(v) >= 1e9 else f"{v/1e6:.0f}M" if abs(v) >= 1e6 else str(round(v, 1)) for v in vs],
            textposition="top center",
            textfont=dict(size=9),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.6)",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
            yaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
        )
        st.plotly_chart(fig, use_container_width=True)
