import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend import api_client as api
from frontend.theme import page_header
from backend.services.benchmarks import compare_to_benchmarks


def show():
    page_header("Industry Benchmarking", "Compare your company's KPIs against sector medians", "📊")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c for c in companies}
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    co = company_map[selected]
    cid = co["id"]
    sector = co.get("sector")

    kpi_resp = api.get_kpis(cid)
    if not kpi_resp:
        st.warning("No KPI data. Upload a statement first.")
        return

    kpis = kpi_resp.get("kpis", {})

    # Run comparison
    comparison = compare_to_benchmarks(kpis, sector)
    comparisons = comparison.get("comparisons", {})
    out_count = comparison.get("outperforming_count", 0)
    under_count = comparison.get("underperforming_count", 0)
    total = len(comparisons)

    # ── Summary ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sector", sector or "General")
    c2.metric("Metrics Compared", total)
    c3.metric("Outperforming", out_count, delta=f"+{out_count}" if out_count else None)
    c4.metric("Underperforming", under_count,
              delta=f"-{under_count}" if under_count else None,
              delta_color="inverse" if under_count else "normal")

    st.markdown("---")

    if not comparisons:
        st.info("Upload more detailed financial data to enable benchmarking.")
        return

    tab1, tab2, tab3 = st.tabs(["📊 Bar Comparison", "🔢 Detailed Table", "🕸️ Radar Chart"])

    with tab1:
        _render_bar_comparison(comparisons)

    with tab2:
        _render_detail_table(comparisons)

    with tab3:
        _render_radar_comparison(comparisons, kpis, sector)


def _render_bar_comparison(comparisons: dict):
    metrics = list(comparisons.items())[:12]
    labels = [m.replace("_", " ").title() for m, _ in metrics]
    company_vals = [v["company_value"] for _, v in metrics]
    industry_vals = [v["industry_median"] for _, v in metrics]
    ratings = [v["rating"] for _, v in metrics]

    colors = [
        "#10b981" if r == "Outperforming" else
        "#3b82f6" if r == "Above Average" else
        "#f59e0b" if r == "Below Average" else "#ef4444"
        for r in ratings
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Company", x=labels, y=company_vals,
        marker_color=colors, opacity=0.9,
        text=[f"{v:.1f}" for v in company_vals],
        textposition="outside", textfont=dict(size=9),
    ))
    fig.add_trace(go.Scatter(
        name="Industry Median", x=labels, y=industry_vals,
        mode="markers",
        marker=dict(color="white", size=8, symbol="line-ew-open",
                    line=dict(color="white", width=2)),
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        height=420,
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=0, r=0, t=10, b=50),
        xaxis=dict(tickangle=-30, gridcolor="rgba(31,45,69,0.5)"),
        yaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="display:flex;gap:16px;font-size:0.78rem;color:var(--text-secondary);margin-top:4px;">
        <span>🟢 Outperforming</span>
        <span>🔵 Above Average</span>
        <span>🟡 Below Average</span>
        <span>🔴 Underperforming</span>
        <span style="margin-left:8px;">— White markers = industry median</span>
    </div>
    """, unsafe_allow_html=True)


def _render_detail_table(comparisons: dict):
    rows = []
    for metric, data in comparisons.items():
        rating = data["rating"]
        color_map = {
            "Outperforming":  "🟢",
            "Above Average":  "🔵",
            "Below Average":  "🟡",
            "Underperforming":"🔴",
        }
        rows.append({
            "Metric": metric.replace("_", " ").title(),
            "Company": f"{data['company_value']:.2f}",
            "Industry Median": f"{data['industry_median']:.2f}",
            "Delta": f"{data['delta']:+.2f}",
            "vs Industry": f"{data['pct_vs_industry']:+.1f}%",
            "Rating": f"{color_map.get(rating, '—')} {rating}",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "Metric": st.column_config.TextColumn(width="large"),
                     "Company": st.column_config.TextColumn(width="small"),
                     "Industry Median": st.column_config.TextColumn(width="small"),
                     "Delta": st.column_config.TextColumn(width="small"),
                     "vs Industry": st.column_config.TextColumn(width="small"),
                     "Rating": st.column_config.TextColumn(width="medium"),
                 })


def _render_radar_comparison(comparisons: dict, kpis: dict, sector: str):
    top_metrics = ["gross_margin", "net_margin", "return_on_equity",
                   "current_ratio", "debt_to_equity", "fcf_margin", "asset_turnover"]
    available = [m for m in top_metrics if m in comparisons]
    if len(available) < 3:
        st.info("Not enough overlapping metrics for radar chart.")
        return

    labels = [m.replace("_", " ").title() for m in available]
    max_val = 1

    def norm(vals):
        mx = max(abs(v) for v in vals if v) or 1
        return [min(abs(v) / mx * 10, 10) for v in vals]

    company_vals = [comparisons[m]["company_value"] for m in available]
    industry_vals = [comparisons[m]["industry_median"] for m in available]
    cn = norm(company_vals)
    ind = norm(industry_vals)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=cn + [cn[0]], theta=labels + [labels[0]],
        fill="toself", name="Company",
        line=dict(color="#3b82f6", width=2),
        fillcolor="rgba(59,130,246,0.18)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=ind + [ind[0]], theta=labels + [labels[0]],
        fill="toself", name=f"{sector or 'Industry'} Median",
        line=dict(color="#f59e0b", width=2, dash="dot"),
        fillcolor="rgba(245,158,11,0.1)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(31,45,69,0.8)"),
            angularaxis=dict(gridcolor="rgba(31,45,69,0.8)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.1),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
