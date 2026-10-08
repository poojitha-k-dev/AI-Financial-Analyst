"""
Industry Benchmarking Service
Provides median KPI benchmarks by sector for comparison.
Data is based on publicly available industry median values.
"""
from typing import Dict, Any, Optional


# Industry medians — key KPIs by sector
# Sources: Damodaran NYU datasets, S&P industry averages
INDUSTRY_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Technology": {
        "gross_margin": 58.0,
        "operating_margin": 18.0,
        "net_margin": 14.0,
        "return_on_equity": 22.0,
        "return_on_assets": 9.0,
        "current_ratio": 2.1,
        "debt_to_equity": 0.45,
        "asset_turnover": 0.65,
        "ebitda_margin": 24.0,
        "fcf_margin": 12.0,
        "revenue_growth": 12.0,
    },
    "Healthcare": {
        "gross_margin": 55.0,
        "operating_margin": 12.0,
        "net_margin": 9.0,
        "return_on_equity": 15.0,
        "return_on_assets": 6.0,
        "current_ratio": 2.5,
        "debt_to_equity": 0.6,
        "asset_turnover": 0.55,
        "ebitda_margin": 18.0,
        "fcf_margin": 8.0,
        "revenue_growth": 8.0,
    },
    "Finance": {
        "gross_margin": 45.0,
        "operating_margin": 22.0,
        "net_margin": 18.0,
        "return_on_equity": 12.0,
        "return_on_assets": 1.2,
        "current_ratio": 1.2,
        "debt_to_equity": 4.0,
        "asset_turnover": 0.08,
        "ebitda_margin": 30.0,
        "fcf_margin": 15.0,
        "revenue_growth": 6.0,
    },
    "Consumer Discretionary": {
        "gross_margin": 35.0,
        "operating_margin": 8.0,
        "net_margin": 5.5,
        "return_on_equity": 16.0,
        "return_on_assets": 5.0,
        "current_ratio": 1.5,
        "debt_to_equity": 1.1,
        "asset_turnover": 1.1,
        "ebitda_margin": 13.0,
        "fcf_margin": 4.0,
        "revenue_growth": 7.0,
    },
    "Consumer Staples": {
        "gross_margin": 32.0,
        "operating_margin": 11.0,
        "net_margin": 7.0,
        "return_on_equity": 20.0,
        "return_on_assets": 7.0,
        "current_ratio": 1.2,
        "debt_to_equity": 0.9,
        "asset_turnover": 1.0,
        "ebitda_margin": 16.0,
        "fcf_margin": 6.0,
        "revenue_growth": 4.0,
    },
    "Energy": {
        "gross_margin": 30.0,
        "operating_margin": 10.0,
        "net_margin": 6.0,
        "return_on_equity": 10.0,
        "return_on_assets": 4.0,
        "current_ratio": 1.3,
        "debt_to_equity": 0.8,
        "asset_turnover": 0.4,
        "ebitda_margin": 22.0,
        "fcf_margin": 5.0,
        "revenue_growth": 3.0,
    },
    "Industrials": {
        "gross_margin": 28.0,
        "operating_margin": 9.0,
        "net_margin": 6.0,
        "return_on_equity": 14.0,
        "return_on_assets": 5.0,
        "current_ratio": 1.8,
        "debt_to_equity": 0.75,
        "asset_turnover": 0.75,
        "ebitda_margin": 14.0,
        "fcf_margin": 5.0,
        "revenue_growth": 5.0,
    },
    "Materials": {
        "gross_margin": 26.0,
        "operating_margin": 10.0,
        "net_margin": 6.5,
        "return_on_equity": 11.0,
        "return_on_assets": 4.5,
        "current_ratio": 1.9,
        "debt_to_equity": 0.7,
        "asset_turnover": 0.65,
        "ebitda_margin": 16.0,
        "fcf_margin": 4.5,
        "revenue_growth": 4.0,
    },
    "Real Estate": {
        "gross_margin": 60.0,
        "operating_margin": 25.0,
        "net_margin": 15.0,
        "return_on_equity": 8.0,
        "return_on_assets": 3.0,
        "current_ratio": 1.0,
        "debt_to_equity": 1.5,
        "asset_turnover": 0.12,
        "ebitda_margin": 40.0,
        "fcf_margin": 10.0,
        "revenue_growth": 5.0,
    },
    "Utilities": {
        "gross_margin": 38.0,
        "operating_margin": 15.0,
        "net_margin": 10.0,
        "return_on_equity": 10.0,
        "return_on_assets": 3.0,
        "current_ratio": 0.9,
        "debt_to_equity": 1.3,
        "asset_turnover": 0.2,
        "ebitda_margin": 30.0,
        "fcf_margin": 3.0,
        "revenue_growth": 2.0,
    },
    "Communication Services": {
        "gross_margin": 50.0,
        "operating_margin": 14.0,
        "net_margin": 10.0,
        "return_on_equity": 18.0,
        "return_on_assets": 7.0,
        "current_ratio": 1.5,
        "debt_to_equity": 0.9,
        "asset_turnover": 0.45,
        "ebitda_margin": 28.0,
        "fcf_margin": 9.0,
        "revenue_growth": 8.0,
    },
    "Default": {
        "gross_margin": 38.0,
        "operating_margin": 11.0,
        "net_margin": 7.5,
        "return_on_equity": 14.0,
        "return_on_assets": 5.0,
        "current_ratio": 1.6,
        "debt_to_equity": 0.85,
        "asset_turnover": 0.65,
        "ebitda_margin": 18.0,
        "fcf_margin": 6.0,
        "revenue_growth": 6.0,
    },
}


def get_industry_benchmarks(sector: Optional[str]) -> Dict[str, Any]:
    benchmarks = INDUSTRY_BENCHMARKS.get(sector or "Default", INDUSTRY_BENCHMARKS["Default"])
    return {
        "sector": sector or "General",
        "metrics": benchmarks,
        "source": "Industry median benchmarks (Damodaran / S&P averages)",
    }


def compare_to_benchmarks(kpis: Dict[str, Any], sector: Optional[str]) -> Dict[str, Any]:
    """
    Returns a comparison dict with delta vs industry median and performance rating.
    """
    benchmarks = get_industry_benchmarks(sector)
    median = benchmarks["metrics"]
    comparisons = {}

    flat_kpis = {}
    for category in ["profitability", "liquidity", "leverage", "cash_flow", "growth"]:
        flat_kpis.update(kpis.get(category, {}))

    for metric, industry_val in median.items():
        company_val = flat_kpis.get(metric)
        if company_val is None:
            continue
        delta = company_val - industry_val
        pct_diff = (delta / abs(industry_val) * 100) if industry_val else 0

        # Higher is better for margins, returns, ratios (except debt ratios)
        higher_is_better = metric not in ("debt_to_equity",)
        if higher_is_better:
            if pct_diff > 20:
                rating = "Outperforming"
            elif pct_diff > 0:
                rating = "Above Average"
            elif pct_diff > -20:
                rating = "Below Average"
            else:
                rating = "Underperforming"
        else:
            # Lower D/E is better
            if pct_diff < -20:
                rating = "Outperforming"
            elif pct_diff < 0:
                rating = "Above Average"
            elif pct_diff < 20:
                rating = "Below Average"
            else:
                rating = "Underperforming"

        comparisons[metric] = {
            "company_value": round(company_val, 2),
            "industry_median": round(industry_val, 2),
            "delta": round(delta, 2),
            "pct_vs_industry": round(pct_diff, 1),
            "rating": rating,
        }

    return {
        "sector": sector or "General",
        "comparisons": comparisons,
        "outperforming_count": sum(1 for v in comparisons.values() if v["rating"] == "Outperforming"),
        "underperforming_count": sum(1 for v in comparisons.values() if v["rating"] == "Underperforming"),
    }
