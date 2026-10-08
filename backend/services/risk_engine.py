"""
Advanced Risk Analysis Engine
- Altman Z-Score (bankruptcy prediction)
- Beneish M-Score (earnings manipulation)
- Piotroski F-Score (financial strength)
- Custom multi-factor risk scoring
- Anomaly detection
"""
from typing import Dict, Any, Optional, List
import math


def analyse_risk(
    data: Dict[str, Any],
    kpis: Dict[str, Any],
    previous_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    results["altman_z_score"] = _altman_z_score(data, kpis)
    results["piotroski_f_score"] = _piotroski_f_score(data, kpis, previous_data)
    results["beneish_m_score"] = _beneish_m_score(data, previous_data) if previous_data else None
    results["custom_risk"] = _custom_risk_score(kpis)
    results["anomalies"] = _detect_anomalies(data, kpis, previous_data)
    results["risk_summary"] = _summarise_risk(results)

    return results


# ─── Altman Z-Score ────────────────────────────────────────────────────────────
def _altman_z_score(data: Dict, kpis: Dict) -> Dict[str, Any]:
    """
    Public company Z-Score:
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    """
    ta = data.get("total_assets")
    te = data.get("total_equity")
    tl = data.get("total_liabilities")
    revenue = data.get("revenue")
    ni = data.get("net_income")
    ebit = data.get("operating_income")
    cl = data.get("total_current_liabilities")
    ca = data.get("total_current_assets")
    td = data.get("total_debt") or ((data.get("short_term_debt") or 0) + (data.get("long_term_debt") or 0))
    retained = ni  # simplified; ideally retained earnings from balance sheet

    if not all([ta, revenue, ebit]):
        return {"score": None, "interpretation": "Insufficient data", "components": {}}

    wc = (ca - cl) if ca and cl else 0

    x1 = wc / ta if ta else 0
    x2 = (retained or 0) / ta if ta else 0
    x3 = ebit / ta if ta else 0
    x4 = (te or 0) / (tl or 1)
    x5 = revenue / ta if ta else 0

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    if z > 2.99:
        zone = "Safe Zone"
        risk_level = "Low"
    elif z > 1.81:
        zone = "Grey Zone"
        risk_level = "Medium"
    else:
        zone = "Distress Zone"
        risk_level = "High"

    return {
        "score": round(z, 2),
        "zone": zone,
        "risk_level": risk_level,
        "interpretation": f"Z-Score of {z:.2f} places the company in the {zone} ({risk_level} bankruptcy risk)",
        "components": {
            "X1_working_capital_ratio": round(x1, 4),
            "X2_retained_earnings_ratio": round(x2, 4),
            "X3_ebit_ratio": round(x3, 4),
            "X4_equity_to_debt": round(x4, 4),
            "X5_asset_turnover": round(x5, 4),
        },
        "thresholds": {"safe": "> 2.99", "grey": "1.81 – 2.99", "distress": "< 1.81"},
    }


# ─── Piotroski F-Score ─────────────────────────────────────────────────────────
def _piotroski_f_score(data: Dict, kpis: Dict, prev: Optional[Dict]) -> Dict[str, Any]:
    """
    9-point financial strength score.
    """
    scores = {}
    total = 0

    def _get_kpi(cat, key):
        return kpis.get(cat, {}).get(key)

    # Profitability (4 points)
    roa = _get_kpi("profitability", "return_on_assets")
    scores["positive_roa"] = 1 if roa and roa > 0 else 0
    total += scores["positive_roa"]

    ocf = data.get("operating_cash_flow")
    scores["positive_ocf"] = 1 if ocf and ocf > 0 else 0
    total += scores["positive_ocf"]

    ni = data.get("net_income")
    ta = data.get("total_assets")
    prev_roa = ((prev.get("net_income", 0) or 0) / prev.get("total_assets", 1)) * 100 if prev else None
    scores["roa_improving"] = 1 if (roa and prev_roa and roa > prev_roa) else 0
    total += scores["roa_improving"]

    scores["accrual_positive"] = 1 if (ocf and ni and ocf > ni) else 0
    total += scores["accrual_positive"]

    # Leverage (3 points)
    de_now = _get_kpi("leverage", "debt_to_equity")
    de_prev = None
    if prev:
        prev_de = (prev.get("total_debt") or 0) / (prev.get("total_equity") or 1)
        de_prev = prev_de
    scores["leverage_improving"] = 1 if (de_now is not None and de_prev is not None and de_now < de_prev) else 0
    total += scores["leverage_improving"]

    cr_now = _get_kpi("liquidity", "current_ratio")
    cr_prev = ((prev.get("total_current_assets") or 0) / (prev.get("total_current_liabilities") or 1)) if prev else None
    scores["liquidity_improving"] = 1 if (cr_now and cr_prev and cr_now > cr_prev) else 0
    total += scores["liquidity_improving"]

    scores["no_dilution"] = 1  # simplified; would check shares outstanding
    total += scores["no_dilution"]

    # Operating Efficiency (2 points)
    gm_now = _get_kpi("profitability", "gross_margin")
    gm_prev = None
    if prev and prev.get("revenue"):
        gp_prev = prev.get("gross_profit") or (prev.get("revenue") - (prev.get("cost_of_goods_sold") or 0))
        gm_prev = (gp_prev / prev["revenue"]) * 100 if prev["revenue"] else None
    scores["margin_improving"] = 1 if (gm_now and gm_prev and gm_now > gm_prev) else 0
    total += scores["margin_improving"]

    at_now = _get_kpi("efficiency", "asset_turnover")
    at_prev = (prev.get("revenue") / prev.get("total_assets")) if (prev and prev.get("total_assets")) else None
    scores["turnover_improving"] = 1 if (at_now and at_prev and at_now > at_prev) else 0
    total += scores["turnover_improving"]

    if total >= 7:
        strength = "Strong"
    elif total >= 4:
        strength = "Moderate"
    else:
        strength = "Weak"

    return {
        "score": total,
        "max_score": 9,
        "strength": strength,
        "components": scores,
        "interpretation": f"Piotroski F-Score of {total}/9 indicates {strength} financial position",
    }


# ─── Beneish M-Score ───────────────────────────────────────────────────────────
def _beneish_m_score(data: Dict, prev: Dict) -> Dict[str, Any]:
    """
    8-variable earnings manipulation model.
    M-Score > -1.78 → likely manipulator
    """
    if not prev:
        return {"score": None, "interpretation": "Requires prior period data"}

    def safe(num, den):
        if not den or den == 0:
            return 1.0
        return (num or 0) / den

    # DSRI - Days Sales Receivable Index
    dsr_now = safe(data.get("accounts_receivable"), data.get("revenue"))
    dsr_prev = safe(prev.get("accounts_receivable"), prev.get("revenue"))
    dsri = safe(dsr_now, dsr_prev)

    # GMI - Gross Margin Index
    gm_now = safe(
        (data.get("revenue") or 0) - (data.get("cost_of_goods_sold") or 0),
        data.get("revenue")
    )
    gm_prev = safe(
        (prev.get("revenue") or 0) - (prev.get("cost_of_goods_sold") or 0),
        prev.get("revenue")
    )
    gmi = safe(gm_prev, gm_now)

    # AQI - Asset Quality Index
    aq_now = safe(
        (data.get("total_assets") or 0) - (data.get("total_current_assets") or 0),
        data.get("total_assets")
    )
    aq_prev = safe(
        (prev.get("total_assets") or 0) - (prev.get("total_current_assets") or 0),
        prev.get("total_assets")
    )
    aqi = safe(aq_now, aq_prev)

    # SGI - Sales Growth Index
    sgi = safe(data.get("revenue"), prev.get("revenue"))

    # DEPI - Depreciation Index (simplified)
    depi = 1.0

    # SGAI - SGA Expense Index (simplified)
    sgai = 1.0

    # LVGI - Leverage Index
    lev_now = safe(
        (data.get("total_debt") or 0),
        data.get("total_assets")
    )
    lev_prev = safe(
        (prev.get("total_debt") or 0),
        prev.get("total_assets")
    )
    lvgi = safe(lev_now, lev_prev)

    # TATA - Total Accruals to Total Assets
    ni = data.get("net_income") or 0
    ocf = data.get("operating_cash_flow") or 0
    ta = data.get("total_assets") or 1
    tata = (ni - ocf) / ta

    m_score = (
        -4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi +
        0.892 * sgi + 0.115 * depi - 0.172 * sgai +
        4.679 * tata - 0.327 * lvgi
    )

    manipulator = m_score > -1.78

    return {
        "score": round(m_score, 3),
        "likely_manipulator": manipulator,
        "threshold": -1.78,
        "interpretation": (
            f"M-Score of {m_score:.3f} {'EXCEEDS' if manipulator else 'is below'} the threshold of -1.78. "
            f"{'High probability of earnings manipulation.' if manipulator else 'Low manipulation risk.'}"
        ),
        "components": {
            "DSRI": round(dsri, 3),
            "GMI": round(gmi, 3),
            "AQI": round(aqi, 3),
            "SGI": round(sgi, 3),
            "LVGI": round(lvgi, 3),
            "TATA": round(tata, 3),
        },
    }


# ─── Custom Risk Score ─────────────────────────────────────────────────────────
def _custom_risk_score(kpis: Dict) -> Dict[str, Any]:
    risks = []
    score = 0  # higher = more risk

    def _get(cat, key):
        return kpis.get(cat, {}).get(key)

    # Liquidity risks
    cr = _get("liquidity", "current_ratio")
    if cr is not None:
        if cr < 1.0:
            risks.append({"factor": "Critical liquidity", "detail": f"Current ratio {cr:.2f} < 1.0", "severity": "high"})
            score += 3
        elif cr < 1.5:
            risks.append({"factor": "Low liquidity", "detail": f"Current ratio {cr:.2f} < 1.5", "severity": "medium"})
            score += 1

    # Profitability risks
    nm = _get("profitability", "net_margin")
    if nm is not None and nm < 0:
        risks.append({"factor": "Negative net margin", "detail": f"Net margin {nm:.1f}%", "severity": "high"})
        score += 3
    elif nm is not None and nm < 2:
        risks.append({"factor": "Very thin margins", "detail": f"Net margin {nm:.1f}%", "severity": "medium"})
        score += 1

    # Leverage risks
    de = _get("leverage", "debt_to_equity")
    if de is not None:
        if de > 3:
            risks.append({"factor": "High leverage", "detail": f"D/E ratio {de:.2f}", "severity": "high"})
            score += 3
        elif de > 2:
            risks.append({"factor": "Elevated leverage", "detail": f"D/E ratio {de:.2f}", "severity": "medium"})
            score += 1

    # Interest coverage
    ic = _get("leverage", "interest_coverage")
    if ic is not None and ic < 1.5:
        risks.append({"factor": "Low interest coverage", "detail": f"Coverage {ic:.2f}x", "severity": "high"})
        score += 2

    # Cash flow
    fcf_margin = _get("cash_flow", "fcf_margin")
    if fcf_margin is not None and fcf_margin < 0:
        risks.append({"factor": "Negative free cash flow", "detail": f"FCF margin {fcf_margin:.1f}%", "severity": "medium"})
        score += 2

    # Score normalisation (0–10)
    normalised = min(score, 10)
    if normalised >= 7:
        level = "Critical"
    elif normalised >= 4:
        level = "High"
    elif normalised >= 2:
        level = "Medium"
    else:
        level = "Low"

    return {
        "risk_score": normalised,
        "risk_level": level,
        "risk_factors": risks,
        "total_flags": len(risks),
    }


# ─── Anomaly Detection ────────────────────────────────────────────────────────
def _detect_anomalies(
    data: Dict, kpis: Dict, prev: Optional[Dict]
) -> List[Dict[str, Any]]:
    anomalies = []

    if not prev:
        return anomalies

    # Check for sudden large swings
    metrics_to_check = [
        ("revenue", "Revenue"),
        ("net_income", "Net Income"),
        ("total_debt", "Total Debt"),
        ("operating_cash_flow", "Operating Cash Flow"),
        ("gross_profit", "Gross Profit"),
    ]

    for key, label in metrics_to_check:
        curr_val = data.get(key)
        prev_val = prev.get(key)
        if curr_val is not None and prev_val and prev_val != 0:
            change = ((curr_val - prev_val) / abs(prev_val)) * 100
            if abs(change) > 50:
                anomalies.append({
                    "metric": label,
                    "change_pct": round(change, 1),
                    "severity": "high" if abs(change) > 100 else "medium",
                    "detail": f"{label} changed by {change:+.1f}% vs prior period",
                })

    # Revenue – net income divergence
    rev = data.get("revenue")
    ni = data.get("net_income")
    prev_rev = prev.get("revenue")
    prev_ni = prev.get("net_income")
    if all([rev, ni, prev_rev, prev_ni]) and prev_rev and prev_ni:
        rev_growth = (rev - prev_rev) / abs(prev_rev)
        ni_growth = (ni - prev_ni) / abs(prev_ni)
        if rev_growth > 0.1 and ni_growth < -0.2:
            anomalies.append({
                "metric": "Revenue-Profit Divergence",
                "severity": "high",
                "detail": f"Revenue grew {rev_growth*100:.1f}% while net income fell {ni_growth*100:.1f}%",
            })

    return anomalies


def _summarise_risk(results: Dict) -> Dict[str, Any]:
    levels = []

    altman = results.get("altman_z_score", {})
    if altman.get("risk_level"):
        levels.append(altman["risk_level"])

    custom = results.get("custom_risk", {})
    if custom.get("risk_level"):
        levels.append(custom["risk_level"])

    # Aggregate to worst case
    order = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    worst = max(levels, key=lambda x: order.get(x, 0)) if levels else "Unknown"

    piotroski = results.get("piotroski_f_score", {})

    return {
        "overall_risk_level": worst,
        "piotroski_strength": piotroski.get("strength", "Unknown"),
        "total_risk_flags": len(results.get("custom_risk", {}).get("risk_factors", [])),
        "anomaly_count": len(results.get("anomalies", [])),
    }
