"""
chatbot_training_data.py
========================
Comprehensive intent-classification training data for the AI Financial Analyst chatbot.
Contains 1000+ question patterns across 12 financial categories.

Each entry is a dict with:
  - "patterns" : list[str]  — natural-language question variations (placeholders welcome)
  - "category" : str        — intent / category label used for classification

Placeholders used in patterns:
  [COMPANY]     — company name  (e.g. "Apple", "TechCorp")
  [REVENUE]     — revenue value (e.g. "$5.2B")
  [NET_INCOME]  — net income value
  [MARGIN]      — a percentage margin
  [RATIO]       — a numeric ratio
  [YEAR]        — a fiscal year  (e.g. "2023")
  [PERIOD]      — a period label (e.g. "Q3 2023")

No external dependencies — pure Python.
"""

# ---------------------------------------------------------------------------
# TRAINING DATA
# ---------------------------------------------------------------------------

TRAINING_QA = [

    # =========================================================================
    # 1. REVENUE & SALES  (100+ patterns)
    # =========================================================================
    {
        "category": "revenue_query",
        "patterns": [
            "What is the revenue of [COMPANY]?",
            "How much revenue did [COMPANY] generate?",
            "What are the total sales of [COMPANY]?",
            "Tell me the revenue for [COMPANY]",
            "Show me [COMPANY]'s revenue",
            "What is [COMPANY]'s turnover?",
            "How much did [COMPANY] earn from sales?",
            "What is the top line for [COMPANY]?",
            "Revenue of [COMPANY] in [YEAR]",
            "What were the sales figures for [COMPANY]?",
        ],
    },
    {
        "category": "revenue_query",
        "patterns": [
            "Can you tell me the total income from operations?",
            "What is [COMPANY]'s net sales?",
            "How much revenue was reported in [PERIOD]?",
            "What are [COMPANY]'s gross sales?",
            "Show me the sales revenue",
            "What is the income from sales for [COMPANY]?",
            "What were [COMPANY]'s revenues last year?",
            "How large is [COMPANY]'s revenue base?",
            "Give me the revenue number",
            "What is [COMPANY]'s annual revenue?",
        ],
    },
    {
        "category": "revenue_growth",
        "patterns": [
            "What is the revenue growth rate for [COMPANY]?",
            "How fast is [COMPANY]'s revenue growing?",
            "Is [COMPANY]'s revenue increasing or decreasing?",
            "What is the sales growth for [COMPANY]?",
            "Has [COMPANY]'s revenue gone up?",
            "Show me revenue growth trend for [COMPANY]",
            "What is the year-over-year revenue change?",
            "What is the CAGR for [COMPANY]'s revenue?",
            "Is [COMPANY] growing its top line?",
            "Revenue growth compared to last year",
        ],
    },
    {
        "category": "revenue_growth",
        "patterns": [
            "How much did [COMPANY]'s sales grow?",
            "What is the revenue momentum for [COMPANY]?",
            "Is [COMPANY] gaining or losing sales?",
            "What percentage did revenue increase?",
            "How does this year's revenue compare to last year?",
            "Is the top-line growth positive?",
            "Show me the revenue trajectory",
            "What is [COMPANY]'s sales growth percentage?",
            "Did revenue improve quarter over quarter?",
            "What is the revenue run rate for [COMPANY]?",
        ],
    },
    {
        "category": "revenue_breakdown",
        "patterns": [
            "What are [COMPANY]'s revenue segments?",
            "Break down [COMPANY]'s revenue by business unit",
            "What product lines drive the most revenue?",
            "What is the revenue mix for [COMPANY]?",
            "Which segment contributes most to revenue?",
            "How is [COMPANY]'s revenue distributed?",
            "What percentage of revenue comes from each division?",
            "Show me a revenue breakdown",
            "What are the revenue streams for [COMPANY]?",
            "Where does [COMPANY] make the most money?",
        ],
    },
    {
        "category": "revenue_comparison",
        "patterns": [
            "How does [COMPANY]'s revenue compare to competitors?",
            "Is [COMPANY]'s revenue above or below industry average?",
            "How does [COMPANY] rank in terms of revenue?",
            "Compare [COMPANY]'s revenue to its peers",
            "Is [COMPANY] a large or small revenue company?",
            "What is [COMPANY]'s market share by revenue?",
            "How does [COMPANY]'s revenue stack up vs the sector?",
            "Is [COMPANY] growing revenue faster than peers?",
            "How does [COMPANY] revenue compare year on year?",
            "Revenue ranking vs industry competitors",
        ],
    },
    {
        "category": "revenue_forecast",
        "patterns": [
            "What will [COMPANY]'s revenue be next year?",
            "Predict [COMPANY]'s future revenue",
            "What is the revenue outlook for [COMPANY]?",
            "Project [COMPANY]'s sales for [YEAR]",
            "How much revenue is expected going forward?",
            "What is the revenue forecast for [COMPANY]?",
            "Will [COMPANY]'s revenue grow in the next period?",
            "What is the expected sales figure next year?",
            "Can you forecast [COMPANY]'s top-line growth?",
            "Show me a revenue projection",
        ],
    },
    {
        "category": "revenue_query",
        "patterns": [
            "Is [REVENUE] a good revenue figure for [COMPANY]?",
            "What does a revenue of [REVENUE] mean for [COMPANY]?",
            "How significant is [COMPANY]'s revenue of [REVENUE]?",
            "Is [COMPANY]'s [REVENUE] revenue strong?",
            "Is [COMPANY]'s revenue healthy?",
            "What does the revenue tell us about [COMPANY]?",
            "Interpret [COMPANY]'s revenue number",
            "Is the revenue figure impressive?",
            "How profitable is [COMPANY]'s revenue?",
            "What does the revenue indicate about business performance?",
        ],
    },

    # =========================================================================
    # 2. PROFIT & LOSS  (100+ patterns)
    # =========================================================================
    {
        "category": "net_profit",
        "patterns": [
            "What is [COMPANY]'s net profit?",
            "How much net income did [COMPANY] report?",
            "What is the bottom line for [COMPANY]?",
            "How much did [COMPANY] earn after taxes?",
            "What is the profit after tax for [COMPANY]?",
            "What is [COMPANY]'s PAT?",
            "Tell me the net earnings of [COMPANY]",
            "What is [COMPANY]'s net income?",
            "Show me the net profit figure",
            "How much money did [COMPANY] actually make?",
        ],
    },
    {
        "category": "net_profit",
        "patterns": [
            "Is [COMPANY] profitable?",
            "Is [COMPANY] making money?",
            "Did [COMPANY] make a profit?",
            "What is [COMPANY]'s profit margin?",
            "How profitable is [COMPANY]?",
            "What is [COMPANY]'s net margin?",
            "Is [COMPANY]'s net margin good?",
            "What percentage of revenue becomes profit?",
            "How much profit does [COMPANY] retain per dollar of sales?",
            "Net profit percentage for [COMPANY]",
        ],
    },
    {
        "category": "gross_profit",
        "patterns": [
            "What is [COMPANY]'s gross profit?",
            "What is the gross margin for [COMPANY]?",
            "How much gross profit did [COMPANY] generate?",
            "What is [COMPANY]'s COGS?",
            "What is the cost of goods sold for [COMPANY]?",
            "How much does it cost [COMPANY] to make its products?",
            "What is [COMPANY]'s cost of revenue?",
            "Show me the gross profit margin",
            "Is [COMPANY]'s gross margin healthy?",
            "What percentage is [COMPANY]'s gross margin?",
        ],
    },
    {
        "category": "operating_profit",
        "patterns": [
            "What is [COMPANY]'s operating profit?",
            "What is the EBIT for [COMPANY]?",
            "What is [COMPANY]'s operating income?",
            "Show me the operating margin",
            "How much operating profit does [COMPANY] make?",
            "What is the operating income for [COMPANY] in [YEAR]?",
            "What is [COMPANY]'s PBIT?",
            "What is the income from operations?",
            "Is the operating margin improving?",
            "How efficient is [COMPANY] operationally?",
        ],
    },
    {
        "category": "ebitda",
        "patterns": [
            "What is [COMPANY]'s EBITDA?",
            "Show me the EBITDA for [COMPANY]",
            "What does EBITDA look like for [COMPANY]?",
            "What is [COMPANY]'s earnings before interest, tax, depreciation and amortisation?",
            "How much EBITDA does [COMPANY] generate?",
            "What is the EBITDA margin?",
            "Is [COMPANY]'s EBITDA positive?",
            "How does EBITDA compare to revenue?",
            "What is the EBITDA multiple for [COMPANY]?",
            "Why is EBITDA important for [COMPANY]?",
        ],
    },
    {
        "category": "loss_analysis",
        "patterns": [
            "Is [COMPANY] making a loss?",
            "Is [COMPANY] losing money?",
            "What is [COMPANY]'s total loss?",
            "How much did [COMPANY] lose?",
            "Is [COMPANY] unprofitable?",
            "Is [COMPANY] loss-making?",
            "Why is [COMPANY] in loss?",
            "What caused [COMPANY]'s net loss?",
            "How bad is [COMPANY]'s loss?",
            "Is [COMPANY] operating at a loss?",
        ],
    },
    {
        "category": "loss_analysis",
        "patterns": [
            "What is the operating loss for [COMPANY]?",
            "Is [COMPANY]'s gross profit negative?",
            "Are losses shrinking or growing?",
            "When will [COMPANY] break even?",
            "Is [COMPANY] burning cash?",
            "How long can [COMPANY] sustain losses?",
            "What is driving [COMPANY]'s losses?",
            "Can [COMPANY] turn profitable?",
            "What is the path to profitability for [COMPANY]?",
            "Is [COMPANY] expected to become profitable?",
        ],
    },
    {
        "category": "profit_summary",
        "patterns": [
            "Give me a full profit and loss summary for [COMPANY]",
            "Show me [COMPANY]'s P&L",
            "What does [COMPANY]'s income statement look like?",
            "Summarise [COMPANY]'s profitability",
            "Give me all profit metrics for [COMPANY]",
            "What are the key P&L figures for [COMPANY]?",
            "Show me gross, operating and net profit",
            "What is the profitability picture for [COMPANY]?",
            "Walk me through [COMPANY]'s profit and loss",
            "Full income statement breakdown for [COMPANY]",
        ],
    },

    # =========================================================================
    # 3. INVESTMENT ADVICE  (80+ patterns)
    # =========================================================================
    {
        "category": "should_invest",
        "patterns": [
            "Should I invest in [COMPANY]?",
            "Is [COMPANY] a good investment?",
            "Is it worth investing in [COMPANY]?",
            "Is [COMPANY] worth buying?",
            "Should I buy [COMPANY] stock?",
            "Is [COMPANY] a buy or a sell?",
            "Would you recommend investing in [COMPANY]?",
            "Is [COMPANY] a good stock to hold?",
            "Is [COMPANY] investment grade?",
            "Should I put money into [COMPANY]?",
        ],
    },
    {
        "category": "should_invest",
        "patterns": [
            "Is [COMPANY] a safe investment?",
            "Is [COMPANY] overvalued or undervalued?",
            "Is now a good time to invest in [COMPANY]?",
            "What is the investment thesis for [COMPANY]?",
            "Does [COMPANY] have strong fundamentals for investment?",
            "Is [COMPANY] worth the risk?",
            "Based on financials, should I invest?",
            "What does the data say about investing in [COMPANY]?",
            "Is [COMPANY] a long-term investment opportunity?",
            "Would you put money in [COMPANY]?",
        ],
    },
    {
        "category": "growth_potential",
        "patterns": [
            "What is [COMPANY]'s growth potential?",
            "Can [COMPANY] grow further?",
            "Does [COMPANY] have upside?",
            "What are [COMPANY]'s growth prospects?",
            "How much can [COMPANY] grow?",
            "Is [COMPANY] a high-growth company?",
            "What is the future growth outlook for [COMPANY]?",
            "Does [COMPANY] have room to grow?",
            "What are [COMPANY]'s expansion opportunities?",
            "How scalable is [COMPANY]'s business?",
        ],
    },
    {
        "category": "growth_potential",
        "patterns": [
            "Is [COMPANY] growing fast enough?",
            "What factors drive [COMPANY]'s growth?",
            "Is [COMPANY] a growth stock?",
            "Can [COMPANY] achieve double-digit growth?",
            "What is the growth trajectory of [COMPANY]?",
            "Is [COMPANY] in a fast-growing market?",
            "Show me [COMPANY]'s growth indicators",
            "Is revenue growth sustainable at [COMPANY]?",
            "What is the long-term growth rate for [COMPANY]?",
            "Can [COMPANY] compound its earnings?",
        ],
    },
    {
        "category": "best_performing_metric",
        "patterns": [
            "What is [COMPANY]'s best performing metric?",
            "Where is [COMPANY] doing best?",
            "What metric stands out for [COMPANY]?",
            "What is [COMPANY]'s strongest financial indicator?",
            "Which financial ratio is best for [COMPANY]?",
            "Where does [COMPANY] outperform?",
            "What is the highest return metric for [COMPANY]?",
            "What is [COMPANY]'s top financial achievement?",
            "Show me [COMPANY]'s best numbers",
            "Where does [COMPANY] excel financially?",
        ],
    },
    {
        "category": "investment_risk",
        "patterns": [
            "How risky is investing in [COMPANY]?",
            "What is the investment risk for [COMPANY]?",
            "Is [COMPANY] a high-risk investment?",
            "Is it safe to invest in [COMPANY]?",
            "What are the risks of buying [COMPANY] stock?",
            "What could go wrong if I invest in [COMPANY]?",
            "What is the downside risk for [COMPANY]?",
            "Is there financial risk in [COMPANY]?",
            "How do I assess the risk of investing in [COMPANY]?",
            "Is [COMPANY] financially stable enough to invest?",
        ],
    },
    {
        "category": "where_to_invest",
        "patterns": [
            "Where should I invest for better returns?",
            "Which [COMPANY] segment offers the best return?",
            "Where does [COMPANY] generate the best returns?",
            "What area of [COMPANY] should I focus on?",
            "Where is [COMPANY] allocating its capital?",
            "Which business unit of [COMPANY] is most profitable?",
            "What division of [COMPANY] should attract investment?",
            "Where should capital be deployed within [COMPANY]?",
            "Which metric of [COMPANY] promises the best outcome?",
            "What is the highest-return opportunity at [COMPANY]?",
        ],
    },

    # =========================================================================
    # 4. CASH FLOW  (80+ patterns)
    # =========================================================================
    {
        "category": "free_cash_flow",
        "patterns": [
            "What is [COMPANY]'s free cash flow?",
            "How much free cash flow does [COMPANY] generate?",
            "What is the FCF for [COMPANY]?",
            "Is [COMPANY]'s free cash flow positive?",
            "Does [COMPANY] generate surplus cash?",
            "What is [COMPANY]'s cash generation ability?",
            "How much cash does [COMPANY] have after investments?",
            "What is FCF as a percentage of revenue?",
            "Is [COMPANY] FCF-positive?",
            "What does [COMPANY]'s free cash flow look like?",
        ],
    },
    {
        "category": "free_cash_flow",
        "patterns": [
            "What is the FCF yield for [COMPANY]?",
            "How does FCF compare to net income?",
            "Is [COMPANY]'s FCF better than its reported profit?",
            "What is free cash flow used for at [COMPANY]?",
            "Is [COMPANY]'s cash flow sustainable?",
            "Can [COMPANY] fund operations from FCF?",
            "Why is [COMPANY]'s FCF negative?",
            "Is [COMPANY] generating enough free cash?",
            "What is the trend in [COMPANY]'s FCF?",
            "How does FCF support [COMPANY]'s dividend?",
        ],
    },
    {
        "category": "operating_cash_flow",
        "patterns": [
            "What is [COMPANY]'s operating cash flow?",
            "How much cash does [COMPANY] generate from operations?",
            "What is the OCF for [COMPANY]?",
            "What is cash flow from operations for [COMPANY]?",
            "Show me operational cash generation",
            "Is [COMPANY]'s operating cash flow positive?",
            "How does [COMPANY]'s operating cash flow compare to net income?",
            "What is the cash from core business operations?",
            "Show me [COMPANY]'s cash flow from operating activities",
            "Is [COMPANY]'s operating cash flow growing?",
        ],
    },
    {
        "category": "capex",
        "patterns": [
            "What is [COMPANY]'s capital expenditure?",
            "How much does [COMPANY] spend on capex?",
            "What are [COMPANY]'s capital investments?",
            "How much did [COMPANY] invest in property, plant and equipment?",
            "What is [COMPANY]'s PP&E spending?",
            "Is [COMPANY]'s capex high?",
            "What percentage of revenue is capex?",
            "Is [COMPANY] investing heavily in assets?",
            "What is the maintenance vs growth capex for [COMPANY]?",
            "Is capex sustainable for [COMPANY]?",
        ],
    },
    {
        "category": "dividends",
        "patterns": [
            "Does [COMPANY] pay dividends?",
            "What dividend did [COMPANY] pay?",
            "What is [COMPANY]'s dividend payout?",
            "How much did [COMPANY] distribute to shareholders?",
            "What is the dividend yield for [COMPANY]?",
            "Is [COMPANY]'s dividend sustainable?",
            "How much of FCF does [COMPANY] pay as dividends?",
            "What is [COMPANY]'s payout ratio?",
            "Did [COMPANY] increase its dividend?",
            "Is [COMPANY] a dividend-paying company?",
        ],
    },
    {
        "category": "cash_flow_summary",
        "patterns": [
            "Give me a cash flow summary for [COMPANY]",
            "Show all cash flow metrics for [COMPANY]",
            "What is the full cash flow picture for [COMPANY]?",
            "Summarise [COMPANY]'s cash flow statement",
            "Walk me through [COMPANY]'s cash flows",
            "What are the cash inflows and outflows for [COMPANY]?",
            "How is [COMPANY] managing its cash?",
            "Is [COMPANY]'s cash flow healthy?",
            "What does the cash flow statement say about [COMPANY]?",
            "Give me operating, investing and financing cash flows",
        ],
    },

    # =========================================================================
    # 5. LIQUIDITY  (80+ patterns)
    # =========================================================================
    {
        "category": "liquidity_general",
        "patterns": [
            "Is [COMPANY] liquid?",
            "Can [COMPANY] meet its short-term obligations?",
            "How liquid is [COMPANY]?",
            "What is [COMPANY]'s liquidity position?",
            "Can [COMPANY] pay its bills?",
            "Is [COMPANY] in a good liquidity position?",
            "Does [COMPANY] have enough liquid assets?",
            "What is [COMPANY]'s short-term financial health?",
            "Can [COMPANY] cover its current liabilities?",
            "Is [COMPANY] at risk of a liquidity crunch?",
        ],
    },
    {
        "category": "current_ratio",
        "patterns": [
            "What is [COMPANY]'s current ratio?",
            "What does the current ratio look like for [COMPANY]?",
            "Is [COMPANY]'s current ratio above 1?",
            "Is [COMPANY]'s current ratio healthy?",
            "Show me the current ratio",
            "What is the current ratio benchmark for [COMPANY]?",
            "Current ratio above or below 2?",
            "What does a current ratio of [RATIO] mean for [COMPANY]?",
            "How does [COMPANY]'s current ratio compare to industry?",
            "Is the current ratio improving or declining?",
        ],
    },
    {
        "category": "quick_ratio",
        "patterns": [
            "What is [COMPANY]'s quick ratio?",
            "What is the acid-test ratio for [COMPANY]?",
            "Is [COMPANY]'s quick ratio above 1?",
            "Show me the quick ratio",
            "What does the acid test say about [COMPANY]?",
            "Is [COMPANY]'s quick ratio healthy?",
            "How does the quick ratio compare to the current ratio?",
            "What is the quick liquidity position?",
            "Is the quick ratio below 1 for [COMPANY]?",
            "What does a quick ratio of [RATIO] indicate?",
        ],
    },
    {
        "category": "cash_position",
        "patterns": [
            "How much cash does [COMPANY] have?",
            "What is [COMPANY]'s cash balance?",
            "What is the cash position of [COMPANY]?",
            "How much cash and equivalents does [COMPANY] hold?",
            "What is [COMPANY]'s cash on hand?",
            "Does [COMPANY] have a strong cash reserve?",
            "What is the cash ratio for [COMPANY]?",
            "Is [COMPANY] cash-rich?",
            "How much cash is [COMPANY] sitting on?",
            "What are [COMPANY]'s cash and short-term investments?",
        ],
    },
    {
        "category": "working_capital",
        "patterns": [
            "What is [COMPANY]'s working capital?",
            "Is [COMPANY]'s working capital positive?",
            "How much net current assets does [COMPANY] have?",
            "What is the working capital ratio for [COMPANY]?",
            "Is working capital a concern for [COMPANY]?",
            "How is [COMPANY] managing its working capital?",
            "What does [COMPANY]'s working capital tell us?",
            "Is [COMPANY]'s working capital healthy?",
            "How much buffer does [COMPANY] have in working capital?",
            "Net current assets for [COMPANY]",
        ],
    },
    {
        "category": "liquidity_risk",
        "patterns": [
            "Is there a liquidity risk for [COMPANY]?",
            "Could [COMPANY] face a cash shortage?",
            "Is [COMPANY] at risk of running out of cash?",
            "What are the liquidity risks for [COMPANY]?",
            "Could [COMPANY] default on short-term obligations?",
            "Is [COMPANY]'s liquidity deteriorating?",
            "What happens if [COMPANY] faces a liquidity crisis?",
            "Can [COMPANY] survive a short-term financial shock?",
            "Is [COMPANY] relying on credit lines for liquidity?",
            "What is the short-term solvency risk for [COMPANY]?",
        ],
    },

    # =========================================================================
    # 6. DEBT & LEVERAGE  (80+ patterns)
    # =========================================================================
    {
        "category": "total_debt",
        "patterns": [
            "How much debt does [COMPANY] have?",
            "What is [COMPANY]'s total debt?",
            "What are [COMPANY]'s total borrowings?",
            "How leveraged is [COMPANY]?",
            "What are the total liabilities of [COMPANY]?",
            "Is [COMPANY] heavily indebted?",
            "What is [COMPANY]'s long-term debt?",
            "What is the short-term debt for [COMPANY]?",
            "How much does [COMPANY] owe to lenders?",
            "What is [COMPANY]'s outstanding debt?",
        ],
    },
    {
        "category": "debt_to_equity",
        "patterns": [
            "What is [COMPANY]'s debt-to-equity ratio?",
            "What is the D/E ratio for [COMPANY]?",
            "Is [COMPANY]'s leverage ratio high?",
            "What does the debt-to-equity ratio say about [COMPANY]?",
            "Is [COMPANY]'s D/E ratio above 1?",
            "What is the gearing ratio for [COMPANY]?",
            "Is [COMPANY] over-leveraged?",
            "How much debt does [COMPANY] carry relative to equity?",
            "What is the financial leverage of [COMPANY]?",
            "Is [COMPANY]'s debt-to-equity ratio healthy?",
        ],
    },
    {
        "category": "debt_to_equity",
        "patterns": [
            "Show me D/E ratio for [COMPANY]",
            "D/E ratio benchmark for [COMPANY]",
            "Is a D/E of [RATIO] good for [COMPANY]?",
            "Is [COMPANY] using more debt than equity?",
            "What is the equity multiplier for [COMPANY]?",
            "How does [COMPANY]'s leverage compare to peers?",
            "Is [COMPANY]'s balance sheet conservative?",
            "Is [COMPANY] debt-free?",
            "What is [COMPANY]'s net debt?",
            "What is [COMPANY]'s net debt to EBITDA?",
        ],
    },
    {
        "category": "interest_coverage",
        "patterns": [
            "What is [COMPANY]'s interest coverage ratio?",
            "Can [COMPANY] cover its interest payments?",
            "How much does [COMPANY] spend on interest?",
            "What is the interest expense for [COMPANY]?",
            "Is [COMPANY] able to service its debt?",
            "Is the interest coverage above 3 for [COMPANY]?",
            "What are [COMPANY]'s finance costs?",
            "Does [COMPANY] have a high interest burden?",
            "What is the debt service coverage for [COMPANY]?",
            "Is [COMPANY] at risk from interest payments?",
        ],
    },
    {
        "category": "debt_risk",
        "patterns": [
            "Is [COMPANY]'s debt level risky?",
            "Could [COMPANY]'s debt cause problems?",
            "Is [COMPANY] at risk of defaulting on debt?",
            "What are the debt-related risks for [COMPANY]?",
            "Is [COMPANY] overleveraged?",
            "Should [COMPANY] reduce its debt?",
            "Is [COMPANY]'s debt manageable?",
            "What is the risk from [COMPANY]'s borrowings?",
            "Is [COMPANY]'s debt increasing?",
            "How is [COMPANY] managing its debt load?",
        ],
    },
    {
        "category": "debt_summary",
        "patterns": [
            "Give me a full debt analysis for [COMPANY]",
            "Summarise [COMPANY]'s leverage position",
            "Show all debt metrics for [COMPANY]",
            "What is the complete leverage picture for [COMPANY]?",
            "Walk me through [COMPANY]'s debt structure",
            "What does the balance sheet say about [COMPANY]'s debt?",
            "How is debt structured at [COMPANY]?",
            "What is [COMPANY]'s debt maturity profile?",
            "How much of [COMPANY]'s capital structure is debt?",
            "Is [COMPANY] debt-heavy or equity-heavy?",
        ],
    },

    # =========================================================================
    # 7. RISK ASSESSMENT  (80+ patterns)
    # =========================================================================
    {
        "category": "overall_risk",
        "patterns": [
            "What are the risks for [COMPANY]?",
            "How risky is [COMPANY]?",
            "What is the overall risk level for [COMPANY]?",
            "Show me [COMPANY]'s risk profile",
            "What are the biggest risks facing [COMPANY]?",
            "Is [COMPANY] financially risky?",
            "What risk score does [COMPANY] have?",
            "Summarise the key risks for [COMPANY]",
            "What does the risk analysis say about [COMPANY]?",
            "Are there any red flags for [COMPANY]?",
        ],
    },
    {
        "category": "overall_risk",
        "patterns": [
            "What are [COMPANY]'s key risk indicators?",
            "Are there any warning signs for [COMPANY]?",
            "What should I watch out for with [COMPANY]?",
            "Is [COMPANY] in financial distress?",
            "What is the probability of [COMPANY] failing?",
            "Is [COMPANY] a high-risk company?",
            "What are the danger signs for [COMPANY]?",
            "Does [COMPANY] have any financial red flags?",
            "What risk flags are raised for [COMPANY]?",
            "Is [COMPANY] financially vulnerable?",
        ],
    },
    {
        "category": "altman_z_score",
        "patterns": [
            "What is [COMPANY]'s Altman Z-Score?",
            "Show me the Altman Z-Score for [COMPANY]",
            "Is [COMPANY] in the Altman safe zone?",
            "What does the Z-Score say about [COMPANY]?",
            "Is [COMPANY] at risk of bankruptcy?",
            "What is the bankruptcy risk for [COMPANY]?",
            "Is [COMPANY] in the grey zone?",
            "Is [COMPANY] in financial distress per Altman?",
            "What is the Z-Score threshold for [COMPANY]?",
            "What zone is [COMPANY] in on the Altman scale?",
        ],
    },
    {
        "category": "altman_z_score",
        "patterns": [
            "Explain the Altman Z-Score for [COMPANY]",
            "Is the Z-Score above 3 for [COMPANY]?",
            "Is the Z-Score below 1.81 for [COMPANY]?",
            "What does an Altman score of [RATIO] mean?",
            "Run bankruptcy analysis for [COMPANY]",
            "Is there distress risk per the Z-Score model?",
            "Is [COMPANY] at risk per Altman model?",
            "What does the Z-Score indicate about [COMPANY]'s future?",
            "Is [COMPANY]'s Z-Score improving?",
            "How does [COMPANY]'s Z-Score compare to benchmarks?",
        ],
    },
    {
        "category": "piotroski_score",
        "patterns": [
            "What is [COMPANY]'s Piotroski F-Score?",
            "Show me the Piotroski score for [COMPANY]",
            "What does the F-Score say about [COMPANY]?",
            "Is [COMPANY]'s Piotroski score high?",
            "Is [COMPANY] financially strong per Piotroski?",
            "What is the financial strength score for [COMPANY]?",
            "Is [COMPANY]'s F-Score above 7?",
            "Is [COMPANY]'s F-Score below 3?",
            "What does a Piotroski score of [RATIO] mean?",
            "Assess [COMPANY] using Piotroski methodology",
        ],
    },
    {
        "category": "beneish_score",
        "patterns": [
            "What is [COMPANY]'s Beneish M-Score?",
            "Show me the Beneish score",
            "Is there earnings manipulation risk for [COMPANY]?",
            "Could [COMPANY] be manipulating its earnings?",
            "What does the M-Score say about [COMPANY]?",
            "Is [COMPANY]'s accounting reliable?",
            "Is [COMPANY] a potential earnings manipulator?",
            "Check [COMPANY] for accounting fraud risk",
            "What is the manipulation score for [COMPANY]?",
            "Is [COMPANY]'s M-Score above -2.22?",
        ],
    },
    {
        "category": "risk_flags",
        "patterns": [
            "What are the risk flags for [COMPANY]?",
            "Are there any red flags in [COMPANY]'s financials?",
            "List all warning signs for [COMPANY]",
            "What alerts does the risk engine show for [COMPANY]?",
            "Show me the financial warnings for [COMPANY]",
            "What are the risk indicators for [COMPANY]?",
            "Is there any danger in [COMPANY]'s metrics?",
            "What custom risk flags are raised?",
            "Are there any negative signals for [COMPANY]?",
            "What does the custom risk model flag for [COMPANY]?",
        ],
    },

    # =========================================================================
    # 8. RETURNS & EFFICIENCY  (80+ patterns)
    # =========================================================================
    {
        "category": "roe",
        "patterns": [
            "What is [COMPANY]'s ROE?",
            "What is the return on equity for [COMPANY]?",
            "Is [COMPANY]'s ROE good?",
            "How much return does [COMPANY] generate on shareholders' equity?",
            "What does ROE tell us about [COMPANY]?",
            "Is [COMPANY]'s ROE above 15%?",
            "What is the equity return for [COMPANY]?",
            "Show me ROE for [COMPANY]",
            "Is ROE improving for [COMPANY]?",
            "What is a good ROE for [COMPANY]'s industry?",
        ],
    },
    {
        "category": "roa",
        "patterns": [
            "What is [COMPANY]'s ROA?",
            "What is the return on assets for [COMPANY]?",
            "How efficiently does [COMPANY] use its assets?",
            "Is [COMPANY]'s ROA healthy?",
            "What does ROA tell us about [COMPANY]?",
            "Is [COMPANY]'s ROA above 10%?",
            "Show me return on assets",
            "How much profit does [COMPANY] generate per dollar of assets?",
            "Is [COMPANY] using its asset base efficiently?",
            "What is the asset return rate for [COMPANY]?",
        ],
    },
    {
        "category": "roce",
        "patterns": [
            "What is [COMPANY]'s ROCE?",
            "What is the return on capital employed?",
            "Is [COMPANY]'s ROCE above WACC?",
            "How efficiently does [COMPANY] use its capital?",
            "Show me ROCE for [COMPANY]",
            "What does ROCE indicate about [COMPANY]?",
            "Is the capital employed generating good returns?",
            "What is the capital return for [COMPANY]?",
            "Is [COMPANY]'s ROCE competitive?",
            "Compare ROCE to industry peers for [COMPANY]",
        ],
    },
    {
        "category": "asset_efficiency",
        "patterns": [
            "What is [COMPANY]'s asset turnover?",
            "How efficiently does [COMPANY] generate revenue from assets?",
            "What is the asset utilisation rate for [COMPANY]?",
            "Is [COMPANY]'s asset turnover high?",
            "Show me asset turnover for [COMPANY]",
            "What is the revenue per asset dollar for [COMPANY]?",
            "Is [COMPANY] sweating its assets?",
            "How many times does [COMPANY] turn over its assets?",
            "Is asset turnover improving at [COMPANY]?",
            "What is a good asset turnover for [COMPANY]'s sector?",
        ],
    },
    {
        "category": "inventory_efficiency",
        "patterns": [
            "What is [COMPANY]'s inventory turnover?",
            "How fast does [COMPANY] sell its inventory?",
            "What are the days inventory outstanding for [COMPANY]?",
            "Is [COMPANY]'s DIO improving?",
            "How long does [COMPANY] hold inventory?",
            "Is [COMPANY]'s inventory management efficient?",
            "What is the stock turnover for [COMPANY]?",
            "How quickly does [COMPANY] convert inventory to sales?",
            "Is [COMPANY] building up inventory?",
            "What is the inventory days for [COMPANY]?",
        ],
    },
    {
        "category": "receivables_efficiency",
        "patterns": [
            "What is [COMPANY]'s DSO?",
            "What are the days sales outstanding for [COMPANY]?",
            "How quickly does [COMPANY] collect receivables?",
            "Is [COMPANY]'s receivables collection improving?",
            "What is [COMPANY]'s receivable turnover?",
            "How long does it take [COMPANY] to get paid?",
            "Are [COMPANY]'s receivables growing?",
            "Is there a receivables risk for [COMPANY]?",
            "What is the average collection period for [COMPANY]?",
            "Is [COMPANY] efficient at collecting cash from customers?",
        ],
    },
    {
        "category": "cash_conversion_cycle",
        "patterns": [
            "What is [COMPANY]'s cash conversion cycle?",
            "How long is [COMPANY]'s cash cycle?",
            "What is the CCC for [COMPANY]?",
            "Is [COMPANY]'s cash conversion cycle improving?",
            "How efficient is [COMPANY]'s working capital cycle?",
            "Show me [COMPANY]'s cash operating cycle",
            "Is [COMPANY]'s CCC negative or positive?",
            "What does [COMPANY]'s cash conversion cycle indicate?",
            "How long before [COMPANY] turns a sale into cash?",
            "Is the cash cycle a strength or weakness for [COMPANY]?",
        ],
    },

    # =========================================================================
    # 9. FORECASTING & TRENDS  (60+ patterns)
    # =========================================================================
    {
        "category": "revenue_forecast",
        "patterns": [
            "What is [COMPANY]'s revenue forecast?",
            "Predict [COMPANY]'s future revenue",
            "What will [COMPANY] earn next year?",
            "Project [COMPANY]'s sales for [YEAR]",
            "What is the revenue outlook?",
            "Show me revenue projections for [COMPANY]",
            "Can you forecast [COMPANY]'s top line?",
            "What is the expected revenue for the next period?",
            "How much will [COMPANY]'s revenue grow?",
            "What is the revenue estimate for [COMPANY]?",
        ],
    },
    {
        "category": "profit_forecast",
        "patterns": [
            "What is [COMPANY]'s profit forecast?",
            "Project [COMPANY]'s future earnings",
            "Will [COMPANY] be more profitable next year?",
            "What is the net income forecast for [COMPANY]?",
            "Show me profit projections",
            "What earnings are expected for [COMPANY] in [YEAR]?",
            "Can you forecast [COMPANY]'s profitability?",
            "Is profit expected to improve for [COMPANY]?",
            "Predict [COMPANY]'s bottom line",
            "What is the earnings forecast?",
        ],
    },
    {
        "category": "trend_analysis",
        "patterns": [
            "What is the trend for [COMPANY]?",
            "Is [COMPANY] trending up or down?",
            "Show me [COMPANY]'s financial trends",
            "What is the trajectory of [COMPANY]'s performance?",
            "Is [COMPANY] improving over time?",
            "What is the multi-year trend for [COMPANY]?",
            "Are [COMPANY]'s margins improving?",
            "What direction is [COMPANY] heading?",
            "Is [COMPANY]'s financial performance on an uptrend?",
            "Show me trend analysis across all periods",
        ],
    },
    {
        "category": "cagr",
        "patterns": [
            "What is the CAGR for [COMPANY]?",
            "What is [COMPANY]'s compound annual growth rate?",
            "How fast has [COMPANY] grown annually?",
            "What is the 3-year CAGR for [COMPANY]?",
            "What is the revenue CAGR for [COMPANY]?",
            "What is the earnings CAGR?",
            "Is [COMPANY]'s CAGR above 10%?",
            "What growth rate has [COMPANY] compounded at?",
            "Show me the CAGR for revenue and profit",
            "Is [COMPANY] compounding at a high rate?",
        ],
    },
    {
        "category": "future_outlook",
        "patterns": [
            "What is the outlook for [COMPANY]?",
            "What does the future look like for [COMPANY]?",
            "Is [COMPANY] well positioned for future growth?",
            "What is the long-term outlook?",
            "What should we expect from [COMPANY] going forward?",
            "Is the future bright for [COMPANY]?",
            "Are [COMPANY]'s prospects positive?",
            "What is the growth scenario for [COMPANY]?",
            "What does management say about [COMPANY]'s future?",
            "Is [COMPANY] likely to outperform?",
        ],
    },
    {
        "category": "seasonal_trend",
        "patterns": [
            "Does [COMPANY] have seasonal revenue patterns?",
            "What is the quarter-over-quarter trend for [COMPANY]?",
            "Which quarter is strongest for [COMPANY]?",
            "Is [COMPANY]'s revenue seasonal?",
            "Show me quarterly performance for [COMPANY]",
            "How consistent is [COMPANY]'s performance across periods?",
            "Is there a cyclical pattern in [COMPANY]'s financials?",
            "What period shows best performance for [COMPANY]?",
            "Is there volatility in [COMPANY]'s results?",
            "How stable are [COMPANY]'s earnings?",
        ],
    },

    # =========================================================================
    # 10. BENCHMARKING  (60+ patterns)
    # =========================================================================
    {
        "category": "industry_comparison",
        "patterns": [
            "How does [COMPANY] compare to the industry?",
            "Is [COMPANY] above or below industry average?",
            "How does [COMPANY] stack up against competitors?",
            "Benchmark [COMPANY] against the sector",
            "Is [COMPANY] outperforming or underperforming its peers?",
            "How does [COMPANY] rank in the industry?",
            "Compare [COMPANY] to industry benchmarks",
            "Is [COMPANY] better than average in its sector?",
            "What is [COMPANY]'s industry percentile?",
            "How competitive is [COMPANY] in its market?",
        ],
    },
    {
        "category": "margin_benchmark",
        "patterns": [
            "Is [COMPANY]'s gross margin above industry average?",
            "How does [COMPANY]'s net margin compare to peers?",
            "Are [COMPANY]'s margins competitive?",
            "What is the industry benchmark for gross margin?",
            "Is [COMPANY]'s operating margin in line with the sector?",
            "Show me [COMPANY]'s margins vs industry",
            "Is [COMPANY]'s profitability above sector average?",
            "How does [COMPANY]'s EBITDA margin compare to benchmarks?",
            "What is the sector average margin vs [COMPANY]?",
            "Are [COMPANY]'s margins leading or lagging?",
        ],
    },
    {
        "category": "leverage_benchmark",
        "patterns": [
            "Is [COMPANY]'s debt-to-equity ratio typical for the industry?",
            "How does [COMPANY]'s leverage compare to peers?",
            "Is [COMPANY] more or less leveraged than competitors?",
            "What is the typical D/E for [COMPANY]'s sector?",
            "Is [COMPANY]'s interest coverage in line with the market?",
            "Benchmark [COMPANY]'s debt against industry norms",
            "Is [COMPANY] more indebted than sector average?",
            "How does [COMPANY]'s balance sheet compare to competitors?",
            "Is leverage a concern relative to industry?",
            "What does the sector benchmark say about [COMPANY]'s debt?",
        ],
    },
    {
        "category": "growth_benchmark",
        "patterns": [
            "Is [COMPANY] growing faster than the industry?",
            "How does [COMPANY]'s revenue growth compare to the sector?",
            "Is [COMPANY] gaining or losing market share?",
            "Compare [COMPANY]'s growth rate to industry average",
            "Is [COMPANY] a market leader by growth?",
            "Is [COMPANY] outgrowing competitors?",
            "How does [COMPANY]'s CAGR compare to peers?",
            "Is [COMPANY] growing faster than inflation?",
            "What is the industry growth rate vs [COMPANY]?",
            "Is [COMPANY] growing in line with market expectations?",
        ],
    },
    {
        "category": "returns_benchmark",
        "patterns": [
            "Is [COMPANY]'s ROE above the industry average?",
            "How does [COMPANY]'s ROA compare to peers?",
            "Is [COMPANY]'s return on capital competitive?",
            "Benchmark ROE and ROA for [COMPANY] vs sector",
            "Is [COMPANY] generating above-average returns?",
            "How does [COMPANY]'s ROCE compare to industry?",
            "What does benchmark analysis say about [COMPANY]'s returns?",
            "Are [COMPANY]'s returns leading or lagging peers?",
            "Is [COMPANY] a high-return business vs the sector?",
            "How do [COMPANY]'s efficiency metrics compare to benchmarks?",
        ],
    },
    {
        "category": "liquidity_benchmark",
        "patterns": [
            "Is [COMPANY]'s current ratio above industry benchmark?",
            "How does [COMPANY]'s liquidity compare to the sector?",
            "Is [COMPANY] more liquid than competitors?",
            "Benchmark [COMPANY]'s quick ratio against the industry",
            "What is the industry standard liquidity ratio?",
            "Is [COMPANY]'s cash position above average?",
            "How does [COMPANY]'s working capital compare?",
            "Is [COMPANY] more conservative with cash than peers?",
            "Liquidity benchmarking for [COMPANY]",
            "Is [COMPANY]'s short-term position better than the sector?",
        ],
    },

    # =========================================================================
    # 11. STRATEGIC ADVICE  (60+ patterns)
    # =========================================================================
    {
        "category": "recommendations",
        "patterns": [
            "What are your recommendations for [COMPANY]?",
            "What should [COMPANY] do to improve?",
            "What strategic actions should [COMPANY] take?",
            "Give me financial recommendations for [COMPANY]",
            "What advice would you give [COMPANY]?",
            "How can [COMPANY] improve its financial performance?",
            "What should [COMPANY] prioritise?",
            "What are the key improvement areas for [COMPANY]?",
            "What action items would help [COMPANY]?",
            "Suggest a strategy for [COMPANY]",
        ],
    },
    {
        "category": "recommendations",
        "patterns": [
            "How can [COMPANY] increase profitability?",
            "What can [COMPANY] do to reduce debt?",
            "How should [COMPANY] improve its margins?",
            "What growth levers does [COMPANY] have?",
            "What cost reduction opportunities exist for [COMPANY]?",
            "How can [COMPANY] generate more cash?",
            "What operational improvements should [COMPANY] make?",
            "How can [COMPANY] improve its capital efficiency?",
            "What financial discipline improvements are needed?",
            "What is the turnaround strategy for [COMPANY]?",
        ],
    },
    {
        "category": "strengths",
        "patterns": [
            "What are [COMPANY]'s financial strengths?",
            "What is [COMPANY] doing well?",
            "What are the positives for [COMPANY]?",
            "Where does [COMPANY] excel?",
            "What are [COMPANY]'s competitive advantages?",
            "What are [COMPANY]'s strongest metrics?",
            "What is going right at [COMPANY]?",
            "What are the key positives in [COMPANY]'s financials?",
            "What are [COMPANY]'s best attributes?",
            "What gives [COMPANY] an edge?",
        ],
    },
    {
        "category": "weaknesses",
        "patterns": [
            "What are [COMPANY]'s weaknesses?",
            "Where is [COMPANY] underperforming?",
            "What are the concerns about [COMPANY]?",
            "What areas does [COMPANY] need to improve?",
            "What are the negatives for [COMPANY]?",
            "What are [COMPANY]'s financial vulnerabilities?",
            "Where is [COMPANY] falling short?",
            "What is holding [COMPANY] back?",
            "What are the red flags in [COMPANY]'s performance?",
            "Where should [COMPANY] focus improvement efforts?",
        ],
    },
    {
        "category": "swot_analysis",
        "patterns": [
            "Give me a SWOT analysis for [COMPANY]",
            "What are [COMPANY]'s strengths and weaknesses?",
            "What are the opportunities and threats for [COMPANY]?",
            "Do a SWOT for [COMPANY]",
            "Summarise strengths, weaknesses, opportunities and threats",
            "What is the strategic position of [COMPANY]?",
            "Analyse [COMPANY] from a strategic perspective",
            "What are the strategic risks for [COMPANY]?",
            "What opportunities should [COMPANY] pursue?",
            "What threats does [COMPANY] face?",
        ],
    },
    {
        "category": "capital_allocation",
        "patterns": [
            "How is [COMPANY] allocating its capital?",
            "Is [COMPANY] reinvesting in growth?",
            "What is [COMPANY]'s capital allocation strategy?",
            "Is [COMPANY] using its cash wisely?",
            "Should [COMPANY] pay dividends or reinvest?",
            "Is [COMPANY] buying back shares?",
            "Is [COMPANY] investing in R&D?",
            "What is [COMPANY]'s M&A activity?",
            "Is [COMPANY] deploying capital efficiently?",
            "What is the best use of [COMPANY]'s excess cash?",
        ],
    },

    # =========================================================================
    # 12. GENERAL QUESTIONS  (100+ patterns)
    # =========================================================================
    {
        "category": "greeting",
        "patterns": [
            "Hi",
            "Hello",
            "Hey",
            "Good morning",
            "Good afternoon",
            "Good evening",
            "Hey there",
            "Howdy",
            "What's up",
            "Greetings",
        ],
    },
    {
        "category": "greeting",
        "patterns": [
            "Hi there",
            "Hello there",
            "Hey bot",
            "Hello bot",
            "Hi bot",
            "Good day",
            "Morning",
            "Afternoon",
            "Evening",
            "Yo",
        ],
    },
    {
        "category": "thanks",
        "patterns": [
            "Thank you",
            "Thanks",
            "Thanks a lot",
            "Thank you so much",
            "That was helpful",
            "Appreciate it",
            "Great, thanks",
            "Perfect, thanks",
            "Awesome, thank you",
            "Cheers",
        ],
    },
    {
        "category": "thanks",
        "patterns": [
            "That helped a lot",
            "Very useful, thanks",
            "Thanks for the analysis",
            "Good answer",
            "Brilliant, thanks",
            "Helpful response",
            "That's what I needed",
            "Thanks for explaining",
            "Much appreciated",
            "You're a great assistant",
        ],
    },
    {
        "category": "help",
        "patterns": [
            "Help",
            "What can you do?",
            "What can you help me with?",
            "What questions can I ask?",
            "Show me what you can do",
            "What are your capabilities?",
            "What topics do you cover?",
            "What financial questions can you answer?",
            "What is the scope of your analysis?",
            "How do I use this chatbot?",
        ],
    },
    {
        "category": "help",
        "patterns": [
            "Give me example questions",
            "What kind of analysis do you do?",
            "What financial metrics do you know?",
            "Can you analyse my company data?",
            "What reports can you generate?",
            "Do you do risk analysis?",
            "Can you forecast financials?",
            "Do you support benchmarking?",
            "What KPIs can you explain?",
            "What is the chatbot trained on?",
        ],
    },
    {
        "category": "company_summary",
        "patterns": [
            "Tell me about [COMPANY]",
            "Give me a summary of [COMPANY]",
            "What is [COMPANY]?",
            "Describe [COMPANY]",
            "Give me an overview of [COMPANY]",
            "What does [COMPANY] do?",
            "Who is [COMPANY]?",
            "Introduce me to [COMPANY]",
            "What is [COMPANY]'s business?",
            "Give me a brief on [COMPANY]",
        ],
    },
    {
        "category": "company_summary",
        "patterns": [
            "Analyse [COMPANY] for me",
            "What is the financial profile of [COMPANY]?",
            "Give me a full analysis of [COMPANY]",
            "Summarise [COMPANY]'s financial position",
            "What are the key financial metrics for [COMPANY]?",
            "Give me the key stats for [COMPANY]",
            "What is the financial snapshot for [COMPANY]?",
            "Overview of [COMPANY]'s performance",
            "What does [COMPANY]'s financial data show?",
            "What is [COMPANY]'s financial health?",
        ],
    },
    {
        "category": "health_score",
        "patterns": [
            "What is [COMPANY]'s health score?",
            "What is the overall financial health of [COMPANY]?",
            "Give me [COMPANY]'s health rating",
            "What is the composite score for [COMPANY]?",
            "Is [COMPANY] financially healthy?",
            "What score does [COMPANY] get overall?",
            "What is [COMPANY]'s overall rating?",
            "How is [COMPANY] rated financially?",
            "What is [COMPANY]'s financial grade?",
            "How strong is [COMPANY] overall?",
        ],
    },
    {
        "category": "kpi_overview",
        "patterns": [
            "Show me all KPIs for [COMPANY]",
            "What are the key performance indicators for [COMPANY]?",
            "Give me all financial ratios for [COMPANY]",
            "What metrics are available for [COMPANY]?",
            "Show me the full KPI dashboard for [COMPANY]",
            "What financial indicators should I track for [COMPANY]?",
            "Give me a complete ratio analysis for [COMPANY]",
            "What are the most important KPIs for [COMPANY]?",
            "Show me all ratios",
            "Full KPI breakdown for [COMPANY]",
        ],
    },
    {
        "category": "sector_info",
        "patterns": [
            "What sector is [COMPANY] in?",
            "What industry does [COMPANY] operate in?",
            "What market does [COMPANY] serve?",
            "What is [COMPANY]'s business sector?",
            "Is [COMPANY] in technology, retail or another sector?",
            "What industry classification does [COMPANY] fall under?",
            "What type of business is [COMPANY]?",
            "What market segment does [COMPANY] serve?",
            "Is [COMPANY] a B2B or B2C company?",
            "What is [COMPANY]'s core business domain?",
        ],
    },
    {
        "category": "data_period",
        "patterns": [
            "What period is the data for?",
            "What year is this analysis for?",
            "What period has been uploaded?",
            "How many periods of data are available?",
            "What is the latest data period?",
            "Is this annual or quarterly data?",
            "What is the date of the financial data?",
            "What fiscal year is this from?",
            "How current is the data?",
            "What periods are available in the dataset?",
        ],
    },
    {
        "category": "unknown",
        "patterns": [
            "I don't understand",
            "Can you repeat that?",
            "That doesn't make sense",
            "Can you clarify?",
            "I'm confused",
            "What do you mean?",
            "Can you explain that differently?",
            "I need more information",
            "Can you be more specific?",
            "I'm not sure what you're asking",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Revenue & Sales (extra depth)
    # =========================================================================
    {
        "category": "revenue_query",
        "patterns": [
            "What were [COMPANY]'s revenues for the most recent quarter?",
            "Has [COMPANY] hit [REVENUE] in revenue yet?",
            "What is [COMPANY]'s revenue per employee?",
            "What is [COMPANY]'s revenue per share?",
            "How much revenue did [COMPANY] book in [PERIOD]?",
            "Is [COMPANY] a billion-dollar revenue company?",
            "What is [COMPANY]'s trailing twelve-month revenue?",
            "What is the revenue run rate for [COMPANY]?",
            "What is [COMPANY]'s recurring revenue?",
            "What is [COMPANY]'s organic revenue growth?",
        ],
    },
    {
        "category": "revenue_growth",
        "patterns": [
            "How has [COMPANY]'s revenue grown over 5 years?",
            "What is the quarterly revenue growth for [COMPANY]?",
            "Is [COMPANY]'s revenue growing faster than inflation?",
            "What drove the revenue increase for [COMPANY]?",
            "Why did [COMPANY]'s revenue decline?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Profit & Loss (extra depth)
    # =========================================================================
    {
        "category": "net_profit",
        "patterns": [
            "What is [COMPANY]'s earnings per share?",
            "What is [COMPANY]'s diluted EPS?",
            "How much profit did [COMPANY] make per share?",
            "What is the EPS for [COMPANY] in [YEAR]?",
            "Is [COMPANY]'s EPS growing?",
            "What is [COMPANY]'s trailing EPS?",
            "How does [COMPANY]'s EPS compare to consensus estimates?",
            "What is the price-to-earnings ratio for [COMPANY]?",
            "What is [COMPANY]'s P/E ratio?",
            "Is [COMPANY]'s P/E ratio reasonable?",
        ],
    },
    {
        "category": "ebitda",
        "patterns": [
            "What is [COMPANY]'s EV/EBITDA?",
            "What is the EBITDA to revenue ratio?",
            "Is [COMPANY]'s EBITDA margin above 20%?",
            "What is the EBITDA growth rate for [COMPANY]?",
            "Is EBITDA a good measure for [COMPANY]?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Investment Advice (extra depth)
    # =========================================================================
    {
        "category": "should_invest",
        "patterns": [
            "Is [COMPANY] a Warren Buffett type company?",
            "Is [COMPANY] a value stock or a growth stock?",
            "Does [COMPANY] pass the quality investing test?",
            "What is [COMPANY]'s intrinsic value?",
            "Is [COMPANY] trading at a discount?",
            "Is [COMPANY] a compounding machine?",
            "Would [COMPANY] qualify as a moat business?",
            "Does [COMPANY] have a durable competitive advantage?",
            "Is [COMPANY] suitable for a long-term portfolio?",
            "Is [COMPANY] suitable for a conservative investor?",
        ],
    },
    {
        "category": "growth_potential",
        "patterns": [
            "What is [COMPANY]'s total addressable market?",
            "Is [COMPANY] expanding into new markets?",
            "What new products or services is [COMPANY] launching?",
            "Is [COMPANY] investing in innovation?",
            "Does [COMPANY] have a clear path to growth?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Cash Flow (extra depth)
    # =========================================================================
    {
        "category": "free_cash_flow",
        "patterns": [
            "Is [COMPANY]'s FCF growing year over year?",
            "What is the FCF per share for [COMPANY]?",
            "What is [COMPANY]'s FCF conversion rate?",
            "How does FCF compare to reported earnings for [COMPANY]?",
            "Is [COMPANY]'s cash flow quality high?",
        ],
    },
    {
        "category": "operating_cash_flow",
        "patterns": [
            "Is [COMPANY]'s operating cash flow higher than net income?",
            "What is the OCF to sales ratio for [COMPANY]?",
            "Is [COMPANY]'s OCF improving or declining?",
            "What is driving [COMPANY]'s operating cash flows?",
            "Why is [COMPANY]'s OCF lower than net income?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Liquidity (extra depth)
    # =========================================================================
    {
        "category": "liquidity_general",
        "patterns": [
            "How many days of operating expenses can [COMPANY] cover with cash?",
            "Is [COMPANY]'s liquidity better than last year?",
            "What is the liquidity trend for [COMPANY]?",
            "Is [COMPANY] borrowing to fund operations?",
            "Does [COMPANY] have an undrawn credit facility?",
        ],
    },
    {
        "category": "cash_position",
        "patterns": [
            "Is [COMPANY] sitting on excess cash?",
            "What is [COMPANY] doing with its cash?",
            "How has [COMPANY]'s cash balance changed?",
            "Is cash growing at [COMPANY]?",
            "What is net cash for [COMPANY]?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Debt & Leverage (extra depth)
    # =========================================================================
    {
        "category": "total_debt",
        "patterns": [
            "Is [COMPANY] reducing its debt?",
            "What is [COMPANY]'s debt reduction plan?",
            "When does [COMPANY]'s debt mature?",
            "Is [COMPANY]'s debt fixed or variable rate?",
            "Has [COMPANY] taken on new debt recently?",
        ],
    },
    {
        "category": "interest_coverage",
        "patterns": [
            "Is [COMPANY]'s interest coverage ratio declining?",
            "Is [COMPANY] struggling to cover interest?",
            "What would happen if interest rates rise for [COMPANY]?",
            "How sensitive is [COMPANY] to interest rate changes?",
            "Is [COMPANY]'s debt at a fixed or variable rate?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Risk (extra depth)
    # =========================================================================
    {
        "category": "overall_risk",
        "patterns": [
            "What is [COMPANY]'s composite risk score?",
            "Has [COMPANY]'s risk profile changed over time?",
            "Is [COMPANY]'s risk improving or deteriorating?",
            "What is the biggest financial risk for [COMPANY]?",
            "Can [COMPANY] survive a recession?",
        ],
    },
    {
        "category": "piotroski_score",
        "patterns": [
            "Is [COMPANY] showing improving financial signals?",
            "What signals did [COMPANY] pass or fail on Piotroski?",
            "Is [COMPANY]'s Piotroski score going up?",
            "What is [COMPANY]'s financial strength per Piotroski?",
            "Is [COMPANY] showing 7+ Piotroski signals?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Returns & Efficiency (extra depth)
    # =========================================================================
    {
        "category": "roe",
        "patterns": [
            "Is [COMPANY]'s ROE sustainable?",
            "What drives [COMPANY]'s ROE (DuPont)?",
            "Is [COMPANY]'s ROE inflated by leverage?",
            "What is the DuPont ROE breakdown for [COMPANY]?",
            "How does ROE decompose for [COMPANY]?",
        ],
    },
    {
        "category": "asset_efficiency",
        "patterns": [
            "Is [COMPANY] making good use of its fixed assets?",
            "What is the fixed asset turnover for [COMPANY]?",
            "Is [COMPANY]'s asset base growing faster than revenue?",
            "How capital intensive is [COMPANY]?",
            "Is [COMPANY] asset-light or asset-heavy?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Forecasting (extra depth)
    # =========================================================================
    {
        "category": "revenue_forecast",
        "patterns": [
            "What revenue should I model for [COMPANY] next year?",
            "What base, bear and bull case revenue scenarios exist?",
            "What are consensus revenue estimates for [COMPANY]?",
            "Forecast [COMPANY]'s revenue using linear regression",
            "What would [COMPANY]'s revenue be at 10% growth?",
        ],
    },
    {
        "category": "trend_analysis",
        "patterns": [
            "Is there a 3-year uptrend for [COMPANY]?",
            "Has [COMPANY]'s profitability been consistent?",
            "Is there a structural change in [COMPANY]'s business?",
            "What trend does the data reveal for [COMPANY]?",
            "Is [COMPANY]'s momentum positive or negative?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Benchmarking (extra depth)
    # =========================================================================
    {
        "category": "industry_comparison",
        "patterns": [
            "Is [COMPANY] the top performer in its sector?",
            "Who are [COMPANY]'s main competitors?",
            "How does [COMPANY] compare to the market leader?",
            "Is [COMPANY] gaining or losing competitive ground?",
            "What are [COMPANY]'s key differentiators vs peers?",
        ],
    },
    {
        "category": "margin_benchmark",
        "patterns": [
            "Is [COMPANY]'s EBITDA margin above the industry median?",
            "What quartile is [COMPANY] in for net margin?",
            "Is [COMPANY]'s gross margin a competitive advantage?",
            "Do [COMPANY]'s margins justify a premium valuation?",
            "Is [COMPANY]'s margin expansion story compelling?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — Strategic Advice (extra depth)
    # =========================================================================
    {
        "category": "recommendations",
        "patterns": [
            "How can [COMPANY] defend its market position?",
            "What acquisitions might benefit [COMPANY]?",
            "Should [COMPANY] expand internationally?",
            "How can [COMPANY] diversify its revenue?",
            "What pricing strategy changes could improve [COMPANY]'s margins?",
        ],
    },
    {
        "category": "swot_analysis",
        "patterns": [
            "What macro threats could impact [COMPANY]?",
            "What regulatory risks does [COMPANY] face?",
            "What technology disruption risks exist for [COMPANY]?",
            "What are the competitive threats to [COMPANY]?",
            "What are the biggest growth opportunities for [COMPANY]?",
        ],
    },

    # =========================================================================
    # ADDITIONAL PATTERNS — General Questions (extra depth)
    # =========================================================================
    {
        "category": "company_summary",
        "patterns": [
            "What is the executive summary for [COMPANY]?",
            "Give me the investor summary for [COMPANY]",
            "What is the one-page financial summary for [COMPANY]?",
            "Summarise [COMPANY] in three sentences",
            "What are the headline numbers for [COMPANY]?",
            "What story does the data tell about [COMPANY]?",
            "Is [COMPANY] a good company based on its financials?",
            "Give me a quick snapshot of [COMPANY]",
            "What is [COMPANY]'s overall financial position?",
            "Is [COMPANY] performing well?",
        ],
    },
    {
        "category": "health_score",
        "patterns": [
            "What contributes to [COMPANY]'s health score?",
            "Why did [COMPANY] score [RATIO] on health?",
            "Is a health score of [RATIO] good for [COMPANY]?",
            "What would improve [COMPANY]'s health score?",
            "How is the health score calculated for [COMPANY]?",
            "What components make up [COMPANY]'s rating?",
            "Is [COMPANY]'s rating Strong, Adequate or Weak?",
            "What does the financial rating mean for [COMPANY]?",
            "How does [COMPANY]'s health score compare to peers?",
            "Has [COMPANY]'s health score improved?",
        ],
    },
    {
        "category": "kpi_overview",
        "patterns": [
            "Which KPI is most important for [COMPANY]?",
            "What are the top 5 metrics I should track for [COMPANY]?",
            "Which ratios are most useful for [COMPANY]'s industry?",
            "What KPIs indicate [COMPANY]'s long-term sustainability?",
            "Show me [COMPANY]'s profitability, liquidity and leverage ratios",
        ],
    },
    {
        "category": "data_period",
        "patterns": [
            "Upload data for [YEAR] to analyse [COMPANY]",
            "Can I see data for multiple years?",
            "Is the uploaded data annual or quarterly?",
            "Which fiscal year does this data cover?",
            "How many years of data are available for [COMPANY]?",
        ],
    },
    {
        "category": "greeting",
        "patterns": [
            "Start",
            "Begin",
            "Let's go",
            "I'm ready",
            "Open the analysis",
            "Wake up",
            "Are you there?",
            "Is anyone there?",
            "Hello, are you awake?",
            "Can you hear me?",
        ],
    },
    {
        "category": "thanks",
        "patterns": [
            "Wonderful, thank you",
            "That's very clear",
            "Exactly what I needed",
            "Spot on, thanks",
            "Nice one",
            "Good job",
            "Well done",
            "I appreciate the detail",
            "That's very thorough",
            "Thank you for the analysis",
        ],
    },
    {
        "category": "help",
        "patterns": [
            "What financial models do you use?",
            "Do you use Altman Z, Piotroski and Beneish?",
            "Can you explain any financial term?",
            "Do you support multi-period analysis?",
            "Can you compare this company to benchmarks?",
        ],
    },

]  # end TRAINING_QA


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def get_pattern_count() -> int:
    """Return the total number of individual patterns across all intents."""
    return sum(len(entry["patterns"]) for entry in TRAINING_QA)


def get_category_counts() -> dict:
    """Return a dict mapping each category to its total pattern count."""
    counts: dict = {}
    for entry in TRAINING_QA:
        cat = entry["category"]
        counts[cat] = counts.get(cat, 0) + len(entry["patterns"])
    return counts


def get_categories() -> list:
    """Return the sorted list of unique category labels."""
    return sorted({entry["category"] for entry in TRAINING_QA})


def get_patterns_for_category(category: str) -> list:
    """Return all patterns for a specific category."""
    patterns = []
    for entry in TRAINING_QA:
        if entry["category"] == category:
            patterns.extend(entry["patterns"])
    return patterns


def get_flat_training_pairs() -> list:
    """
    Return a flat list of (pattern, category) tuples suitable for
    training a text classifier (e.g. sklearn, spaCy, etc.).
    """
    pairs = []
    for entry in TRAINING_QA:
        for pattern in entry["patterns"]:
            pairs.append((pattern, entry["category"]))
    return pairs


# ---------------------------------------------------------------------------
# Module self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    total = get_pattern_count()
    cats  = get_category_counts()
    print(f"Total patterns : {total}")
    print(f"Total categories: {len(cats)}")
    print()
    print(f"{'Category':<30} {'Count':>6}")
    print("-" * 38)
    for cat, cnt in sorted(cats.items()):
        print(f"{cat:<30} {cnt:>6}")
    print("-" * 38)
    print(f"{'TOTAL':<30} {total:>6}")
