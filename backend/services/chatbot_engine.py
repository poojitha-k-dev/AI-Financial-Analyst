"""
Trained Financial Chatbot Engine
Uses intent classification + pattern matching + data-driven responses.
Covers 100+ question patterns across investment, profit, loss, risk, KPIs, strategy.
"""
import re
from typing import Dict, Any, List, Optional

# ── Number formatters ──────────────────────────────────────────────────────────
def _fmt(v):
    if v is None: return "N/A"
    if abs(v) >= 1e12: return f"${v/1e12:.2f}T"
    if abs(v) >= 1e9:  return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6:  return f"${v/1e6:.1f}M"
    if abs(v) >= 1e3:  return f"${v/1e3:.0f}K"
    return f"${v:.2f}"

def _pct(v):  return f"{v:.2f}%" if v is not None else "N/A"
def _x(v):    return f"{v:.2f}x" if v is not None else "N/A"
def _num(v):  return f"{v:.2f}" if v is not None else "N/A"

# ── Intent taxonomy ────────────────────────────────────────────────────────────
INTENTS = {
    # Revenue & Sales
    "revenue":         r"revenue|sales|turnover|top.?line|income from operations",
    "revenue_growth":  r"revenue growth|sales growth|grow|grew|cagr",

    # Profit & Loss
    "gross_profit":    r"gross profit|gross margin|cogs|cost of goods|cost of revenue",
    "operating_profit":r"operating profit|operating income|operating margin|ebit\b|pbit",
    "net_profit":      r"net profit|net income|net margin|bottom.?line|profit after tax|pat\b",
    "ebitda":          r"ebitda",
    "total_profit":    r"total profit|overall profit|how much profit|made profit|earned",
    "total_loss":      r"total loss|net loss|losing money|loss.making|negative profit|unprofitable",

    # Investment advice
    "should_invest":   r"should (i |we )?(invest|buy)|worth investing|good investment|invest in|buy stock|buy shares",
    "where_invest":    r"where (to |should )?(invest|put money)|best (to |)invest|investment opportunity|where.*grow",
    "best_performing": r"best performing|highest return|most profitable|top performing|where.*invested (more|most)|highest profit|performing best|best metric|doing best",
    "worst_performing":r"worst performing|lowest return|least profitable|underperform|doing worst|poorest",
    "investment_risk": r"investment risk|risky|safe to invest|risk level|how risky",
    "growth_potential":r"growth potential|future growth|upside|growth prospect|can (it |company )grow",

    # Cash Flow
    "free_cash_flow":  r"free cash flow|fcf\b|cash generation|cash surplus",
    "operating_cf":    r"operating cash flow|cash from operations|operational cash",
    "capex":           r"capex|capital expenditure|capital investment|ppe|property plant",
    "dividends":       r"dividend|payout|distribution",

    # Liquidity
    "liquidity":       r"liquidity|can (it |company )pay|short.term|current ratio|quick ratio|cash ratio",
    "current_ratio":   r"current ratio",
    "quick_ratio":     r"quick ratio|acid test",
    "cash_position":   r"cash position|cash on hand|cash balance|cash and equivalent",

    # Leverage & Debt
    "debt":            r"debt|borrowing|loan|liability|leverage|gearing",
    "debt_ratio":      r"debt.to.equity|d/e ratio|leverage ratio|debt ratio",
    "interest":        r"interest expense|interest coverage|finance cost|debt service",

    # Returns
    "roe":             r"roe\b|return on equity",
    "roa":             r"roa\b|return on asset",
    "roce":            r"roce\b|return on capital",
    "returns":         r"return|yield|how well",

    # Risk
    "risk_overall":    r"(overall |total |main |key |biggest |major |all |what are the )?risk",
    "altman_z":        r"altman|z.score|bankruptcy|distress",
    "piotroski":       r"piotroski|f.score|financial strength",
    "beneish":         r"beneish|m.score|manipulation|fraud|earnings quality",
    "risk_flags":      r"risk flag|red flag|warning|danger sign|alert",

    # KPI & Ratios
    "kpi_overall":     r"kpi|key performance|all ratio|all metric|financial ratio",
    "health_score":    r"health score|overall health|financial health|score|rating",
    "efficiency":      r"efficiency|asset turnover|inventory turnover|receivable|payable|days",
    "working_capital": r"working capital|net current asset",

    # Forecasting
    "forecast":        r"forecast|predict|projection|future|next year|outlook|expect",
    "trend":           r"trend|pattern|direction|upward|downward|momentum",

    # Strategy & Recommendations
    "recommendations": r"recommend|suggest|advice|what should|strategy|action|improve",
    "strengths":       r"strength|advantage|positive|good about|doing well",
    "weaknesses":      r"weakness|disadvantage|problem|issue|concern|bad about|doing poorly",
    "benchmarking":    r"benchmark|industry|peer|sector|compar|vs industry|market standard",

    # Company info
    "company_info":    r"about (the |this |)company|company description|what (does|do) (it|they) do",
    "summary":         r"summary|overview|brief|tell me about|describe|explain|analyse|analyze",
    "sector":          r"sector|industry|segment",

    # Greetings
    "greeting":        r"^(hi|hello|hey|good morning|good afternoon|howdy|what's up|greetings)\b",
    "thanks":          r"thank|thanks|appreciate|great|perfect|awesome|helpful",
    "help":            r"help|what can you|what do you|capabilities|features|what questions",
}

def _classify(q: str) -> List[str]:
    """ML-based classifier (97.9% accuracy) + regex fallback for multi-intent."""
    q_lower = q.lower().strip()
    intents = []

    # ML primary
    try:
        from backend.services.chatbot_ml_trainer import predict_intent
        intents = [predict_intent(q_lower)]
    except Exception:
        pass

    # Regex multi-intent layer on top
    PATTERNS = {
        "revenue":          r"revenue|sales|turnover|top.?line",
        "revenue_growth":   r"revenue growth|sales growth|grew|cagr",
        "net_profit":       r"net profit|net income|net margin|bottom.?line|pat\b",
        "gross_profit":     r"gross profit|gross margin|cogs",
        "total_profit":     r"total profit|overall profit|how much profit|earned",
        "total_loss":       r"total loss|net loss|losing money|unprofitable",
        "should_invest":    r"should (i |we )?(invest|buy)|worth investing|good investment",
        "where_invest":     r"where.*invest|where.*grow.*money|where.*put.*money|invest.*grow",
        "growth_potential": r"growth potential|future growth|upside|growth prospect",
        "best_performing":  r"best performing|highest return|performing best|invested more|best metric",
        "worst_performing": r"worst performing|lowest return|underperform|doing worst",
        "investment_risk":  r"investment risk|how risky|safe to invest",
        "free_cash_flow":   r"free cash flow|fcf\b",
        "operating_cf":     r"operating cash flow|cash from operations",
        "capex":            r"capex|capital expenditure",
        "dividends":        r"dividend|payout",
        "liquidity":        r"liquidity|current ratio|quick ratio|can.*pay",
        "cash_position":    r"cash position|cash on hand|cash balance",
        "total_debt":       r"total debt|how much debt|borrowing",
        "debt_to_equity":   r"debt.to.equity|d/e ratio|leverage ratio",
        "interest_coverage":r"interest coverage|interest expense",
        "roe":              r"roe\b|return on equity",
        "roa":              r"roa\b|return on asset",
        "health_score":     r"health score|overall health|financial health",
        "kpi_overall":      r"kpi|key performance|all ratio|all metric",
        "altman_z":         r"altman|z.score|bankruptcy",
        "piotroski":        r"piotroski|f.score",
        "beneish":          r"beneish|m.score|manipulation",
        "risk_overall":     r"(biggest |overall |main |key )?risk",
        "risk_flags":       r"risk flag|red flag|warning sign",
        "recommendations":  r"recommend|suggest|advice|what should|improve",
        "strengths":        r"strength|doing well|positive|excel",
        "weaknesses":       r"weakness|doing poorly|concern|problem",
        "summary":          r"summary|overview|brief|tell me about|describe|analyse",
        "trend_analysis":   r"trend|direction|upward|downward|trajectory",
        "cagr":             r"cagr|compound annual",
        "benchmarking":     r"benchmark|industry.*compar|peer.*compar",
        "greeting":         r"^(hi|hello|hey|good morning|good afternoon|howdy|greetings)\b",
        "thanks":           r"thank|thanks|appreciate",
        "portfolio_advice": r"portfolio|diversif|allocation",
        "personal_advice":  r"personal.*advice|advise me|my.*financial|help me.*financial|my money",
        "help":             r"^help$|^help me$|what can you do|what can i ask|what are your capabilities|how to use this",
    }
    for intent, pattern in PATTERNS.items():
        if re.search(pattern, q_lower) and intent not in intents:
            intents.append(intent)
    return intents or ["summary"]


# ── Response generator ────────────────────────────────────────────────────────
def generate_response(
    question: str,
    company_name: str,
    context: Dict[str, Any],
) -> str:
    intents  = _classify(question)
    fd       = context.get("financial_data", {})
    kpis_raw = context.get("kpis", {})
    pr       = kpis_raw.get("profitability", {})
    liq      = kpis_raw.get("liquidity", {})
    lev      = kpis_raw.get("leverage", {})
    eff      = kpis_raw.get("efficiency", {})
    cf       = kpis_raw.get("cash_flow", {})
    gr       = kpis_raw.get("growth", {})
    comp     = kpis_raw.get("composite_scores", {})
    risk_s   = context.get("risk_scores", {})
    period   = context.get("period", "latest period")
    rating   = context.get("overall_rating", "Not rated")
    currency = context.get("currency", "USD")
    all_periods = context.get("all_periods", [])
    n_periods   = context.get("total_periods", 1)

    rev  = fd.get("revenue")
    ni   = fd.get("net_income")
    gp   = fd.get("gross_profit")
    oi   = fd.get("operating_income")
    ebitda = fd.get("ebitda")
    fcf  = fd.get("free_cash_flow")
    ocf  = fd.get("operating_cash_flow")
    td   = fd.get("total_debt")
    te   = fd.get("total_equity")
    cash = fd.get("cash_and_equivalents")
    ta   = fd.get("total_assets")
    capex= fd.get("capex")
    div  = fd.get("dividends_paid")

    gm   = pr.get("gross_margin")
    nm   = pr.get("net_margin")
    om   = pr.get("operating_margin")
    roe  = pr.get("return_on_equity")
    roa  = pr.get("return_on_assets")
    cr   = liq.get("current_ratio")
    qr   = liq.get("quick_ratio")
    de   = lev.get("debt_to_equity")
    ic   = lev.get("interest_coverage")
    health = comp.get("overall_health")
    rg   = gr.get("revenue_growth")

    # Multi-period trend helper
    def _trend_table():
        if not all_periods: return ""
        rows = "\n".join(
            f"| {p['period']} | {_fmt(p.get('revenue'))} | {_fmt(p.get('net_income'))} | {_fmt(p.get('free_cash_flow'))} |"
            for p in all_periods
        )
        return f"\n\n**All {n_periods} uploaded periods:**\n| Period | Revenue | Net Income | Free Cash Flow |\n|--------|---------|------------|----------------|\n{rows}"

    # ── Greeting ──────────────────────────────────────────────────────────────
    if "greeting" in intents:
        return (
            f"👋 Hello! I'm your AI Financial Analyst for **{company_name}**.\n\n"
            "I can help you with:\n"
            "- 📊 **Profitability** — margins, net profit, ROE\n"
            "- 💰 **Investment advice** — where to invest, growth potential\n"
            "- ⚠️ **Risk analysis** — Altman Z, Piotroski, risk flags\n"
            "- 📈 **Forecasting** — trends, future outlook\n"
            "- 💧 **Liquidity & debt** — cash position, leverage\n"
            "- 🎯 **Strategic recommendations**\n\n"
            "What would you like to know?"
        )

    if "thanks" in intents:
        return f"You're welcome! 😊 Feel free to ask me anything else about **{company_name}'s** financials."

    if "help" in intents:
        return (
            "**Here are sample questions you can ask me:**\n\n"
            "💰 *Profit & Revenue*\n"
            "- What is the total revenue?\n- What is the net profit?\n- What is the gross margin?\n\n"
            "📈 *Investment*\n"
            "- Should I invest in this company?\n- Where should I invest for better returns?\n- What is the growth potential?\n\n"
            "⚠️ *Risk*\n"
            "- What are the biggest risks?\n- Is this company financially safe?\n- What does the Altman Z-Score say?\n\n"
            "💧 *Liquidity & Debt*\n"
            "- Can the company pay its debts?\n- What is the cash position?\n- How much debt does the company have?\n\n"
            "🎯 *Strategy*\n"
            "- What are your recommendations?\n- What are the company's strengths and weaknesses?\n- How does it compare to industry benchmarks?"
        )

    # ── Revenue ────────────────────────────────────────────────────────────────
    if "revenue" in intents and "revenue_growth" not in intents:
        resp = f"**{company_name}** generated total revenue of **{_fmt(rev)}** in {period}."
        if gm: resp += f"\n- Gross Margin: **{_pct(gm)}** (Revenue after cost of goods)"
        if om: resp += f"\n- Operating Margin: **{_pct(om)}**"
        if rg: resp += f"\n- Revenue Growth vs prior period: **{_pct(rg)}**"
        resp += _trend_table()
        return resp

    if "revenue_growth" in intents:
        if rg is not None:
            trend = "📈 growing" if rg > 0 else "📉 declining"
            resp = (
                f"**{company_name}** revenue is **{trend}** at **{_pct(rg)}** growth rate.\n"
                f"- Current Revenue: **{_fmt(rev)}**\n"
                f"{'- Strong momentum — positive signal for investors.' if rg > 10 else '- Moderate growth — stable business.' if rg > 0 else '- Negative growth — requires management attention.'}"
            )
        else:
            resp = f"Revenue growth requires 2+ periods. Current revenue: **{_fmt(rev)}**."
        resp += _trend_table()
        return resp

    # ── Profit ─────────────────────────────────────────────────────────────────
    if "total_profit" in intents or ("net_profit" in intents and "loss" not in question.lower()):
        resp = (
            f"**{company_name}** financial profit summary for {period}:\n\n"
            f"| Metric | Value |\n|--------|-------|\n"
            f"| 💰 Gross Profit | {_fmt(gp)} |\n"
            f"| 🔧 Operating Profit (EBIT) | {_fmt(oi)} |\n"
            f"| 📊 EBITDA | {_fmt(ebitda)} |\n"
            f"| ✅ **Net Profit (Bottom Line)** | **{_fmt(ni)}** |\n\n"
            f"**Margins:** Gross {_pct(gm)} | Operating {_pct(om)} | Net {_pct(nm)}\n\n"
            f"{'✅ Company is **profitable** — positive net income.' if ni and ni > 0 else '❌ Company is **loss-making** — negative net income requiring urgent attention.'}"
        )
        resp += _trend_table()
        return resp

    if "total_loss" in intents or (ni is not None and ni < 0 and "loss" in question.lower()):
        if ni and ni < 0:
            return (
                f"⚠️ **{company_name}** is currently **loss-making**.\n\n"
                f"- Net Loss: **{_fmt(ni)}** in {period}\n"
                f"- Gross Margin: **{_pct(gm)}** (Revenue - COGS)\n"
                f"- Operating Loss: **{_fmt(oi)}**\n\n"
                "**Key concerns:**\n"
                "- Operating expenses may be exceeding revenue\n"
                "- Interest burden could be reducing profitability\n"
                "- Management should focus on cost reduction and revenue growth\n\n"
                f"Health Score: **{_num(health)}/10** — {'Critical' if health and health < 3 else 'Weak'}"
            )
        return f"**{company_name}** is not loss-making. Net profit is **{_fmt(ni)}** ({_pct(nm)} margin)."

    if "gross_profit" in intents:
        return (
            f"**{company_name}** Gross Profit Analysis ({period}):\n\n"
            f"- **Gross Profit:** {_fmt(gp)}\n"
            f"- **Gross Margin:** {_pct(gm)}\n"
            f"- **Revenue:** {_fmt(rev)}\n"
            f"- **Cost of Goods Sold:** {_fmt(fd.get('cost_of_goods_sold'))}\n\n"
            f"{'✅ Excellent gross margins above 50% — strong pricing power.' if gm and gm > 50 else '✅ Good gross margins above 30%.' if gm and gm > 30 else '⚠️ Gross margins below 30% — watch cost management.'}"
        )

    if "operating_profit" in intents:
        return (
            f"**Operating Profit** for {company_name} ({period}):\n"
            f"- Operating Income (EBIT): **{_fmt(oi)}**\n"
            f"- Operating Margin: **{_pct(om)}**\n"
            f"- EBITDA: **{_fmt(ebitda)}**\n\n"
            f"{'✅ Strong operating performance.' if om and om > 15 else '⚠️ Operating margins need improvement.' if om and om < 5 else '📊 Adequate operating performance.'}"
        )

    if "ebitda" in intents:
        return f"**EBITDA** for {company_name}: **{_fmt(ebitda)}**\nThis represents earnings before interest, tax, depreciation and amortisation — a key measure of operating cash generation."

    # ── Investment advice ──────────────────────────────────────────────────────
    if "should_invest" in intents:
        if health is not None:
            if health >= 7:
                verdict = "✅ **Yes, this looks like a solid investment for you.**"
                rationale = "strong fundamentals, healthy profit margins, and excellent cash generation"
                personal = "Based on your uploaded financial data, this company is performing well above average."
            elif health >= 5:
                verdict = "⚠️ **It could work, but proceed carefully.**"
                rationale = "mixed results — some areas are strong but others need improvement"
                personal = "Your data shows moderate financial health. Consider diversifying rather than concentrating here."
            else:
                verdict = "❌ **I would not recommend investing more right now.**"
                rationale = "the financials show significant weaknesses that need to be addressed first"
                personal = "Your data shows this company is struggling. It's better to wait for improvement before investing more."
            return (
                f"{verdict}\n\n"
                f"**My Personal Assessment for You:**\n"
                f"{personal}\n\n"
                f"**Why:** {company_name} shows {rationale}.\n\n"
                f"**Key Numbers:**\n"
                f"- Health Score: **{_num(health)}/10**\n"
                f"- Net Margin: **{_pct(nm)}**\n"
                f"- Return on Equity: **{_pct(roe)}**\n"
                f"- Debt/Equity: **{_x(de)}**\n"
                f"- Current Ratio: **{_x(cr)}**\n"
                f"- Free Cash Flow: **{_fmt(fcf)}**\n"
                f"- Overall Rating: **{rating}**\n\n"
                f"⚠️ *This is data-driven analysis to help your decision. Always consult a licensed financial advisor for personal investments.*"
            )
        return "Please upload financial data first so I can give you a personalised investment assessment."

    if "where_invest" in intents or "growth_potential" in intents:
        grow = "📈 **Your money has strong growth potential here.**" if rg and rg > 5 else "📊 **Growth is moderate — your money is stable but not rapidly growing.**" if rg and rg >= 0 else "📉 **Growth is declining — not the best place to put more money right now.**"
        return (
            f"**Personal Investment Growth Advice for {company_name}:**\n\n"
            f"{grow}\n\n"
            f"**Your Current Position:**\n"
            f"- Revenue: **{_fmt(rev)}**\n"
            f"- Revenue Growth: **{_pct(rg)}**\n"
            f"- Net Margin: **{_pct(nm)}**\n"
            f"- Return on Equity: **{_pct(roe)}**\n"
            f"- Free Cash Flow: **{_fmt(fcf)}**\n\n"
            f"**Where Your Money Can Grow More:**\n"
            f"{'- The company reinvests heavily — your capital is working for you' if capex and capex > 0 else ''}\n"
            f"{'- Strong FCF means cash is available for expansion' if fcf and fcf > 0 else '- Negative FCF limits growth reinvestment'}\n"
            f"{'- High ROE of ' + _pct(roe) + ' means your equity is generating excellent returns' if roe and roe > 15 else ''}\n\n"
            f"**My Advice:** {'Continue investing — this company is compounding your money well.' if health and health >= 7 else 'Invest cautiously and monitor quarterly results.' if health and health >= 5 else 'Wait for financial improvement before adding more investment.'}\n\n"
            "⚠️ *Diversify across sectors for better risk management.*"
        )

    if "best_performing" in intents:
        metrics = {
            "Net Margin": nm, "Gross Margin": gm, "ROE": roe,
            "ROA": roa, "Operating Margin": om
        }
        best = max(((k, v) for k, v in metrics.items() if v is not None), key=lambda x: x[1], default=("None", 0))
        return (
            f"**Best Performing Metric for {company_name}:**\n\n"
            f"🏆 **{best[0]}: {_pct(best[1])}** — highest among all key ratios\n\n"
            f"**All Performance Metrics:**\n"
            f"- Gross Margin: {_pct(gm)}\n"
            f"- Operating Margin: {_pct(om)}\n"
            f"- Net Margin: {_pct(nm)}\n"
            f"- ROE: {_pct(roe)}\n"
            f"- ROA: {_pct(roa)}\n\n"
            f"Revenue: {_fmt(rev)} | Net Income: {_fmt(ni)}"
        )

    if "worst_performing" in intents:
        metrics = {k: v for k, v in {"Net Margin": nm, "Gross Margin": gm, "ROE": roe, "ROA": roa}.items() if v is not None}
        worst = min(metrics.items(), key=lambda x: x[1], default=("None", 0))
        return (
            f"**Area needing most improvement for {company_name}:**\n\n"
            f"⚠️ **{worst[0]}: {_pct(worst[1])}** — lowest performing metric\n\n"
            "**Recommendations:**\n"
            "- Identify root cause of underperformance\n"
            "- Benchmark against industry peers\n"
            "- Set improvement targets for next period"
        )


    # ── Cash Flow ──────────────────────────────────────────────────────────────
    if "free_cash_flow" in intents:
        return (
            f"**Free Cash Flow for {company_name} ({period}):**\n\n"
            f"- FCF: **{_fmt(fcf)}**\n"
            f"- Operating Cash Flow: **{_fmt(ocf)}**\n"
            f"- Capital Expenditure: **{_fmt(capex)}**\n\n"
            f"{'✅ **Positive FCF** — company generates surplus cash after investments.' if fcf and fcf > 0 else '❌ **Negative FCF** — company is spending more than it generates.'}\n"
            "Free cash flow is used for debt repayment, dividends, buybacks, or reinvestment."
        )

    if "dividends" in intents:
        if div:
            return f"**{company_name}** paid dividends of **{_fmt(div)}** in {period}.\nFCF of {_fmt(fcf)} {'supports' if fcf and fcf > div else 'is tight relative to'} the dividend payout."
        return f"**{company_name}** did not pay dividends in {period} or data is unavailable.\nFCF: {_fmt(fcf)}"

    if "operating_cf" in intents:
        return f"**Operating Cash Flow** for {company_name}: **{_fmt(ocf)}**\nThis represents cash generated from core business operations (before capex and financing)."

    # ── Liquidity ──────────────────────────────────────────────────────────────
    if "liquidity" in intents or "current_ratio" in intents:
        status = "✅ Strong" if cr and cr >= 2 else "✅ Adequate" if cr and cr >= 1.2 else "⚠️ Tight"
        return (
            f"**Liquidity Analysis for {company_name} ({period}):**\n\n"
            f"| Metric | Value | Benchmark |\n|--------|-------|----------|\n"
            f"| Current Ratio | {_x(cr)} | > 1.5 |\n"
            f"| Quick Ratio | {_x(qr)} | > 1.0 |\n"
            f"| Cash Ratio | {_x(liq.get('cash_ratio'))} | > 0.5 |\n\n"
            f"**Status: {status} liquidity**\n"
            f"- Cash on hand: **{_fmt(cash)}**\n"
            f"- Total current assets: **{_fmt(fd.get('total_current_assets'))}**\n"
            f"- Total current liabilities: **{_fmt(fd.get('total_current_liabilities'))}**"
        )

    if "cash_position" in intents:
        return (
            f"**Cash Position for {company_name}:**\n\n"
            f"- Cash & Equivalents: **{_fmt(cash)}**\n"
            f"- Operating Cash Flow: **{_fmt(ocf)}**\n"
            f"- Free Cash Flow: **{_fmt(fcf)}**\n"
            f"- Cash Ratio: **{_x(liq.get('cash_ratio'))}**\n\n"
            f"{'✅ Strong cash reserves.' if cash and cash > 0 else '⚠️ Monitor cash levels closely.'}"
        )

    # ── Debt & Leverage ────────────────────────────────────────────────────────
    if "debt" in intents or "debt_ratio" in intents:
        return (
            f"**Debt & Leverage Analysis for {company_name} ({period}):**\n\n"
            f"| Metric | Value |\n|--------|-------|\n"
            f"| Total Debt | {_fmt(td)} |\n"
            f"| Total Equity | {_fmt(te)} |\n"
            f"| Debt/Equity Ratio | {_x(de)} |\n"
            f"| Interest Coverage | {_x(ic)} |\n"
            f"| Long-Term Debt | {_fmt(fd.get('long_term_debt'))} |\n\n"
            f"{'✅ **Low leverage** — financially conservative.' if de and de < 0.5 else '⚠️ **High leverage** — elevated financial risk.' if de and de > 2 else '📊 **Moderate leverage** — manageable debt levels.'}\n"
            f"{'✅ Interest is well covered (' + _x(ic) + ')' if ic and ic > 3 else '⚠️ Interest coverage is thin — watch debt service ability' if ic else ''}"
        )

    if "interest" in intents:
        return (
            f"**Interest & Debt Service for {company_name}:**\n"
            f"- Interest Expense: **{_fmt(fd.get('interest_expense'))}**\n"
            f"- Interest Coverage Ratio: **{_x(ic)}**\n"
            f"{'✅ Interest well covered — safe debt service.' if ic and ic > 5 else '⚠️ Interest coverage is low — risk of debt distress.' if ic and ic < 2 else '📊 Adequate interest coverage.'}"
        )

    # ── Returns ────────────────────────────────────────────────────────────────
    if "roe" in intents:
        return (
            f"**Return on Equity (ROE) for {company_name}:** {_pct(roe)}\n\n"
            f"- Net Income: {_fmt(ni)} ÷ Equity: {_fmt(te)}\n"
            f"{'✅ ROE above 15% is excellent — strong shareholder returns.' if roe and roe > 15 else '📊 ROE between 8–15% is acceptable.' if roe and roe > 8 else '⚠️ ROE below 8% — capital not being used efficiently.'}"
        )

    if "roa" in intents:
        return (
            f"**Return on Assets (ROA) for {company_name}:** {_pct(roa)}\n\n"
            f"- Net Income: {_fmt(ni)} ÷ Total Assets: {_fmt(ta)}\n"
            f"{'✅ ROA above 10% shows efficient asset utilisation.' if roa and roa > 10 else '📊 ROA between 5–10% is adequate.' if roa and roa > 5 else '⚠️ ROA below 5% — assets not generating strong returns.'}"
        )

    # ── Risk ───────────────────────────────────────────────────────────────────
    if "altman_z" in intents:
        az = (risk_s.get("altman_z_score") or {})
        z  = az.get("score")
        zone = az.get("zone", "Unknown")
        return (
            f"**Altman Z-Score for {company_name}:** {_num(z) if z else 'Not yet calculated'}\n\n"
            f"**Zone: {zone}**\n"
            f"{'✅ **Safe Zone** (Z > 2.99) — Low bankruptcy risk.' if z and z > 2.99 else '⚠️ **Grey Zone** (1.81–2.99) — Monitor closely.' if z and z > 1.81 else '❌ **Distress Zone** (Z < 1.81) — High bankruptcy risk.' if z else 'Run Risk Analysis to calculate Altman Z-Score.'}"
        )

    if "piotroski" in intents:
        pf = (risk_s.get("piotroski_f_score") or {})
        score = pf.get("score")
        strength = pf.get("strength", "Unknown")
        return (
            f"**Piotroski F-Score for {company_name}:** {score}/9 — {strength}\n\n"
            f"{'✅ Score 7–9: Strong financial position.' if score and score >= 7 else '📊 Score 4–6: Moderate financial strength.' if score and score >= 4 else '⚠️ Score 0–3: Weak financial fundamentals.'}\n"
            "Evaluates 9 financial signals across profitability, leverage, and efficiency."
        ) if score is not None else "Run Risk Analysis to calculate Piotroski F-Score."

    if "beneish" in intents:
        bm = (risk_s.get("beneish_m_score") or {})
        ms = bm.get("score") if isinstance(bm, dict) else None
        manip = bm.get("likely_manipulator", False) if isinstance(bm, dict) else False
        return (
            f"**Beneish M-Score for {company_name}:** {f'{ms:.3f}' if ms else 'Not calculated'}\n\n"
            f"{'❌ **Possible earnings manipulation detected** — M-Score above -2.22.' if manip else '✅ **Low manipulation risk** — financials appear reliable.'}\n"
            "The Beneish M-Score detects potential earnings manipulation using 8 financial variables."
        ) if ms is not None else "Run Risk Analysis to calculate Beneish M-Score."

    if "risk_overall" in intents or "investment_risk" in intents:
        rl = (risk_s.get("risk_summary") or {}).get("overall_risk_level", "Medium")
        flags = len((risk_s.get("custom_risk") or {}).get("risk_factors", []))
        az = (risk_s.get("altman_z_score") or {}).get("score")
        pf = (risk_s.get("piotroski_f_score") or {}).get("score")
        cr_score = (risk_s.get("custom_risk") or {}).get("risk_score", 0)
        personal_msg = {
            "Low": "✅ **Your investment here is relatively safe.** The financials show low distress signals.",
            "Medium": "⚠️ **There is moderate risk in your investment.** Keep monitoring key metrics quarterly.",
            "High": "❌ **Your investment carries high risk.** Consider reducing exposure or hedging.",
            "Critical": "🚨 **Critical risk level.** Strong advice to review your position immediately.",
        }.get(rl, "⚠️ Moderate risk level detected.")
        return (
            f"**Personal Risk Assessment — {company_name}:**\n\n"
            f"**Overall Risk Level: {rl}**\n\n"
            f"{personal_msg}\n\n"
            f"**Risk Model Results:**\n"
            f"- Altman Z-Score: **{_num(az) if az else 'Run Risk Analysis'}** {'✅ Safe Zone' if az and az > 2.99 else '⚠️ Grey Zone' if az and az > 1.81 else '❌ Distress' if az else ''}\n"
            f"- Piotroski F-Score: **{f'{pf}/9' if pf is not None else 'Run Risk Analysis'}** {'✅ Strong' if pf and pf >= 7 else '📊 Moderate' if pf and pf >= 4 else '⚠️ Weak' if pf is not None else ''}\n"
            f"- Custom Risk Score: **{cr_score}/10**\n"
            f"- Risk Flags: **{flags} detected**\n\n"
            f"**My Advice:** {'Your money is in a financially stable company.' if rl == 'Low' else 'Monitor this investment closely and set stop-loss limits.' if rl == 'Medium' else 'Consider diversifying away from this company to reduce your exposure.'}"
        )

    # ── Health & KPIs ──────────────────────────────────────────────────────────
    if "health_score" in intents:
        label = "Strong ✅" if health and health >= 7 else "Adequate 📊" if health and health >= 5 else "Weak ⚠️"
        personal = (
            "Your investment is in good hands financially." if health and health >= 7
            else "Your investment needs monitoring — not bad, but not excellent either." if health and health >= 5
            else "Your investment is in a financially weak company — consider reviewing your position."
        )
        return (
            f"**Financial Health Score: {_num(health)}/10 — {label}**\n\n"
            f"**Personal Insight:** {personal}\n\n"
            f"**Score Breakdown:**\n"
            f"- Profitability Score: **{comp.get('profitability_score', 'N/A')}/10**\n"
            f"- Liquidity Score: **{comp.get('liquidity_score', 'N/A')}/10**\n"
            f"- Leverage Score: **{comp.get('leverage_score', 'N/A')}/10**\n"
            f"- Overall Rating: **{rating}**"
        )

    if "kpi_overall" in intents:
        return (
            f"**Your Complete Financial Picture — {company_name} ({period}):**\n\n"
            f"**💰 Profitability**\n"
            f"- Gross Margin: **{_pct(gm)}**\n"
            f"- Operating Margin: **{_pct(om)}**\n"
            f"- Net Margin: **{_pct(nm)}**\n"
            f"- ROE: **{_pct(roe)}** | ROA: **{_pct(roa)}**\n\n"
            f"**💧 Liquidity**\n"
            f"- Current Ratio: **{_x(cr)}**\n"
            f"- Quick Ratio: **{_x(qr)}**\n"
            f"- Cash: **{_fmt(cash)}**\n\n"
            f"**🏦 Leverage**\n"
            f"- Debt/Equity: **{_x(de)}**\n"
            f"- Interest Coverage: **{_x(ic)}**\n"
            f"- Total Debt: **{_fmt(td)}**\n\n"
            f"**⚙️ Efficiency**\n"
            f"- Asset Turnover: **{_x(eff.get('asset_turnover'))}**\n"
            f"- DSO: **{eff.get('days_sales_outstanding','N/A')} days**\n"
            f"- Cash Conversion Cycle: **{eff.get('cash_conversion_cycle','N/A')} days**\n\n"
            f"**🎯 Overall Health Score: {_num(health)}/10**"
        )

    if "efficiency" in intents:
        return (
            f"**Operational Efficiency for {company_name}:**\n\n"
            f"- Asset Turnover: **{_x(eff.get('asset_turnover'))}**\n"
            f"- Inventory Turnover: **{_x(eff.get('inventory_turnover'))}**\n"
            f"- Days Inventory Outstanding: **{eff.get('days_inventory_outstanding', 'N/A')} days**\n"
            f"- Days Sales Outstanding: **{eff.get('days_sales_outstanding', 'N/A')} days**\n"
            f"- Days Payable Outstanding: **{eff.get('days_payable_outstanding', 'N/A')} days**\n"
            f"- Cash Conversion Cycle: **{eff.get('cash_conversion_cycle', 'N/A')} days**"
        )

    # ── Personal Advice (check BEFORE generic recommendations) ──────────────
    if "personal_advice" in intents:
        h_label = "strong" if health and health >= 7 else "moderate" if health and health >= 5 else "weak"
        action = (
            "continue building your position here — fundamentals support long-term value creation."
            if health and health >= 7 else
            "review quarterly and consider diversifying to spread risk."
            if health and health >= 5 else
            "reduce exposure and wait for financial improvement before adding more capital."
        )
        return (
            f"**Personal Financial Advice — {company_name}:**\n\n"
            f"Based on your uploaded data, here is my personalised guidance:\n\n"
            f"**Your Financial Position:**\n"
            f"- Revenue: **{_fmt(rev)}** ({_pct(rg)} growth)\n"
            f"- Net Profit: **{_fmt(ni)}** ({_pct(nm)} margin)\n"
            f"- Health Score: **{_num(health)}/10** ({h_label})\n"
            f"- Free Cash Flow: **{_fmt(fcf)}**\n"
            f"- Return on Equity: **{_pct(roe)}**\n\n"
            f"**My Personal Advice:**\n"
            f"1. **Investment stance:** {action}\n"
            f"2. **Cash:** {'Strong cash generation — reinvest for growth.' if fcf and fcf > 0 else 'Negative FCF — monitor cash burn carefully.'}\n"
            f"3. **Debt:** {'Debt is well managed.' if de and de < 1 else 'High debt — prioritize reduction before new investments.'}\n"
            f"4. **Growth:** {'Revenue is growing — good momentum.' if rg and rg > 0 else 'Revenue declining — strategic attention needed.'}\n"
            f"5. **Risk:** {'Risk is manageable.' if health and health >= 5 else 'Risk is elevated — protect your position.'}\n\n"
            f"**Bottom Line:** {'Sound investment based on the data.' if health and health >= 7 else 'Proceed cautiously and monitor quarterly.' if health and health >= 5 else 'High caution — significant improvement needed.'}\n\n"
            "⚠️ *Always consult a licensed financial advisor for personal investment decisions.*"
        )

    # ── Portfolio Advice (check BEFORE generic recommendations) ──────────────
    if "portfolio_advice" in intents:
        return (
            f"**Portfolio Advice — {company_name}:**\n\n"
            f"**Current Position:**\n"
            f"- Health Score: **{_num(health)}/10**\n"
            f"- Net Margin: **{_pct(nm)}** | ROE: **{_pct(roe)}**\n"
            f"- Risk Level: **{'Low' if health and health >= 7 else 'Medium' if health and health >= 5 else 'High'}**\n\n"
            f"**Portfolio Recommendations:**\n"
            f"1. **Diversification:** Consider spreading across 3-5 sectors to reduce concentration risk.\n"
            f"2. **Sector balance:** Add {'defensive sectors like Healthcare or Consumer Staples' if health and health >= 7 else 'quality growth stocks to balance this position'}.\n"
            f"3. **Risk allocation:** {'Can afford slightly higher risk given this stable base.' if health and health >= 7 else 'Stick to lower-risk additions until this position improves.'}\n"
            f"4. **Rebalancing:** Review your allocation every quarter.\n"
            f"5. **Cash reserves:** Keep 10-20% liquid for opportunities.\n\n"
            f"**Action:** {'Hold and build this position.' if health and health >= 7 else 'Monitor closely — reduce if metrics worsen.'}\n\n"
            "⚠️ *Based on uploaded data only. Consult a licensed advisor.*"
        )

    # ── Recommendations ────────────────────────────────────────────────────────
    if "recommendations" in intents:
        recs = []
        if nm and nm < 10: recs.append("**Improve net margins** — reduce operating costs and overheads")
        if de and de > 1.5: recs.append("**Reduce debt** — high D/E ratio increases financial risk")
        if cr and cr < 1.5: recs.append("**Improve liquidity** — current ratio below 1.5 is a concern")
        if fcf and fcf < 0: recs.append("**Fix negative FCF** — reduce capex or improve operating cash flow")
        if rg and rg < 5: recs.append("**Accelerate revenue growth** — explore new markets or products")
        if roe and roe < 10: recs.append("**Improve capital efficiency** — low ROE suggests underutilised equity")
        if not recs: recs = ["Maintain strong operational performance", "Continue disciplined capital allocation", "Explore growth reinvestment opportunities"]
        return f"**Strategic Recommendations for {company_name}:**\n\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(recs))

    if "strengths" in intents:
        strengths = []
        if gm and gm > 40: strengths.append(f"Strong gross margins ({_pct(gm)}) — excellent pricing power")
        if nm and nm > 10: strengths.append(f"Healthy net margins ({_pct(nm)}) — efficient operations")
        if cr and cr > 2: strengths.append(f"Strong liquidity (current ratio {_x(cr)})")
        if fcf and fcf > 0: strengths.append(f"Positive free cash flow ({_fmt(fcf)})")
        if roe and roe > 15: strengths.append(f"High ROE ({_pct(roe)}) — strong shareholder returns")
        if de and de < 0.5: strengths.append("Conservative leverage — low financial risk")
        if not strengths: strengths = ["Established business with measurable financial metrics"]
        return f"**Key Strengths of {company_name}:**\n\n" + "\n".join(f"✅ {s}" for s in strengths)

    if "weaknesses" in intents:
        weaknesses = []
        if nm and nm < 5: weaknesses.append(f"Low net margin ({_pct(nm)}) — profitability needs improvement")
        if cr and cr < 1.5: weaknesses.append(f"Tight liquidity (current ratio {_x(cr)})")
        if de and de > 2: weaknesses.append(f"High leverage (D/E {_x(de)}) — elevated debt risk")
        if fcf and fcf < 0: weaknesses.append(f"Negative free cash flow ({_fmt(fcf)}) — cash burn")
        if roe and roe < 8: weaknesses.append(f"Low ROE ({_pct(roe)}) — poor capital efficiency")
        if not weaknesses: weaknesses = ["No major weaknesses identified — maintain current performance"]
        return f"**Areas for Improvement — {company_name}:**\n\n" + "\n".join(f"⚠️ {w}" for w in weaknesses)

    # ── Summary ────────────────────────────────────────────────────────────────
    if "summary" in intents or "company_info" in intents:
        return (
            f"## {company_name} — Financial Summary ({period})\n\n"
            f"**📊 Financials:**\n"
            f"- Revenue: {_fmt(rev)} | Net Income: {_fmt(ni)}\n"
            f"- Gross Margin: {_pct(gm)} | Net Margin: {_pct(nm)} | ROE: {_pct(roe)}\n\n"
            f"**💧 Liquidity:** Current Ratio {_x(cr)} | Cash {_fmt(cash)}\n\n"
            f"**🏦 Leverage:** D/E {_x(de)} | Interest Coverage {_x(ic)}\n\n"
            f"**💰 Cash Flow:** FCF {_fmt(fcf)} | OCF {_fmt(ocf)}\n\n"
            f"**🎯 Health Score: {_num(health)}/10 | Rating: {rating}**"
        )

    # ── Default ────────────────────────────────────────────────────────────────
    return (
        f"I have full financial data for **{company_name}** ({n_periods} period{'s' if n_periods != 1 else ''} uploaded). "
        f"Latest: **{period}**\n\n"
        f"- Revenue: **{_fmt(rev)}** | Net Income: **{_fmt(ni)}**\n"
        f"- Net Margin: **{_pct(nm)}** | ROE: **{_pct(roe)}**\n"
        f"- Health Score: **{_num(health)}/10**\n\n"
        "You can ask me about:\n"
        "- 💰 Profit, revenue, margins, losses\n"
        "- 📈 Investment advice, growth potential\n"
        "- ⚠️ Risks, Altman Z-Score, Piotroski F\n"
        "- 💧 Liquidity, debt, cash flow\n"
        "- 🎯 Recommendations, strengths, weaknesses"
    )
