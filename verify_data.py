from backend.services.parser import parse_financial_document
from backend.services.kpi_engine import calculate_kpis

files = [
    ('data/sample/techcorp_financials.csv',  'TechCorp Solutions'),
    ('data/sample/retailmart_financials.csv','RetailMart Inc.'),
    ('data/sample/pharmaplus_financials.csv','PharmaPlus Ltd.'),
]

for fname, name in files:
    with open(fname, 'rb') as f:
        data = parse_financial_document(f.read(), fname.split('/')[-1])
    multi = data.pop('__multi_period__', {})
    kpis = calculate_kpis(data)
    pr   = kpis.get('profitability', {})
    liq  = kpis.get('liquidity', {})
    comp = kpis.get('composite_scores', {})

    rev = data.get('revenue', 0)
    ni  = data.get('net_income', 0)

    print(f"=== {name} ===")
    print(f"  Revenue:      ${rev:>20,.0f}")
    print(f"  Net Income:   ${ni:>20,.0f}")
    print(f"  Gross Margin: {pr.get('gross_margin')}%")
    print(f"  Net Margin:   {pr.get('net_margin')}%")
    print(f"  ROE:          {pr.get('return_on_equity')}%")
    print(f"  Current Ratio:{liq.get('current_ratio')}x")
    print(f"  Health Score: {comp.get('overall_health')}/10")
    print(f"  Periods:      {list(multi.keys())}")
    print()
