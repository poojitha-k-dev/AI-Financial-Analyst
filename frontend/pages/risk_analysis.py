import streamlit as st
import plotly.graph_objects as go
from frontend import api_client as api
from frontend.theme import page_header, risk_pill


def show():
    page_header("Risk Analysis", "Altman Z-Score · Beneish M-Score · Piotroski F-Score · Custom Risk Flags", "⚠️")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    with col2:
        run = st.button("🔍 Run Risk Analysis", use_container_width=True, type="primary")

    cid = company_map[selected]

    if run:
        with st.spinner("Analysing risk factors..."):
            result = api.get_risk(cid)

        if result:
            st.session_state["last_risk"] = result

    result = st.session_state.get("last_risk")
    if not result:
        st.info("Click **Run Risk Analysis** to start.")
        return

    risk = result.get("risk_analysis", {})
    narrative = result.get("narrative", "")
    period = result.get("period", "Latest")

    # ── Summary Banner ──
    summary = risk.get("risk_summary", {})
    level = summary.get("overall_risk_level", "Unknown")
    color_map = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444", "Critical": "#dc2626"}
    color = color_map.get(level, "#64748b")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color}15,{color}05);
                border:2px solid {color};border-radius:var(--radius);
                padding:1.25rem 1.75rem;margin:1rem 0;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;
                            letter-spacing:0.1em;">Overall Risk Level</div>
                <div style="font-size:2rem;font-weight:700;color:{color};margin:4px 0;">{level}</div>
                <div style="font-size:0.82rem;color:var(--text-secondary);">
                    Period: {period} | Piotroski: {summary.get('piotroski_strength','—')} | 
                    Flags: {summary.get('total_risk_flags',0)} | 
                    Anomalies: {summary.get('anomaly_count',0)}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Model Tabs ──
    tabs = st.tabs(["🏦 Altman Z-Score", "📊 Piotroski F-Score", "🔍 Beneish M-Score",
                    "🚩 Risk Flags", "📈 Anomalies", "🤖 AI Narrative"])

    with tabs[0]:
        _render_altman(risk.get("altman_z_score", {}))

    with tabs[1]:
        _render_piotroski(risk.get("piotroski_f_score", {}))

    with tabs[2]:
        _render_beneish(risk.get("beneish_m_score"))

    with tabs[3]:
        _render_flags(risk.get("custom_risk", {}))

    with tabs[4]:
        _render_anomalies(risk.get("anomalies", []))

    with tabs[5]:
        if narrative:
            st.markdown(narrative)
        else:
            st.info("Run analysis to generate AI narrative.")


def _render_altman(altman: dict):
    if not altman or altman.get("score") is None:
        st.info("Insufficient data to calculate Altman Z-Score.")
        return

    score = altman["score"]
    zone = altman.get("zone", "")
    zone_colors = {"Safe Zone": "#10b981", "Grey Zone": "#f59e0b", "Distress Zone": "#ef4444"}
    color = zone_colors.get(zone, "#64748b")

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"font": {"size": 42, "color": color}},
            title={"text": "Z-Score", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 5], "tickwidth": 1},
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 1.81], "color": "rgba(239,68,68,0.15)"},
                    {"range": [1.81, 2.99], "color": "rgba(245,158,11,0.15)"},
                    {"range": [2.99, 5], "color": "rgba(16,185,129,0.15)"},
                ],
                "threshold": {"line": {"color": "white", "width": 2}, "value": score},
            },
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=280,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### {zone}")
        st.markdown(f"**Score:** `{score:.2f}`")
        st.markdown(altman.get("interpretation", ""))

        with st.expander("📐 Formula Components", expanded=False):
            components = altman.get("components", {})
            for k, v in components.items():
                st.markdown(f"- **{k}:** `{v}`")

        thresholds = altman.get("thresholds", {})
        st.markdown("**Interpretation:**")
        for k, v in thresholds.items():
            st.markdown(f"- {k.title()}: `{v}`")


def _render_piotroski(p: dict):
    if not p:
        st.info("Insufficient data.")
        return

    score = p.get("score", 0)
    strength = p.get("strength", "")
    color = "#10b981" if strength == "Strong" else "#f59e0b" if strength == "Moderate" else "#ef4444"

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = go.Figure(go.Indicator(
            mode="number+gauge",
            value=score,
            number={"suffix": "/9", "font": {"size": 48, "color": color}},
            title={"text": strength, "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 9]},
                "bar": {"color": color, "thickness": 0.3},
                "steps": [
                    {"range": [0, 3], "color": "rgba(239,68,68,0.12)"},
                    {"range": [3, 6], "color": "rgba(245,158,11,0.12)"},
                    {"range": [6, 9], "color": "rgba(16,185,129,0.12)"},
                ],
            },
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=280,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(p.get("interpretation", ""))
        st.markdown("**9-Point Checklist:**")
        components = p.get("components", {})
        for k, v in components.items():
            icon = "✅" if v == 1 else "❌"
            st.markdown(f"{icon} {k.replace('_', ' ').title()}")


def _render_beneish(b):
    if not b or b.get("score") is None:
        st.info(b.get("interpretation", "Requires two periods of data.") if b else "Requires two periods of data.")
        return

    score = b["score"]
    manipulator = b.get("likely_manipulator", False)
    color = "#ef4444" if manipulator else "#10b981"
    label = "⚠️ HIGH RISK" if manipulator else "✅ LOW RISK"

    st.markdown(f"""
    <div class="fin-card" style="border-left:4px solid {color};">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="section-title">Beneish M-Score</div>
                <div style="font-size:2.2rem;font-weight:700;color:{color};">{score:.3f}</div>
            </div>
            <div style="font-size:1.5rem;color:{color};">{label}</div>
        </div>
        <p style="margin:12px 0 0;color:var(--text-secondary);font-size:0.85rem;">
            {b.get('interpretation','')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📊 8-Variable Components", expanded=False):
        components = b.get("components", {})
        cols = st.columns(4)
        for i, (k, v) in enumerate(components.items()):
            cols[i % 4].metric(k, f"{v:.3f}")


def _render_flags(custom: dict):
    flags = custom.get("risk_factors", [])
    score = custom.get("risk_score", 0)
    level = custom.get("risk_level", "Unknown")
    color = "#10b981" if score <= 2 else "#f59e0b" if score <= 5 else "#ef4444"

    st.markdown(f"""
    <div class="fin-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="section-title">Custom Risk Score</div>
                <div style="font-size:2rem;font-weight:700;color:{color};">{score}/10</div>
            </div>
            <div style="font-size:1rem;color:{color};font-weight:600;">{level}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not flags:
        st.success("✅ No critical risk flags detected.")
        return

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    for flag in flags:
        sev = flag.get("severity", "medium")
        color = "#ef4444" if sev == "high" else "#f59e0b"
        icon = "🔴" if sev == "high" else "🟡"
        st.markdown(f"""
        <div style="background:var(--bg-card);border-left:4px solid {color};
                    padding:12px 16px;margin:6px 0;border-radius:4px;">
            <div style="display:flex;align-items:start;gap:8px;">
                <span style="font-size:1.1rem;">{icon}</span>
                <div style="flex:1;">
                    <div style="font-weight:600;margin-bottom:3px;">{flag['factor']}</div>
                    <div style="font-size:0.82rem;color:var(--text-secondary);">{flag['detail']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_anomalies(anomalies: list):
    if not anomalies:
        st.success("✅ No anomalies detected in recent period changes.")
        return

    st.markdown(f"**{len(anomalies)} Anomalies Detected**")
    for a in anomalies:
        sev = a.get("severity", "medium")
        color = "#ef4444" if sev == "high" else "#f59e0b"
        change = a.get("change_pct")
        arrow = "📈" if change and change > 0 else "📉"
        st.markdown(f"""
        <div style="background:var(--bg-card);border-left:4px solid {color};
                    padding:12px 16px;margin:6px 0;border-radius:4px;">
            <div style="display:flex;align-items:start;gap:8px;">
                <span style="font-size:1.1rem;">{arrow}</span>
                <div style="flex:1;">
                    <div style="font-weight:600;margin-bottom:3px;">{a['metric']}</div>
                    <div style="font-size:0.82rem;color:var(--text-secondary);">{a['detail']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
