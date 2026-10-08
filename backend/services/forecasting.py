"""
Time-series forecasting for financial metrics.
Uses: Linear Regression, Exponential Smoothing, ARIMA-style via statsmodels
"""
from typing import Dict, Any, List, Optional
import numpy as np


def forecast_metrics(
    historical_series: Dict[str, List[float]],
    periods_ahead: int = 4,
) -> Dict[str, Any]:
    """
    Args:
        historical_series: {metric_name: [val1, val2, ...]} time-ordered list
        periods_ahead: how many future periods to forecast
    Returns:
        forecasts dict per metric
    """
    results = {}
    for metric, values in historical_series.items():
        clean = [v for v in values if v is not None]
        if len(clean) < 2:
            results[metric] = {"error": "Insufficient data points"}
            continue
        results[metric] = _forecast_single(clean, periods_ahead)
    return results


def _forecast_single(values: List[float], periods_ahead: int) -> Dict[str, Any]:
    n = len(values)
    x = np.arange(n)
    y = np.array(values)

    # Linear regression
    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs
    future_x = np.arange(n, n + periods_ahead)
    linear_forecast = (slope * future_x + intercept).tolist()

    # Exponential smoothing (simple)
    alpha = 0.3
    smoothed = [values[0]]
    for v in values[1:]:
        smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])

    # Project using the last smoothed value + trend
    last_smooth = smoothed[-1]
    trend = (smoothed[-1] - smoothed[-2]) if len(smoothed) >= 2 else 0
    exp_forecast = [last_smooth + trend * (i + 1) for i in range(periods_ahead)]

    # Ensemble (average)
    ensemble = [(l + e) / 2 for l, e in zip(linear_forecast, exp_forecast)]

    # Confidence interval (±1 std of residuals)
    residuals = y - (slope * x + intercept)
    std = float(np.std(residuals))

    # CAGR
    cagr = None
    if values[0] and values[0] > 0 and values[-1] and values[-1] > 0:
        cagr = ((values[-1] / values[0]) ** (1 / max(n - 1, 1)) - 1) * 100

    return {
        "historical": values,
        "linear_forecast": [round(v, 2) for v in linear_forecast],
        "exponential_forecast": [round(v, 2) for v in exp_forecast],
        "ensemble_forecast": [round(v, 2) for v in ensemble],
        "confidence_interval": {
            "lower": [round(v - 1.96 * std, 2) for v in ensemble],
            "upper": [round(v + 1.96 * std, 2) for v in ensemble],
        },
        "trend": {
            "slope": round(float(slope), 4),
            "direction": "upward" if slope > 0 else "downward",
            "r_squared": float(_r_squared(y, slope * x + intercept)),
        },
        "cagr_pct": round(cagr, 2) if cagr else None,
    }


def _r_squared(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 1.0
    return 1 - (ss_res / ss_tot)


def build_historical_series(statements: List[Dict]) -> Dict[str, List[float]]:
    """
    Convert a list of financial statement dicts (sorted oldest→newest)
    into per-metric time series.
    """
    metrics = [
        "revenue", "net_income", "gross_profit", "operating_income",
        "ebitda", "total_assets", "total_equity", "total_debt",
        "operating_cash_flow", "free_cash_flow",
    ]
    series: Dict[str, List[float]] = {m: [] for m in metrics}
    for stmt in statements:
        for m in metrics:
            series[m].append(stmt.get(m))
    return series
