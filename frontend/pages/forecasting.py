import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend import api_client as api
from frontend.theme import page_header


def show():
    page_header("Financial Forecasting", "Multi-method forecasting: Linear · Exponential · Ensemble with confidence intervals", "🔮")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    with col2:
        periods_ahead = st.slider("Periods Ahead", 2, 8, 4, label_visibility="collapsed")
    with col3:
        run = st.button("🚀 Forecast", use_container_width=True, type="primary")

    cid = company_map[selected]

    if run:
        with st.spinner("Running forecast models..."):
            result = api.get_forecast(cid, periods_ahead)
        if result:
            st.session_state["last_forecast"] = result

    result = st.session_state.get("last_forecast")
    if not result:
        st.info("Click **Forecast** to generate predictions (requires at least 2 historical periods).")
        return

    forecasts = result.get("forecasts", {})
    narrative = result.get("narrative", "")

    available = [k for k, v in forecasts.items()
                 if isinstance(v, dict) and "historical" in v and len(v.get("historical", [])) >= 2]

    if not available:
        st.warning("Not enough historical data. Upload at least 2 periods first.")
        return

    # ── Controls ──
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        metric = st.selectbox(
            "Select Metric",
            available,
            format_func=lambda x: x.replace("_", " ").title(),
            key="forecast_metric",
        )
    with col2:
        method = st.selectbox("Display Method", ["Ensemble (Recommended)", "All Methods", "Linear Only"],
                              key="forecast_method")

    fdata = forecasts[metric]
    historical = fdata.get("historical", [])
    linear_fc  = fdata.get("linear_forecast", [])
    exp_fc     = fdata.get("exponential_forecast", [])
    ensemble   = fdata.get("ensemble_forecast", [])
    ci_lower   = fdata.get("confidence_interval", {}).get("lower", [])
    ci_upper   = fdata.get("confidence_interval", {}).get("upper", [])
    trend      = fdata.get("trend", {})
    cagr       = fdata.get("cagr_pct")

    n = len(historical)
    hist_labels   = [f"T-{n-i-1}" for i in range(n-1)] + ["T0 (Latest)"]
    future_labels = [f"T+{i+1}" for i in range(len(ensemble))]

    # ── Summary metrics ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Historical Periods", n)
    c2.metric("CAGR", f"{cagr:.1f}%" if cagr else "—")
    c3.metric("Trend", trend.get("direction", "—").title())
    c4.metric("R² Fit", f"{trend.get('r_squared', 0):.3f}")
    trend_slope = trend.get("slope", 0)
    c5.metric("Trend Slope", f"{trend_slope:+.2f}" if trend_slope else "—")

    # ── Chart ──
    fig = go.Figure()

    # Historical shaded area
    fig.add_trace(go.Scatter(
        x=hist_labels, y=historical,
        mode="lines+markers",
        name="Historical",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=7, color="#3b82f6", line=dict(color="white", width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.05)",
    ))

    # Forecast traces
    if method in ("Ensemble (Recommended)", "All Methods") and ensemble:
        fig.add_trace(go.Scatter(
            x=future_labels, y=ensemble,
            mode="lines+markers",
            name="Ensemble",
            line=dict(color="#10b981", width=2.5, dash="dash"),
            marker=dict(size=9, color="#10b981", symbol="diamond",
                        line=dict(color="white", width=1)),
        ))

    if method == "All Methods":
        if linear_fc:
            fig.add_trace(go.Scatter(
                x=future_labels, y=linear_fc,
                mode="lines", name="Linear Regression",
                line=dict(color="#f59e0b", width=1.5, dash="dot"),
                opacity=0.8,
            ))
        if exp_fc:
            fig.add_trace(go.Scatter(
                x=future_labels, y=exp_fc,
                mode="lines", name="Exponential Smoothing",
                line=dict(color="#8b5cf6", width=1.5, dash="dot"),
                opacity=0.8,
            ))

    if method == "Linear Only" and linear_fc:
        fig.add_trace(go.Scatter(
            x=future_labels, y=linear_fc,
            mode="lines+markers", name="Linear Forecast",
            line=dict(color="#10b981", width=2.5, dash="dash"),
            marker=dict(size=8),
        ))

    # Confidence interval band
    active_forecast = ensemble if method != "Linear Only" else linear_fc
    if ci_upper and ci_lower and active_forecast:
        fig.add_trace(go.Scatter(
            x=future_labels + future_labels[::-1],
            y=ci_upper + ci_lower[::-1],
            fill="toself",
            fillcolor="rgba(16,185,129,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% Confidence Interval",
        ))

    # Divider between historical and forecast
    if hist_labels:
        fig.add_vline(
            x=hist_labels[-1],
            line_dash="dot",
            line_color="rgba(255,255,255,0.25)",
            annotation_text="→ Forecast",
            annotation_position="top right",
            annotation_font_color="#64748b",
            annotation_font_size=11,
        )

    metric_label = metric.replace("_", " ").title()
    fig.update_layout(
        title=dict(text=f"{metric_label} — Historical & Forecast", font=dict(size=14)),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        height=420,
        legend=dict(orientation="h", y=-0.18, font=dict(size=11)),
        margin=dict(l=0, r=0, t=40, b=50),
        yaxis_title=metric_label,
        xaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
        yaxis=dict(gridcolor="rgba(31,45,69,0.5)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Forecast table ──
    active = ensemble if method != "Linear Only" else linear_fc
    if active:
        st.markdown("<p class='section-title'>Forecast Values</p>", unsafe_allow_html=True)
        rows = []
        for i, (lbl, val) in enumerate(zip(future_labels, active)):
            row = {"Period": lbl, "Forecast": f"{val:,.2f}"}
            if ci_lower and ci_upper and i < len(ci_lower):
                row["Lower 95%"] = f"{ci_lower[i]:,.2f}"
                row["Upper 95%"] = f"{ci_upper[i]:,.2f}"
            rows.append(row)
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Multi-metric overview ──
    if len(available) > 1:
        st.markdown("---")
        _render_multi_metric_summary(forecasts, available)

    # ── AI Narrative ──
    if narrative:
        st.markdown("---")
        st.markdown("<p class='section-title'>AI Forecast Narrative</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="fin-card fin-card-accent">
            {narrative}
        </div>
        """, unsafe_allow_html=True)


def _render_multi_metric_summary(forecasts: dict, available: list):
    st.markdown("<p class='section-title'>Multi-Metric Outlook Summary</p>", unsafe_allow_html=True)

    cols = st.columns(min(len(available), 4))
    for i, metric in enumerate(available[:4]):
        fdata = forecasts[metric]
        trend = fdata.get("trend", {})
        cagr = fdata.get("cagr_pct")
        direction = trend.get("direction", "—")
        arrow = "↑" if direction == "upward" else "↓"
        color = "#10b981" if direction == "upward" else "#ef4444"

        with cols[i % 4]:
            st.markdown(f"""
            <div class="fin-card" style="text-align:center;">
                <div class="section-title">{metric.replace('_',' ').title()}</div>
                <div style="font-size:2rem;color:{color};">{arrow}</div>
                <div style="font-size:0.75rem;color:var(--text-secondary);">
                    {f'CAGR {cagr:.1f}%' if cagr else 'Trend: ' + direction}
                </div>
            </div>
            """, unsafe_allow_html=True)
