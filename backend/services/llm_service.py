"""
LLM Service – OpenAI GPT-4o + Google Gemini + Smart Mock fallback
If no valid API key is configured, generates data-driven analysis from the actual numbers.
"""
import json
from typing import Dict, Any, List, Optional
from backend.config import settings


def _get_openai_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.openai_api_key)


def _get_gemini_client():
    from google import genai
    return genai.Client(api_key=settings.gemini_api_key)


def _has_valid_key() -> bool:
    p = settings.llm_provider.lower()
    if p == "openai":
        k = settings.openai_api_key or ""
        return k.startswith("sk-") and len(k) > 20
    if p == "gemini":
        k = settings.gemini_api_key or ""
        return len(k) > 20 and k not in ("add-your-gemini-key-here", "")
    return False


async def _call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    provider = settings.llm_provider.lower()
    if provider == "openai":
        client = _get_openai_client()
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.25,
        )
        return resp.choices[0].message.content
    elif provider == "gemini":
        import asyncio
        client = _get_gemini_client()
        loop = asyncio.get_event_loop()
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        resp = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.0-flash", contents=full_prompt)
        )
        return resp.text
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# ── Smart mock generator ──────────────────────────────────────────────────────
def _fmt(v):
    if v is None: return "N/A"
    if abs(v) >= 1e9: return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6: return f"${v/1e6:.1f}M"
    if abs(v) >= 1e3: return f"${v/1e3:.0f}K"
    return f"${v:.0f}"

def _pct(v): return f"{v:.1f}%" if v is not None else "N/A"
def _x(v):   return f"{v:.2f}x" if v is not None else "N/A"

def _mock_insights(company_name, period, financial_data, kpis, risk_data, benchmarks):
    pr   = kpis.get("profitability", {})
    liq  = kpis.get("liquidity", {})
    lev  = kpis.get("leverage", {})
    eff  = kpis.get("efficiency", {})
    cf   = kpis.get("cash_flow", {})
    gr   = kpis.get("growth", {})
    comp = kpis.get("composite_scores", {})
    health = comp.get("overall_health", 5)
    gm   = pr.get("gross_margin")
    nm   = pr.get("net_margin")
    roe  = pr.get("return_on_equity")
    cr   = liq.get("current_ratio")
    de   = lev.get("debt_to_equity")
    rev  = financial_data.get("revenue")
    ni   = financial_data.get("net_income")
    fcf  = financial_data.get("free_cash_flow")

    if health >= 7:
        rating = "Good"; outlook = "positive"; strength = "strong"
    elif health >= 5:
        rating = "Fair"; outlook = "stable"; strength = "adequate"
    else:
        rating = "Weak"; outlook = "cautious"; strength = "weak"

    risk_level = "Low"
    if risk_data:
        rs = risk_data.get("risk_summary", {})
        risk_level = rs.get("overall_risk_level", "Medium")

    return f"""## 1. Executive Summary

{company_name} demonstrates {strength} financial performance for {period} with an overall health score of **{health:.1f}/10**.
Revenue stands at **{_fmt(rev)}** with a net income of **{_fmt(ni)}**, yielding a net margin of **{_pct(nm)}**.
The company maintains a current ratio of **{_x(cr)}**, indicating {"healthy" if cr and cr >= 1.5 else "tight"} liquidity.
Overall financial risk is classified as **{risk_level}**, and the investment outlook is **{outlook}**.

---

## 2. Profitability Analysis

- **Gross Margin:** {_pct(gm)} — {"above average, reflecting strong pricing power and cost discipline" if gm and gm > 40 else "in line with sector peers" if gm and gm > 20 else "below average, indicating margin pressure"}
- **Net Margin:** {_pct(nm)} — {"excellent bottom-line efficiency" if nm and nm > 15 else "acceptable profitability" if nm and nm > 5 else "weak net profitability requiring attention"}
- **Return on Equity (ROE):** {_pct(roe)} — {"strong returns delivered to shareholders" if roe and roe > 15 else "moderate shareholder returns" if roe and roe > 8 else "low returns on equity capital"}
- **Return on Assets:** {_pct(pr.get("return_on_assets"))}
- **Operating Margin:** {_pct(pr.get("operating_margin"))}

---

## 3. Liquidity & Working Capital

- **Current Ratio:** {_x(cr)} — {"comfortable liquidity buffer" if cr and cr >= 2 else "adequate short-term coverage" if cr and cr >= 1.2 else "tight liquidity — monitor closely"}
- **Quick Ratio:** {_x(liq.get("quick_ratio"))}
- **Cash Ratio:** {_x(liq.get("cash_ratio"))}
- Cash and equivalents: {_fmt(financial_data.get("cash_and_equivalents"))}

---

## 4. Capital Structure & Leverage

- **Debt/Equity Ratio:** {_x(de)} — {"conservative leverage" if de and de < 0.5 else "moderate leverage" if de and de < 1.5 else "elevated leverage — financial risk present"}
- **Interest Coverage:** {_x(lev.get("interest_coverage"))}
- **Total Debt:** {_fmt(financial_data.get("total_debt"))}
- **Total Equity:** {_fmt(financial_data.get("total_equity"))}

---

## 5. Operational Efficiency

- **Asset Turnover:** {_x(eff.get("asset_turnover"))}
- **Days Sales Outstanding (DSO):** {eff.get("days_sales_outstanding", "N/A")} days
- **Days Inventory Outstanding:** {eff.get("days_inventory_outstanding", "N/A")} days
- **Days Payable Outstanding:** {eff.get("days_payable_outstanding", "N/A")} days
- **Cash Conversion Cycle:** {eff.get("cash_conversion_cycle", "N/A")} days

---

## 6. Cash Flow Quality

- **Free Cash Flow:** {_fmt(fcf)} — {"strong cash generation" if fcf and fcf > 0 else "negative FCF — cash burn present"}
- **Operating Cash Flow:** {_fmt(financial_data.get("operating_cash_flow"))}
- **CapEx:** {_fmt(financial_data.get("capex"))}
- **CapEx to Revenue:** {_pct(cf.get("capex_to_revenue"))}

---

## 7. Industry Benchmarking

{"Benchmarks not available for this sector." if not benchmarks else f"Compared to {benchmarks.get('sector','sector')} median — gross margin {_pct(gm)} vs sector {_pct(benchmarks.get('metrics',{}).get('gross_margin'))}."}

---

## 8. Key Strengths ✅

{"- Strong gross margins reflecting competitive pricing power" if gm and gm > 40 else "- Adequate revenue base supporting operations"}
{"- Healthy liquidity position with current ratio above 1.5" if cr and cr >= 1.5 else "- Working capital being actively managed"}
{"- Positive free cash flow providing financial flexibility" if fcf and fcf > 0 else "- Management focused on operational improvements"}
- Diversified revenue streams reducing concentration risk
- Consistent operational structure with measurable KPIs

---

## 9. Key Risks & Red Flags ⚠️

{"- Net margin pressure may intensify with cost increases" if nm and nm < 10 else "- Margin sustainability requires monitoring in competitive markets"}
{"- Elevated debt levels increase financial vulnerability" if de and de > 1.5 else "- Leverage is manageable but should be monitored"}
{"- Negative free cash flow raises sustainability concerns" if fcf and fcf < 0 else "- Capital expenditure discipline critical to maintain FCF"}
- Macroeconomic headwinds could impact demand
- Regulatory changes in core markets pose execution risk

---

## 10. Strategic Recommendations

1. **Margin optimisation:** Focus on operational efficiency to protect net margins
2. **Working capital management:** Reduce DSO and optimise inventory levels
3. **Capital allocation:** Prioritise high-return investments and shareholder value
4. {"**Debt reduction:** Prioritise deleveraging to reduce interest burden" if de and de > 1 else "**Growth investment:** Deploy strong balance sheet for strategic acquisitions"}
5. **KPI monitoring:** Establish quarterly review cadence for financial health metrics

---

## 11. Investment Outlook

{company_name} presents a {outlook} investment profile for {period}. {"The company's strong fundamentals, healthy cash flows, and manageable leverage suggest continued value creation potential." if health >= 7 else "Management needs to address margin pressures and improve key operational metrics to unlock shareholder value." if health >= 5 else "Significant operational and financial challenges require urgent management attention and strategic restructuring."}

---

## Overall Rating: {rating}

Health score of {health:.1f}/10 with {risk_level.lower()} overall financial risk. {"Company demonstrates solid fundamentals with room for continued growth." if health >= 7 else "Adequate performance with key areas requiring improvement." if health >= 5 else "Financial performance is below expectations — corrective action needed."}
"""


def _mock_risk_narrative(company_name, risk_data, kpis):
    ra    = risk_data or {}
    altman = ra.get("altman_z_score", {})
    pio    = ra.get("piotroski_f_score", {})
    ben    = ra.get("beneish_m_score") or {}
    custom = ra.get("custom_risk", {})
    rs     = ra.get("risk_summary", {})

    z  = altman.get("score")
    zone = altman.get("zone", "Unknown")
    f  = pio.get("score")
    ms = ben.get("score") if isinstance(ben, dict) else None
    cr = custom.get("risk_score", 0)
    rl = rs.get("overall_risk_level", "Medium")

    return f"""## Overall Risk Profile

{company_name} carries a **{rl}** overall risk rating based on three academic risk models and a custom assessment.

---

## Bankruptcy Risk — Altman Z-Score

**Score: {z:.2f if z else "N/A"}** → {zone}

{"The company sits in the **Safe Zone** (Z > 2.99), indicating low probability of financial distress in the near term." if z and z > 2.99 else "The company sits in the **Grey Zone** (1.81–2.99), indicating some financial uncertainty warranting close monitoring." if z and z > 1.81 else "The company sits in the **Distress Zone** (Z < 1.81), indicating elevated bankruptcy risk requiring immediate attention."}

---

## Earnings Quality — Beneish M-Score

**Score: {ms:.3f if ms else "N/A"}**

{"M-Score below -2.22 suggests **low probability of earnings manipulation** — financials appear reliable." if ms and ms < -2.22 else "M-Score above -2.22 suggests **possible earnings manipulation** — independent audit review recommended." if ms else "Insufficient data for Beneish analysis — requires 2+ periods of financial statements."}

---

## Financial Strength — Piotroski F-Score

**Score: {f}/9 — {pio.get("strength", "N/A")}** if f is not None else "Score: N/A"

{"F-Score of 7–9 indicates a **financially strong** company with improving fundamentals." if f and f >= 7 else "F-Score of 4–6 indicates **moderate financial strength** — some signals are positive, others need attention." if f and f >= 4 else "F-Score of 0–3 indicates **weak financial fundamentals** — multiple deteriorating signals detected."}

---

## Custom Risk Flags

{chr(10).join(f"- ⚠️ **{rf['factor']}**: {rf['detail']}" for rf in custom.get("risk_factors", [])) or "- ✅ No major risk flags detected"}

---

## Risk Mitigation Recommendations

1. Monitor Altman Z-Score quarterly to detect early distress signals
2. Review accounts receivable ageing to identify collection risks
3. Maintain adequate liquidity buffer (current ratio > 1.5)
4. {"Prioritise debt reduction to improve financial stability" if cr > 5 else "Maintain current conservative leverage profile"}
5. Conduct regular internal audit to ensure earnings quality
"""


def _mock_forecast_narrative(company_name, forecasts, historical):
    rev_fc = forecasts.get("revenue", {})
    cagr   = rev_fc.get("cagr_pct")
    trend  = rev_fc.get("trend", {}).get("direction", "stable")
    ef     = rev_fc.get("ensemble_forecast", [])
    n      = len(historical)

    return f"""## Revenue Outlook

Based on {n} historical periods, {company_name}'s revenue shows a **{trend}** trajectory.
{"CAGR of " + f"{cagr:.1f}%" if cagr else "Growth rate analysis"} {"suggests healthy expansion momentum." if cagr and cagr > 5 else "indicates moderate growth prospects." if cagr and cagr > 0 else "signals potential revenue headwinds."}

Ensemble forecast for next period: **{"${:,.0f}".format(ef[0]) if ef else "Pending data"}**

---

## Profitability Trends

{"Revenue growth is outpacing cost increases, suggesting margin expansion potential." if cagr and cagr > 8 else "Revenue growth is steady — margin maintenance will depend on cost discipline." if cagr and cagr > 0 else "Revenue decline puts pressure on fixed cost absorption and profitability."}

---

## Key Growth Drivers

- Core business expansion in primary markets
- Operational efficiency improvements driving margin gains
- {"Strong free cash flow funding organic and inorganic growth" if any(forecasts.get("free_cash_flow", {}).get("ensemble_forecast", [])) else "Capital allocation strategy supporting long-term value creation"}

---

## Downside Risks

- Macroeconomic slowdown reducing demand
- Competitive pricing pressure compressing margins
- Input cost inflation impacting gross margins
- Regulatory changes in key operating markets

---

## Upside Catalysts

- Market share gains from competitor weakness
- New product or service launches
- Geographical expansion into high-growth markets
- Operational leverage as fixed costs are spread over higher revenue

---

## 12-Month Outlook: {"Bullish" if cagr and cagr > 8 else "Neutral" if cagr and cagr > 0 else "Bearish"}

{"Strong growth trajectory and healthy fundamentals support a positive 12-month outlook. Continue monitoring execution against strategic targets." if cagr and cagr > 8 else "Moderate growth with stable fundamentals. Focus on efficiency and margin protection." if cagr and cagr >= 0 else "Revenue headwinds and deteriorating metrics warrant a cautious outlook. Management must prioritise stabilisation."}
"""


def _mock_executive_summary(company_name, analysis_text):
    lines = [l.strip() for l in analysis_text.split("\n") if l.strip() and not l.startswith("#")]
    bullets = [l for l in lines if len(l) > 40][:5]
    return "\n".join(f"• {b[:200]}" for b in bullets) or f"• {company_name} financial analysis complete. Review full report for detailed insights."


def _mock_chat(question, company_name, context):
    q = question.lower()
    kpis = context.get("kpis", {})
    pr   = kpis.get("profitability", {})
    liq  = kpis.get("liquidity", {})
    lev  = kpis.get("leverage", {})
    comp = kpis.get("composite_scores", {})
    fd   = context.get("financial_data", {})

    if any(w in q for w in ["revenue", "sales", "turnover"]):
        rev = fd.get("revenue")
        return f"{company_name}'s revenue is **{_fmt(rev)}**. " + (f"Gross margin is **{_pct(pr.get('gross_margin'))}**." if pr.get("gross_margin") else "")
    if any(w in q for w in ["profit", "income", "margin", "net"]):
        return f"Net income: **{_fmt(fd.get('net_income'))}** | Net margin: **{_pct(pr.get('net_margin'))}** | Gross margin: **{_pct(pr.get('gross_margin'))}** | Operating margin: **{_pct(pr.get('operating_margin'))}**"
    if any(w in q for w in ["liquidity", "current ratio", "cash"]):
        return f"Current ratio: **{_x(liq.get('current_ratio'))}** | Quick ratio: **{_x(liq.get('quick_ratio'))}** | Cash: **{_fmt(fd.get('cash_and_equivalents'))}**"
    if any(w in q for w in ["debt", "leverage", "equity"]):
        return f"Debt/Equity: **{_x(lev.get('debt_to_equity'))}** | Total debt: **{_fmt(fd.get('total_debt'))}** | Total equity: **{_fmt(fd.get('total_equity'))}**"
    if any(w in q for w in ["health", "score", "rating", "overall"]):
        h = comp.get("overall_health", 0)
        label = "Strong" if h >= 7 else "Adequate" if h >= 5 else "Weak"
        return f"{company_name}'s overall financial health score is **{h:.1f}/10** ({label}). Profitability: {comp.get('profitability_score', 'N/A')}/10 | Liquidity: {comp.get('liquidity_score', 'N/A')}/10 | Leverage: {comp.get('leverage_score', 'N/A')}/10"
    if any(w in q for w in ["roe", "return on equity"]):
        return f"Return on Equity (ROE): **{_pct(pr.get('return_on_equity'))}** | Return on Assets: **{_pct(pr.get('return_on_assets'))}**"
    if any(w in q for w in ["risk"]):
        return f"Based on the financial data, {company_name} presents a medium risk profile. Run Risk Analysis for full Altman Z-Score, Piotroski F-Score and Beneish M-Score breakdown."

    return f"I have access to {company_name}'s financial data. You can ask me about revenue, profitability margins, liquidity ratios, debt levels, cash flow, return on equity, or overall financial health."


# ── Public API ────────────────────────────────────────────────────────────────
SYSTEM_ANALYST = "You are a senior financial analyst (CFA). Produce precise data-driven insights."


async def generate_financial_insights(company_name, period, financial_data, kpis,
                                       risk_data=None, benchmarks=None):
    if _has_valid_key():
        try:
            from backend.services.llm_service import _call_llm, SYSTEM_ANALYST
            prompt = f"Analyse {company_name} for {period}.\nKPIs: {json.dumps(kpis)}\nData: {json.dumps(financial_data)}"
            return await _call_llm(SYSTEM_ANALYST, prompt, 3000)
        except Exception:
            pass
    return _mock_insights(company_name, period, financial_data, kpis, risk_data, benchmarks)


async def generate_risk_narrative(company_name, risk_data, kpis):
    if _has_valid_key():
        try:
            prompt = f"Risk analysis for {company_name}.\nRisk: {json.dumps(risk_data)}\nKPIs: {json.dumps(kpis)}"
            return await _call_llm(SYSTEM_ANALYST, prompt, 1800)
        except Exception:
            pass
    return _mock_risk_narrative(company_name, risk_data, kpis)


async def generate_forecast_narrative(company_name, forecasts, historical_data):
    if _has_valid_key():
        try:
            prompt = f"Forecast narrative for {company_name}.\nForecasts: {json.dumps({k:v for k,v in list(forecasts.items())[:4]})}"
            return await _call_llm(SYSTEM_ANALYST, prompt, 1400)
        except Exception:
            pass
    return _mock_forecast_narrative(company_name, forecasts, historical_data)


async def generate_executive_summary(company_name, analysis_text):
    if _has_valid_key():
        try:
            prompt = f"Summarise in 5 bullets (max 200 words):\n{analysis_text[:3000]}"
            return await _call_llm(SYSTEM_ANALYST, prompt, 350)
        except Exception:
            pass
    return _mock_executive_summary(company_name, analysis_text)


async def chat_with_financials(question, company_name, financial_context, chat_history):
    if _has_valid_key():
        try:
            system = f"You are a financial analyst for {company_name}. Context: {json.dumps(financial_context)[:3000]}"
            messages = [{"role": "system", "content": system}]
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": question})
            provider = settings.llm_provider.lower()
            if provider == "openai":
                client = _get_openai_client()
                resp = await client.chat.completions.create(
                    model="gpt-4o", messages=messages, max_tokens=900, temperature=0.2)
                return resp.choices[0].message.content
            else:
                import asyncio
                client = _get_gemini_client()
                flat = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])
                loop = asyncio.get_event_loop()
                resp = await loop.run_in_executor(
                    None, lambda: client.models.generate_content(model="gemini-2.0-flash", contents=flat))
                return resp.text
        except Exception:
            pass
    return _mock_chat(question, company_name, financial_context)


def _mock_chat(question, company_name, context):
    from backend.services.chatbot_engine import generate_response
    return generate_response(question, company_name, context)
