"""
chatbot_ml_trainer.py
ML training system for the AI Financial Analyst chatbot.
Generates 10,000+ patterns across 55 intent categories and trains
a TfidfVectorizer + LogisticRegression classifier.
"""

import pickle
import os

# ---------------------------------------------------------------------------
# Compact variant sets  (kept small so Cartesian products stay tractable)
# ---------------------------------------------------------------------------

SHOW2   = ["show me", "tell me", "give me", "what is", "display", "provide",
           "explain", "describe", "list", "summarize", "report"]
SHOW3   = ["show", "tell", "give", "display", "provide", "explain"]
POSS2   = ["my ", "our ", "the company's ", ""]
ADJ2    = ["total ", "annual ", "quarterly ", "net ", "gross ", ""]
VERB2   = ["did", "does", "has", "would"]
CO2     = ["", "the company ", "this company ", "the firm "]
HOW2    = ["how much", "how many", "what is the", "what was the"]


def _cx(templates, **kw_iters):
    """Expand format-string templates with cartesian product of kw_iters values."""
    from itertools import product
    results = set()
    keys = list(kw_iters.keys())
    vals = list(kw_iters.values())
    for combo in product(*vals):
        m = dict(zip(keys, combo))
        for t in templates:
            try:
                results.add(t.format(**m).strip().lower())
            except (KeyError, IndexError):
                pass
    return list(results)


# ---------------------------------------------------------------------------
# Intent generators  — each returns 200+ unique strings
# ---------------------------------------------------------------------------

def gen_revenue():
    a = _cx(["{s} {p}{a}revenue", "{s} {p}sales figures", "{s} {p}top line",
             "{s} {p}turnover", "{h} revenue {p}have"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = _cx(["{h} {a}revenue {v} {c}generate", "{c}revenue breakdown",
             "{s} {a}sales revenue", "net sales figure",
             "{p}revenue performance", "income from sales {s}",
             "{c}total income from operations"],
            s=SHOW3, p=POSS2, a=ADJ2, v=VERB2, c=CO2, h=HOW2)
    return list(set(a + b))


def gen_revenue_growth():
    base = _cx(["{s} {p}revenue growth", "{s} {p}revenue increase",
                "{s} {p}revenue rise", "{s} {p}revenue expansion",
                "year over year revenue {g}", "{a}revenue {g} rate",
                "{h} {p}revenue {g}", "revenue {g} trend",
                "{p}top line {g}"],
               s=SHOW2, p=POSS2, a=ADJ2, h=HOW2,
               g=["growth", "increase", "improvement", "rise"])
    extra = ["how fast is revenue growing", "is our revenue growing",
             "revenue growth percentage", "sales growth rate",
             "how much did revenue grow", "revenue cagr"]
    return list(set(base + extra))


def gen_gross_profit():
    a = _cx(["{s} {p}{a}gross profit", "{s} {p}gross margin",
             "{h} {p}gross profit", "gross margin for the company"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = _cx(["{c}gross income", "{h} gross profit {v} {c}make",
             "{p}gross profit breakdown", "revenue minus cost of goods sold",
             "{a}gross profit figure"],
            s=SHOW3, p=POSS2, a=ADJ2, v=VERB2, c=CO2, h=HOW2)
    return list(set(a + b))


def gen_operating_profit():
    a = _cx(["{s} {p}{a}operating profit", "{s} {p}operating income",
             "{s} {p}operating margin", "{h} {p}operating profit",
             "ebit is", "{a}operating profit for the company",
             "{s} {p}{a}operating earnings", "{h} {p}ebit"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = _cx(["earnings before interest and tax", "{h} operating earnings",
             "{p}profit from operations", "ebit value",
             "{h} {a}operating income {v} {c}earn",
             "{c}operating income breakdown"],
            s=SHOW3, p=POSS2, a=ADJ2, v=VERB2, c=CO2, h=HOW2)
    return list(set(a + b))


def gen_net_profit():
    a = _cx(["{s} {p}{a}net profit", "{s} {p}net income",
             "{s} {p}bottom line", "{h} {p}net earnings",
             "{p}profit after tax", "{s} {p}{a}net earnings",
             "{h} {p}final profit"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = _cx(["{h} {a}net profit {v} {c}earn", "{c}net profit margin",
             "profit after interest and tax", "{a}net earnings",
             "what is the final profit", "{c}net income breakdown"],
            s=SHOW3, p=POSS2, a=ADJ2, v=VERB2, c=CO2, h=HOW2)
    return list(set(a + b))


def gen_ebitda():
    a = _cx(["{s} {p}ebitda", "{h} {p}ebitda", "ebitda margin",
             "{a}ebitda value", "{p}ebitda breakdown",
             "{s} {p}{a}ebitda figure", "{h} {p}ebitda margin"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["earnings before interest tax depreciation amortization",
         "what is the ebitda", "ebitda figure", "ebitda for the company",
         "operating cash earnings", "ebitda does the company report",
         "show ebitda margin", "ebitda analysis", "ebitda ratio",
         "ebitda multiple", "ebitda performance"]
    return list(set(a + b))


def gen_total_profit():
    a = _cx(["{s} {p}total profit", "{s} {p}overall profit",
             "{h} {p}total earnings", "combined profit",
             "aggregate profit", "{s} {p}{a}total profit",
             "{h} {p}{a}overall earnings"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["show all profit figures", "sum of all profits",
         "how profitable is the company", "overall earnings",
         "total profitability", "what is the total profit",
         "combined earnings", "all profit metrics",
         "total income summary", "net total profit"]
    return list(set(a + b))


def gen_total_loss():
    a = _cx(["{s} {p}total loss", "{h} much {v} {c}lose",
             "{p}net loss", "{p}overall losses", "aggregate losses",
             "{s} {p}{a}total loss", "{h} {p}net losses"],
            s=SHOW2, p=POSS2, v=VERB2, c=CO2, a=ADJ2, h=HOW2)
    b = ["what is the total loss", "did the company incur a loss",
         "show loss statement", "financial loss figure", "net loss amount",
         "how much was lost", "loss this year", "negative profit",
         "income deficit", "loss figures"]
    return list(set(a + b))


def gen_should_invest():
    companies = ["the company", "this company", "this firm", "this stock",
                 "this business", "this investment", "this asset"]
    a = _cx(["should i invest in {c}", "is {c} a good investment",
             "would you recommend investing in {c}",
             "is it worth investing in {c}", "is {c} investment worthy",
             "good time to invest in {c}", "should i put money into {c}",
             "is {c} a buy", "should i consider {c} for investment",
             "is {c} a solid investment", "is {c} worth buying"],
            c=companies)
    b = ["should i invest", "is this a good investment",
         "is it a good time to invest", "buy or sell recommendation",
         "investment recommendation", "should i buy shares",
         "is this worth my money"]
    return list(set(a + b))


def gen_where_invest():
    base = ["where should i invest", "which sector should i invest in",
            "best place to invest money", "where would you recommend investing",
            "where should i put my money", "what should i invest in",
            "best investment opportunities", "where to invest for growth",
            "top investment picks", "what stocks should i buy",
            "where is the best investment", "recommend investment areas",
            "investment options available", "what are good investment choices",
            "best performing sectors to invest in", "where can i grow my money",
            "highest return investments", "safe investment options",
            "low risk investment recommendations", "growth investment ideas",
            "where to allocate capital", "which stocks are worth buying",
            "where to put my savings", "best asset class to invest in",
            "which market segment to target", "best dividend stocks",
            "top value stocks to consider", "where to invest for passive income",
            "good etf recommendations", "best sectors for long term investment",
            "where to invest in a bear market", "inflation hedge investments",
            "should i invest in bonds or stocks", "best investment for beginners",
            "low volatility investment options", "high growth investment areas"]
    a = _cx(["{s} {p}investment recommendations",
             "{h} best to invest {p}money"],
            s=SHOW2, p=POSS2, h=HOW2)
    return list(set(base + a))


def gen_growth_potential():
    a = _cx(["{s} {p}growth potential", "{h} {p}growth outlook",
             "growth potential for {c}", "{p}expansion possibilities",
             "does {c} have growth potential", "long term growth for {c}",
             "upside potential for {c}", "{s} {c}growth trajectory"],
            s=SHOW2, p=POSS2, c=CO2, h=HOW2)
    b = ["future growth prospects", "scalability of the company",
         "what is the growth potential", "future prospects",
         "long term upside", "growth runway", "expansion potential"]
    return list(set(a + b))


def gen_best_performing():
    a = _cx(["{s} {p}best financial metrics", "{s} {p}top performing areas",
             "{h} performing well", "strongest area in {p}financials",
             "best segment", "top performer in {p}portfolio"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what is performing well", "highest performing category",
         "outperforming segments", "what does the company do best",
         "best metric", "top financial strength", "where is the company excelling",
         "where have i invested more", "where did i invest more",
         "where have i invested the most", "where is my highest investment",
         "which area has the most investment", "most invested area",
         "where is investment concentrated", "top invested segment",
         "where are my best returns", "highest return area",
         "where is the most money invested", "best return on investment",
         "which metric is best", "top kpi", "best performing kpi",
         "highest margin area", "best profitability metric",
         "what is the company's best performance area",
         "top financial achievement", "best financial outcome",
         "highest earning segment"]
    return list(set(a + b))


def gen_worst_performing():
    a = _cx(["{s} {p}underperforming areas", "{s} {p}worst metrics",
             "{h} performing poorly", "weakest area in {p}financials",
             "worst segment", "lowest performing category"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what is performing poorly", "problem areas in financials",
         "what does the company struggle with", "worst financial metric",
         "underperformance areas", "where is the company falling short"]
    return list(set(a + b))


def gen_investment_risk():
    a = _cx(["{s} {p}investment risk", "{h} risky is {c}",
             "{p}risk level for investing", "risk assessment for {c}",
             "is {c} a risky investment", "risk profile of {c}",
             "downside risk for {c}"],
            s=SHOW2, p=POSS2, c=CO2, h=HOW2)
    b = ["what is the investment risk", "financial risk factors",
         "is it safe to invest", "risk factors", "how risky is this",
         "investment downside", "what could go wrong"]
    return list(set(a + b))


def gen_free_cash_flow():
    a = _cx(["{s} {p}{a}free cash flow", "{h} {p}free cash flow",
             "{a}free cash flow figure", "{p}cash flow after investments"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["fcf for the company", "cash available after capex",
         "free cash generation", "what is the fcf", "free cash flow trend",
         "operating cash minus capex", "fcf value", "free cash flow analysis"]
    return list(set(a + b))


def gen_operating_cf():
    a = _cx(["{s} {p}{a}operating cash flow", "{h} {p}cash from operations",
             "{p}cash from operating activities"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["operating cash flow figure", "cash generated from operations",
         "cash flow from core business", "what is the operating cash flow",
         "cfo figure", "show operating cash flow"]
    return list(set(a + b))


def gen_capex():
    a = _cx(["{s} {p}capital expenditure", "{h} much {v} {c}spend on capex",
             "{p}infrastructure spending", "{a}capital expenditure"],
            s=SHOW2, p=POSS2, v=VERB2, c=CO2, a=ADJ2, h=HOW2)
    b = ["capex figure", "capital spending", "investment in assets",
         "property plant and equipment spending", "what is the capex",
         "capex to revenue ratio", "capex amount"]
    return list(set(a + b))


def gen_dividends():
    a = _cx(["{s} {p}dividends", "{h} much {v} {c}pay in dividends",
             "{p}dividend payout ratio", "{a}dividend payment"],
            s=SHOW2, p=POSS2, v=VERB2, c=CO2, a=ADJ2, h=HOW2)
    b = ["dividend yield", "dividend history", "does the company pay dividends",
         "what is the dividend", "dividend per share", "when are dividends paid",
         "dividend rate"]
    return list(set(a + b))


def gen_cash_flow_summary():
    a = _cx(["{s} {p}cash flow summary", "summarize {p}cash flow",
             "{s} all cash flow figures", "{p}cash position overview",
             "{s} {p}{a}cash flow overview", "{h} {p}overall cash flow"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["overall cash flow", "cash flow overview", "cash flow statement summary",
         "complete cash flow", "cash inflows and outflows",
         "cash flow breakdown", "cash flow analysis",
         "cash flow report", "summarize cash flows",
         "net cash flow"]
    return list(set(a + b))


def gen_liquidity_general():
    a = _cx(["{s} {p}liquidity", "{h} liquid is {c}",
             "{p}ability to meet short term obligations",
             "liquidity position of {c}", "{s} {p}{a}liquidity position",
             "{h} {p}liquidity situation"],
            s=SHOW2, p=POSS2, c=CO2, a=ADJ2, h=HOW2)
    b = ["can the company pay its bills", "short term financial health",
         "what is the liquidity", "liquid assets", "short term solvency",
         "liquidity analysis", "assess liquidity", "liquidity health"]
    return list(set(a + b))


def gen_current_ratio():
    a = _cx(["{s} {p}current ratio", "{h} {p}current ratio",
             "{a}current ratio value"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["current assets divided by current liabilities",
         "short term liquidity ratio", "what is the current ratio",
         "current ratio benchmark", "is the current ratio healthy",
         "current ratio figure"]
    return list(set(a + b))


def gen_quick_ratio():
    a = _cx(["{s} {p}quick ratio", "{h} {p}quick ratio",
             "{a}quick ratio value"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["acid test ratio", "liquid ratio", "what is the quick ratio",
         "cash and receivables vs current liabilities",
         "is the quick ratio good", "acid test value", "quick ratio figure"]
    return list(set(a + b))


def gen_cash_position():
    a = _cx(["{s} {p}cash position", "{h} much cash {v} {c}have",
             "{p}cash balance", "{p}cash reserves", "{a}cash position"],
            s=SHOW2, p=POSS2, v=VERB2, c=CO2, a=ADJ2, h=HOW2)
    b = ["cash and equivalents", "what is the cash on hand",
         "cash holdings", "available cash", "liquidity in cash terms"]
    return list(set(a + b))


def gen_working_capital():
    a = _cx(["{s} {p}working capital", "{h} {p}working capital",
             "{p}net working capital", "{a}working capital figure"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["current assets minus current liabilities", "what is the working capital",
         "working capital ratio", "is working capital positive",
         "short term net assets", "working capital analysis"]
    return list(set(a + b))


def gen_total_debt():
    a = _cx(["{s} {p}total debt", "{h} much debt {v} {c}have",
             "{p}debt level", "{a}total debt figure", "{p}total liabilities"],
            s=SHOW2, p=POSS2, v=VERB2, c=CO2, a=ADJ2, h=HOW2)
    b = ["total borrowings", "outstanding debt", "debt load",
         "how indebted is the company", "debt amount", "what is the total debt"]
    return list(set(a + b))


def gen_debt_to_equity():
    a = _cx(["{s} {p}debt to equity ratio", "{h} {p}leverage",
             "{p}leverage ratio", "{a}debt to equity value"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["d/e ratio", "debt equity ratio", "financial leverage",
         "what is the debt to equity", "debt versus equity",
         "gearing ratio", "leverage figure"]
    return list(set(a + b))


def gen_interest_coverage():
    a = _cx(["{s} {p}interest coverage ratio", "{h} {p}interest coverage",
             "{a}interest coverage ratio"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["can the company cover its interest payments",
         "ebit divided by interest expense", "times interest earned",
         "what is the interest coverage", "ability to pay interest",
         "interest service coverage", "does the company earn enough to pay interest"]
    return list(set(a + b))


def gen_debt_risk():
    a = _cx(["{s} {p}debt risk", "{h} risky is {p}debt",
             "debt risk assessment"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["is the company over leveraged", "is the debt level concerning",
         "default risk", "credit risk from debt",
         "is the company carrying too much debt", "solvency risk",
         "debt sustainability", "high debt warning", "over-leveraged"]
    return list(set(a + b))


def gen_roe():
    a = _cx(["{s} {p}return on equity", "{h} {p}roe", "{a}roe value",
             "{p}equity return"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["roe figure", "return on equity for the company",
         "shareholder return", "what is the return on equity",
         "how well does the company use equity",
         "return generated on shareholder funds", "roe analysis"]
    return list(set(a + b))


def gen_roa():
    a = _cx(["{s} {p}return on assets", "{h} {p}roa", "{a}roa value"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["roa figure", "return on assets for the company", "asset return",
         "what is the return on assets",
         "how well does the company use assets",
         "profit relative to total assets",
         "net income divided by total assets", "roa analysis"]
    return list(set(a + b))


def gen_roce():
    a = _cx(["{s} {p}return on capital employed", "{h} {p}roce",
             "{a}roce value", "{p}capital return metric"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["roce figure", "return on capital employed for the company",
         "capital efficiency", "what is the roce",
         "ebit divided by capital employed", "roce analysis"]
    return list(set(a + b))


def gen_asset_efficiency():
    a = _cx(["{s} {p}asset efficiency", "{h} efficiently {c}use assets",
             "{a}asset turnover value"],
            s=SHOW2, p=POSS2, c=CO2, a=ADJ2, h=HOW2)
    b = ["asset turnover ratio", "asset utilization", "what is the asset turnover",
         "revenue per unit of asset", "fixed asset turnover",
         "how productive are assets", "asset efficiency ratio"]
    return list(set(a + b))


def gen_efficiency():
    a = _cx(["{s} {p}operational efficiency", "{h} efficient is {c}",
             "{p}cost efficiency", "{a}efficiency ratio"],
            s=SHOW2, p=POSS2, c=CO2, a=ADJ2, h=HOW2)
    b = ["operating efficiency metrics", "what is the efficiency",
         "resource utilization", "cost to income ratio",
         "how well does the company manage costs", "productivity metrics",
         "efficiency analysis"]
    return list(set(a + b))


def gen_health_score():
    a = _cx(["{s} {p}financial health score", "{h} {p}financial health",
             "health score", "{p}health rating"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["overall financial health", "financial wellness score",
         "is the company financially healthy", "financial fitness",
         "overall health metric", "financial health assessment",
         "what is the health score"]
    return list(set(a + b))


def gen_kpi_overall():
    a = _cx(["{s} {p}key performance indicators", "{s} {p}kpis",
             "overall kpi dashboard", "{s} all kpis"],
            s=SHOW2, p=POSS2)
    b = ["kpi summary", "all kpi metrics", "performance indicators",
         "kpi overview", "key metrics", "kpi analysis",
         "what are the kpis", "show kpi dashboard"]
    return list(set(a + b))


def gen_altman_z():
    a = _cx(["{s} {p}altman z score", "{h} {p}altman z score",
             "{a}altman z score"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["z score", "bankruptcy prediction score", "altman score",
         "is the company at risk of bankruptcy based on z score",
         "altman model result", "z score analysis",
         "financial distress score altman", "what is the altman z score"]
    return list(set(a + b))


def gen_piotroski():
    a = _cx(["{s} {p}piotroski score", "{h} {p}piotroski f score",
             "{a}piotroski f score"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["f score result", "piotroski analysis", "piotroski financial strength",
         "what is the f score", "piotroski score breakdown",
         "what does the company score on piotroski"]
    return list(set(a + b))


def gen_beneish():
    a = _cx(["{s} {p}beneish m score", "{h} {p}beneish score",
             "{a}beneish m score"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["earnings manipulation score", "beneish analysis",
         "is the company manipulating earnings", "m score",
         "beneish model result", "fraud detection score",
         "what is the beneish score"]
    return list(set(a + b))


def gen_risk_overall():
    a = _cx(["{s} {p}overall risk", "{h} {p}risk profile",
             "overall risk", "{p}risk overview",
             "{s} {p}risk", "{h} risky is {c}",
             "what risk does {c}have", "{p}risk level"],
            s=SHOW2, p=POSS2, h=HOW2, c=CO2)
    b = ["risk summary", "risk assessment", "how risky is the company overall",
         "total risk exposure", "comprehensive risk analysis",
         "risk level", "what is the risk profile",
         "what are the biggest risks", "biggest risks",
         "major risks", "key risks", "main risks",
         "what risks are there", "all risks", "financial risks",
         "tell me the risks", "what are the risks",
         "identify risks", "risk factors", "potential risks",
         "risk analysis", "evaluate risk", "risk evaluation",
         "is it risky", "how risky", "risk overview",
         "what is dangerous about this company",
         "what could go wrong financially",
         "downside risks", "risk exposure",
         "biggest financial risks", "company risk factors",
         "what are the main financial risks",
         "list all risks", "show all risk factors",
         "overall financial risk", "financial danger",
         "risk warnings for this company",
         "what are my investment risks"]
    return list(set(a + b))


def gen_risk_flags():
    a = _cx(["{s} {p}risk flags", "{h} red flags",
             "risk warning signs", "{s} {p}financial red flags",
             "{s} {p}financial warnings", "{h} {p}warning signs"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what are the red flags", "financial red flags",
         "any concerns about the company", "warning flags in financials",
         "potential risks", "risk indicators", "flags and warnings",
         "what should i be worried about", "financial warnings",
         "show me the risks", "danger signals", "risk warnings",
         "warning indicators"]
    return list(set(a + b))


def gen_recommendations():
    a = _cx(["{s} {p}recommendations", "{h} you recommend",
             "financial recommendations", "{s} {p}suggested actions",
             "{s} {p}financial advice", "{h} {p}recommend"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what should the company do to improve", "advice for the company",
         "recommended actions", "what improvements would you suggest",
         "recommended strategy", "action items", "what steps should be taken",
         "financial advice", "what would you recommend", "improvement suggestions",
         "best course of action", "strategic recommendations",
         "financial improvement plan"]
    return list(set(a + b))


def gen_strengths():
    a = _cx(["{s} {p}financial strengths", "{h} strong is {c}",
             "{s} {p}strengths"],
            s=SHOW2, p=POSS2, c=CO2, h=HOW2)
    b = ["what is strong about the company", "key strengths",
         "positive aspects", "what does the company do well financially",
         "financial advantages", "competitive strengths",
         "best financial aspects", "where is the company excelling financially"]
    return list(set(a + b))


def gen_weaknesses():
    a = _cx(["{s} {p}financial weaknesses", "{h} weak is {c}",
             "{s} {p}weaknesses"],
            s=SHOW2, p=POSS2, c=CO2, h=HOW2)
    b = ["what is weak about the company", "key weaknesses",
         "negative aspects", "what does the company do poorly financially",
         "financial disadvantages", "areas of concern",
         "worst financial aspects", "where does the company fall short"]
    return list(set(a + b))


def gen_summary():
    a = _cx(["{s} {p}financial summary", "summarize {p}financials",
             "{s} an overview", "{p}financial snapshot"],
            s=SHOW2, p=POSS2)
    b = ["give me an overview", "financial overview", "overall financial picture",
         "brief summary of finances", "what is the financial situation",
         "quick financial overview", "full financial summary",
         "financial report overview"]
    return list(set(a + b))


def gen_sector():
    a = _cx(["{h} sector is {c}in", "{c}industry", "{h} industry {v} {c}operate in"],
            h=HOW2, c=CO2, v=VERB2)
    b = ["sector classification", "what is the sector",
         "which sector", "business segment", "industry type",
         "which market sector", "what industry is the company in",
         "sector of the company"]
    return list(set(a + b))


def gen_data_period():
    a = _cx(["{s} {p}data period", "{h} the reporting period",
             "{s} the fiscal year covered", "{h} the data date range"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what time period does this data cover", "data period",
         "which year is this data from", "financial year covered",
         "when does this data end", "reporting period",
         "what is the fiscal year", "data date range",
         "time frame of the financial data", "which fiscal period",
         "what year is the data", "data coverage period",
         "fiscal year of the data", "what period does this cover",
         "what years are included", "how recent is this data",
         "when was this data collected", "data freshness",
         "what is the latest data year", "historical period covered"]
    return list(set(a + b))


def gen_revenue_forecast():
    a = _cx(["{s} {p}revenue forecast", "{h} {p}projected revenue",
             "{s} {p}revenue projection", "{p}revenue outlook"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what is the revenue prediction", "future revenue estimate",
         "expected revenue growth", "forecast revenue",
         "predicted sales for next year", "revenue estimate for next year",
         "revenue forecast analysis"]
    return list(set(a + b))


def gen_profit_forecast():
    a = _cx(["{s} {p}profit forecast", "{h} {p}projected profit",
             "{s} {p}profit projection", "{p}earnings outlook"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["what is the profit prediction", "future profit estimate",
         "expected profit growth", "forecast profit",
         "predicted profit for next year", "profit estimate for next year",
         "profit forecast analysis"]
    return list(set(a + b))


def gen_trend_analysis():
    a = _cx(["{s} {p}trend analysis", "{h} {p}financial trends",
             "{p}financial trajectory"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["how do the financials trend", "trend over time",
         "historical trend analysis", "revenue trend",
         "profit trend over years", "financial trends",
         "trend direction", "show trends", "financial trend report"]
    return list(set(a + b))


def gen_cagr():
    a = _cx(["{s} {p}cagr", "{h} {p}compound annual growth rate",
             "{a}cagr value"],
            s=SHOW2, p=POSS2, a=ADJ2, h=HOW2)
    b = ["compound annual growth rate", "what is the cagr",
         "annual growth rate compounded", "cagr figure",
         "cagr over the period", "what is the compound growth",
         "five year cagr", "three year cagr", "cagr analysis"]
    return list(set(a + b))


def gen_benchmarking():
    a = _cx(["{s} {p}benchmarking", "{h} {c}compare to industry"],
            s=SHOW2, p=POSS2, c=CO2, h=HOW2)
    b = ["benchmark analysis", "compare to peers",
         "industry comparison", "vs industry average",
         "how does the company stack up", "peer comparison",
         "sector benchmarks", "competitive positioning",
         "industry benchmark", "benchmarking report"]
    return list(set(a + b))


def gen_greeting():
    return [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "howdy", "greetings", "hi there", "hello there", "hey there",
        "hi kiro", "hello kiro", "good day", "what's up", "whats up",
        "yo", "hiya", "nice to meet you", "how are you", "how do you do",
        "how's it going", "hows it going", "start", "begin",
        "let's start", "lets begin", "get started", "hey assistant",
        "hello assistant", "hi assistant", "morning", "evening",
        "good to meet you", "pleased to meet you", "hi bot", "hello bot",
        "hey bot", "good to see you", "hi there bot", "good morning bot",
        "hello financial analyst", "hi financial analyst",
        "hey financial analyst", "good evening bot",
        "good afternoon assistant", "hi there assistant",
        "hello there assistant", "start chatting", "begin session",
    ]


def gen_thanks():
    return [
        "thank you", "thanks", "thank you so much", "many thanks", "thx",
        "ty", "thanks a lot", "much appreciated", "appreciate it",
        "great thanks", "that's helpful", "thats helpful",
        "that was helpful", "very helpful", "thanks for the info",
        "thanks for the information", "thanks for your help",
        "thank you for the analysis", "appreciated", "cheers",
        "perfect thanks", "awesome thanks", "brilliant thanks",
        "excellent thank you", "wonderful thank you", "that helps",
        "got it thanks", "understood thanks", "ok thanks", "great",
        "fantastic thank you", "i appreciate your help",
        "thanks for the breakdown", "helpful thanks",
        "thank you for explaining", "thanks for clarifying",
        "that clears it up thanks", "much obliged", "you're great",
        "thanks for the insight", "really helpful",
        "appreciate the analysis", "good work thanks",
    ]


def gen_help():
    return [
        "help", "help me", "what can you do", "what can i ask",
        "what questions can i ask", "how does this work", "guide me",
        "what are your capabilities", "what can this chatbot do",
        "show me what you can do", "what topics can you cover",
        "what do you know", "what can i ask you", "what features do you have",
        "how can you help me", "what are the available queries",
        "menu", "options", "topics", "available topics",
        "what financial questions can i ask", "tell me what you can do",
        "capabilities", "features", "how to use this",
        "i need help", "help please", "i'm lost", "im lost",
        "what are the commands", "list all features",
        "show available commands", "what can i query",
        "how do i use this", "user guide", "instructions",
        "what queries are supported", "supported questions",
        "list topics", "show topics", "what can i find here",
        "what financial data can you show", "help with analysis",
        "tutorial", "getting started", "quick start",
        "what can this tool do", "show me the features",
        "what questions can i ask you",
        "how can you assist me",
        "what analysis can you do",
        "what are the available features",
        "give me a list of things you can help with",
    ]


def gen_personal_advice():
    a = _cx(["{h} {p}money", "{h} manage {p}finances",
             "{h} grow {p}wealth"],
            h=HOW2, p=POSS2)
    b = ["give me personal financial advice", "personal investment advice",
         "help me with financial planning", "what would you advise me to do",
         "financial guidance for me", "should i save or invest",
         "personal finance tips", "how to achieve financial freedom",
         "personal financial strategy", "what should i do financially",
         "help me plan my finances", "what should i prioritize financially"]
    return list(set(a + b))


def gen_portfolio_advice():
    a = _cx(["{s} {p}portfolio analysis", "{h} {p}portfolio performing",
             "{p}investment portfolio advice"],
            s=SHOW2, p=POSS2, h=HOW2)
    b = ["portfolio recommendation", "should i diversify my portfolio",
         "portfolio review", "optimize my portfolio",
         "how to balance my portfolio", "portfolio allocation suggestions",
         "what should my portfolio look like",
         "diversification advice", "portfolio strategy"]
    return list(set(a + b))


def gen_market_comparison():
    a = _cx(["{h} {c}compare to the market", "{h} {c}perform vs market",
             "{s} {p}market comparison", "{s} {p}market performance"],
            h=HOW2, c=CO2, s=SHOW2, p=POSS2)
    b = ["market comparison", "vs market average",
         "how does the company perform vs market",
         "market benchmark comparison", "compare to s&p 500",
         "industry vs market", "market position",
         "outperforming the market", "market relative performance",
         "company vs index", "how does the company compare to market",
         "beat the market", "underperform the market",
         "market outperformance", "relative market performance",
         "how does the stock compare to its index",
         "compare to market peers", "market cap comparison",
         "versus the benchmark", "sector vs market"]
    return list(set(a + b))


# ---------------------------------------------------------------------------
# Dataset builder
# ---------------------------------------------------------------------------

INTENT_GENERATORS = {
    "revenue":           gen_revenue,
    "revenue_growth":    gen_revenue_growth,
    "gross_profit":      gen_gross_profit,
    "operating_profit":  gen_operating_profit,
    "net_profit":        gen_net_profit,
    "ebitda":            gen_ebitda,
    "total_profit":      gen_total_profit,
    "total_loss":        gen_total_loss,
    "should_invest":     gen_should_invest,
    "where_invest":      gen_where_invest,
    "growth_potential":  gen_growth_potential,
    "best_performing":   gen_best_performing,
    "worst_performing":  gen_worst_performing,
    "investment_risk":   gen_investment_risk,
    "free_cash_flow":    gen_free_cash_flow,
    "operating_cf":      gen_operating_cf,
    "capex":             gen_capex,
    "dividends":         gen_dividends,
    "cash_flow_summary": gen_cash_flow_summary,
    "liquidity_general": gen_liquidity_general,
    "current_ratio":     gen_current_ratio,
    "quick_ratio":       gen_quick_ratio,
    "cash_position":     gen_cash_position,
    "working_capital":   gen_working_capital,
    "total_debt":        gen_total_debt,
    "debt_to_equity":    gen_debt_to_equity,
    "interest_coverage": gen_interest_coverage,
    "debt_risk":         gen_debt_risk,
    "roe":               gen_roe,
    "roa":               gen_roa,
    "roce":              gen_roce,
    "asset_efficiency":  gen_asset_efficiency,
    "efficiency":        gen_efficiency,
    "health_score":      gen_health_score,
    "kpi_overall":       gen_kpi_overall,
    "altman_z":          gen_altman_z,
    "piotroski":         gen_piotroski,
    "beneish":           gen_beneish,
    "risk_overall":      gen_risk_overall,
    "risk_flags":        gen_risk_flags,
    "recommendations":   gen_recommendations,
    "strengths":         gen_strengths,
    "weaknesses":        gen_weaknesses,
    "summary":           gen_summary,
    "sector":            gen_sector,
    "data_period":       gen_data_period,
    "revenue_forecast":  gen_revenue_forecast,
    "profit_forecast":   gen_profit_forecast,
    "trend_analysis":    gen_trend_analysis,
    "cagr":              gen_cagr,
    "benchmarking":      gen_benchmarking,
    "greeting":          gen_greeting,
    "thanks":            gen_thanks,
    "help":              gen_help,
    "personal_advice":   gen_personal_advice,
    "portfolio_advice":  gen_portfolio_advice,
    "market_comparison": gen_market_comparison,
}


def build_dataset():
    """Generate all (text, label) pairs for every intent."""
    texts, labels = [], []
    for intent, gen_fn in INTENT_GENERATORS.items():
        patterns = list(set(gen_fn()))
        for p in patterns:
            texts.append(p)
            labels.append(intent)
    return texts, labels


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_and_save():
    """Build dataset, train model, save to chatbot_model.pkl, return accuracy."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import accuracy_score

    print("Building dataset...")
    texts, labels = build_dataset()
    print(f"  Total patterns : {len(texts)}")
    print(f"  Total intents  : {len(set(labels))}")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )
    print(f"  Train size: {len(X_train)}  |  Test size: {len(X_test)}")

    print("Training TF-IDF + LogisticRegression pipeline...")
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=20000,
                                  sublinear_tf=True)),
        ("clf",   LogisticRegression(C=5, max_iter=500, solver="lbfgs")),
    ])
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Test accuracy  : {acc:.1%}")

    save_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(save_dir, "chatbot_model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"  Model saved to : {model_path}")

    return acc


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

_pipeline = None


def _load_model():
    global _pipeline
    if _pipeline is None:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "chatbot_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Run train_and_save() first."
            )
        with open(model_path, "rb") as f:
            _pipeline = pickle.load(f)
    return _pipeline


def predict_intent(question: str) -> str:
    """Predict the intent label for a user question string."""
    model = _load_model()
    return model.predict([question.strip().lower()])[0]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    accuracy = train_and_save()
    print(f"\nDone — model trained with accuracy: {accuracy:.1%}")
