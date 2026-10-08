"""
KPI Calculation Engine
Computes 40+ financial ratios across profitability, liquidity, leverage,
efficiency, valuation, and growth categories.
"""
from typing import Dict, Any, Optional
import math


def safe_div(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def calculate_kpis(data: Dict[str, Any], previous_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Args:
        data: current period financial data dict
        previous_data: prior period data for growth / trend calculations
    Returns:
        kpis dict with categories
    """
    d = data
    p = previous_data or {}

    kpis: Dict[str, Any] = {
        "profitability": {},
        "liquidity": {},
        "leverage": {},
        "efficiency": {},
        "growth": {},
        "valuation": {},
        "cash_flow": {},
        "quality": {},
    }

    # ── Derive missing values ──────────────────────────────────────────────
    revenue = d.get("revenue")
    cogs = d.get("cost_of_goods_sold")
    gross_profit = d.get("gross_profit") or (
        (revenue - cogs) if revenue is not None and cogs is not None else None
    )
    operating_income = d.get("operating_income")
    net_income = d.get("net_income")
    ebitda = d.get("ebitda")
    interest_expense = d.get("interest_expense")
    income_tax = d.get("income_tax")
    income_before_tax = d.get("income_before_tax")

    total_assets = d.get("total_assets")
    total_equity = d.get("total_equity")
    total_liabilities = d.get("total_liabilities")
    total_debt = d.get("total_debt") or (
        (d.get("short_term_debt", 0) or 0) + (d.get("long_term_debt", 0) or 0)
    ) or None
    cash = d.get("cash_and_equivalents")
    current_assets = d.get("total_current_assets")
    current_liabilities = d.get("total_current_liabilities")
    inventory = d.get("inventory")
    accounts_receivable = d.get("accounts_receivable")
    accounts_payable = d.get("accounts_payable")

    ocf = d.get("operating_cash_flow")
    capex = d.get("capex")
    fcf = d.get("free_cash_flow") or (
        (ocf - abs(capex)) if ocf is not None and capex is not None else None
    )

    # ── Profitability ──────────────────────────────────────────────────────
    pr = kpis["profitability"]
    pr["gross_margin"] = _pct(safe_div(gross_profit, revenue))
    pr["operating_margin"] = _pct(safe_div(operating_income, revenue))
    pr["net_margin"] = _pct(safe_div(net_income, revenue))
    pr["ebitda_margin"] = _pct(safe_div(ebitda, revenue))
    pr["return_on_assets"] = _pct(safe_div(net_income, total_assets))
    pr["return_on_equity"] = _pct(safe_div(net_income, total_equity))

    # ROCE
    capital_employed = (
        (total_assets - (current_liabilities or 0))
        if total_assets is not None and current_liabilities is not None else None
    )
    pr["return_on_capital_employed"] = _pct(safe_div(operating_income, capital_employed))

    # Effective tax rate
    pr["effective_tax_rate"] = _pct(safe_div(income_tax, income_before_tax))

    # ── Liquidity ──────────────────────────────────────────────────────────
    liq = kpis["liquidity"]
    liq["current_ratio"] = safe_div(current_assets, current_liabilities)
    quick_assets = (
        (current_assets - (inventory or 0))
        if current_assets is not None else None
    )
    liq["quick_ratio"] = safe_div(quick_assets, current_liabilities)
    liq["cash_ratio"] = safe_div(cash, current_liabilities)
    liq["operating_cash_flow_ratio"] = safe_div(ocf, current_liabilities)

    # ── Leverage ──────────────────────────────────────────────────────────
    lev = kpis["leverage"]
    lev["debt_to_equity"] = safe_div(total_debt, total_equity)
    lev["debt_to_assets"] = safe_div(total_debt, total_assets)
    lev["equity_multiplier"] = safe_div(total_assets, total_equity)
    net_debt = (
        (total_debt - cash) if total_debt is not None and cash is not None else None
    )
    lev["net_debt_to_ebitda"] = safe_div(net_debt, ebitda)
    lev["interest_coverage"] = safe_div(operating_income, interest_expense)
    lev["debt_service_coverage"] = safe_div(ocf, interest_expense)

    # ── Efficiency ────────────────────────────────────────────────────────
    eff = kpis["efficiency"]
    eff["asset_turnover"] = safe_div(revenue, total_assets)
    eff["inventory_turnover"] = safe_div(cogs, inventory)
    eff["days_inventory_outstanding"] = _days(safe_div(inventory, cogs))
    eff["receivables_turnover"] = safe_div(revenue, accounts_receivable)
    eff["days_sales_outstanding"] = _days(safe_div(accounts_receivable, revenue))
    eff["payables_turnover"] = safe_div(cogs, accounts_payable)
    eff["days_payable_outstanding"] = _days(safe_div(accounts_payable, cogs))

    dio = eff["days_inventory_outstanding"]
    dso = eff["days_sales_outstanding"]
    dpo = eff["days_payable_outstanding"]
    if dio is not None and dso is not None:
        cash_conversion_cycle = dio + dso - (dpo or 0)
        eff["cash_conversion_cycle"] = round(cash_conversion_cycle, 2)
    else:
        eff["cash_conversion_cycle"] = None

    # ── Cash Flow ─────────────────────────────────────────────────────────
    cf = kpis["cash_flow"]
    cf["free_cash_flow"] = fcf
    cf["fcf_margin"] = _pct(safe_div(fcf, revenue))
    cf["capex_to_revenue"] = _pct(safe_div(capex, revenue))
    cf["ocf_to_net_income"] = safe_div(ocf, net_income)
    cf["capex_intensity"] = _pct(safe_div(capex, total_assets))

    # ── Quality of Earnings ───────────────────────────────────────────────
    qual = kpis["quality"]
    qual["accrual_ratio"] = safe_div(
        (net_income - ocf if net_income and ocf else None), total_assets
    )
    qual["cash_earnings_quality"] = safe_div(ocf, net_income)

    # ── Growth (requires prior period) ────────────────────────────────────
    gr = kpis["growth"]
    if p:
        gr["revenue_growth"] = _growth(revenue, p.get("revenue"))
        gr["gross_profit_growth"] = _growth(gross_profit, p.get("gross_profit"))
        gr["operating_income_growth"] = _growth(operating_income, p.get("operating_income"))
        gr["net_income_growth"] = _growth(net_income, p.get("net_income"))
        gr["ebitda_growth"] = _growth(ebitda, p.get("ebitda"))
        gr["fcf_growth"] = _growth(fcf, p.get("free_cash_flow"))
        gr["total_assets_growth"] = _growth(total_assets, p.get("total_assets"))

    # ── Composite Scores ──────────────────────────────────────────────────
    kpis["composite_scores"] = calculate_composite_scores(kpis)

    # Remove None values for cleanliness
    kpis = _clean_none(kpis)
    return kpis


def calculate_composite_scores(kpis: Dict) -> Dict[str, Any]:
    """Piotroski F-Score style composite health scores (0–10 scale)."""
    scores = {}

    def _get(category, key):
        return kpis.get(category, {}).get(key)

    profitability_score = 0
    if _get("profitability", "net_margin") and _get("profitability", "net_margin") > 0:
        profitability_score += 2
    if _get("profitability", "return_on_assets") and _get("profitability", "return_on_assets") > 5:
        profitability_score += 2
    if _get("profitability", "gross_margin") and _get("profitability", "gross_margin") > 20:
        profitability_score += 2
    if _get("cash_flow", "ocf_to_net_income") and _get("cash_flow", "ocf_to_net_income") > 1:
        profitability_score += 2
    if _get("profitability", "operating_margin") and _get("profitability", "operating_margin") > 10:
        profitability_score += 2
    scores["profitability_score"] = min(profitability_score, 10)

    liquidity_score = 0
    cr = _get("liquidity", "current_ratio")
    if cr:
        if cr >= 2:
            liquidity_score += 4
        elif cr >= 1.5:
            liquidity_score += 3
        elif cr >= 1:
            liquidity_score += 2
    qr = _get("liquidity", "quick_ratio")
    if qr:
        if qr >= 1:
            liquidity_score += 3
        elif qr >= 0.7:
            liquidity_score += 2
    ic = _get("leverage", "interest_coverage")
    if ic and ic >= 3:
        liquidity_score += 3
    scores["liquidity_score"] = min(liquidity_score, 10)

    leverage_score = 0
    de = _get("leverage", "debt_to_equity")
    if de is not None:
        if de < 0.5:
            leverage_score += 4
        elif de < 1:
            leverage_score += 3
        elif de < 2:
            leverage_score += 2
        else:
            leverage_score += 1
    nde = _get("leverage", "net_debt_to_ebitda")
    if nde is not None:
        if nde < 1:
            leverage_score += 4
        elif nde < 2:
            leverage_score += 3
        elif nde < 3:
            leverage_score += 2
        else:
            leverage_score += 1
    scores["leverage_score"] = min(leverage_score + 2, 10)

    # Overall financial health (weighted average)
    scores["overall_health"] = round(
        (scores["profitability_score"] * 0.4 +
         scores["liquidity_score"] * 0.3 +
         scores["leverage_score"] * 0.3), 1
    )

    return scores


def _pct(val: Optional[float]) -> Optional[float]:
    if val is None:
        return None
    return round(val * 100, 2)


def _days(val: Optional[float]) -> Optional[float]:
    if val is None:
        return None
    return round(val * 365, 1)


def _growth(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous is None or previous == 0:
        return None
    return _pct((current - previous) / abs(previous))


def _clean_none(obj):
    if isinstance(obj, dict):
        return {k: _clean_none(v) for k, v in obj.items() if v is not None}
    return obj
