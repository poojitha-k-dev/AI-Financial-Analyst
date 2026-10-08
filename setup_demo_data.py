"""
Auto-creates 3 demo companies and uploads all financial data
for account: poojitha@adyapan.com
"""
import requests, sqlite3, json

BASE = "http://localhost:8000"

# ── Login ──────────────────────────────────────────────────────────────────────
r = requests.post(f"{BASE}/auth/login",
    data={"username": "poojitha@adyapan.com", "password": "Poojitha@123"})
if r.status_code != 200:
    print("Login failed:", r.json())
    exit(1)
token = r.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}
print(f"Logged in as poojitha@adyapan.com")

# ── Clear existing data ────────────────────────────────────────────────────────
conn = sqlite3.connect("financial_analyst.db")
cur  = conn.cursor()
user_id = cur.execute("SELECT id FROM users WHERE email=?",
    ("poojitha@adyapan.com",)).fetchone()[0]
old_companies = cur.execute("SELECT id FROM companies WHERE owner_id=?",
    (user_id,)).fetchall()
for (cid,) in old_companies:
    cur.execute("DELETE FROM financial_statements WHERE company_id=?", (cid,))
    cur.execute("DELETE FROM analysis_reports WHERE company_id=?", (cid,))
cur.execute("DELETE FROM companies WHERE owner_id=?", (user_id,))
conn.commit()
conn.close()
print("Cleared old data")

# ── Companies to create ────────────────────────────────────────────────────────
COMPANIES = [
    {
        "name":     "TechCorp Solutions",
        "ticker":   "TCS",
        "sector":   "Technology",
        "industry": "Software & Cloud Services",
        "country":  "United States",
        "currency": "USD",
        "description": "A leading enterprise software company specialising in cloud infrastructure and AI-powered analytics platforms.",
        "file":     "data/sample/techcorp_financials.csv",
    },
    {
        "name":     "RetailMart Inc.",
        "ticker":   "RMI",
        "sector":   "Consumer Discretionary",
        "industry": "General Merchandise Retail",
        "country":  "United States",
        "currency": "USD",
        "description": "Large-format retail chain operating 850+ stores across North America, facing margin pressure from e-commerce competition.",
        "file":     "data/sample/retailmart_financials.csv",
    },
    {
        "name":     "PharmaPlus Ltd.",
        "ticker":   "PPL",
        "sector":   "Healthcare",
        "industry": "Pharmaceuticals",
        "country":  "United Kingdom",
        "currency": "USD",
        "description": "Global pharmaceutical company with strong oncology and cardiovascular drug portfolio and robust R&D pipeline.",
        "file":     "data/sample/pharmaplus_financials.csv",
    },
]

for co in COMPANIES:
    # Create company
    payload = {k: v for k, v in co.items() if k != "file"}
    r = requests.post(f"{BASE}/companies/", json=payload, headers=H)
    if r.status_code not in (200, 201):
        print(f"Failed to create {co['name']}: {r.json()}")
        continue
    cid = r.json()["id"]
    print(f"\nCreated company: {co['name']} (ID {cid})")

    # Upload CSV
    with open(co["file"], "rb") as f:
        files = {"file": (co["file"].split("/")[-1], f, "text/csv")}
        data  = {
            "company_id":     str(cid),
            "period":         "2023-FY",
            "period_type":    "annual",
            "statement_type": "combined",
        }
        r2 = requests.post(f"{BASE}/upload/statement",
            headers=H, files=files, data=data)

    if r2.status_code == 200:
        res = r2.json()
        print(f"  Uploaded: {res['fields_extracted']} fields, "
              f"{res['kpis_calculated']} KPIs, "
              f"periods: {res['periods_imported']}")
        prev = res['preview']
        print(f"  Revenue: ${prev.get('revenue', 0):,.0f}  "
              f"Net Income: ${prev.get('net_income', 0):,.0f}  "
              f"Gross Margin: {prev.get('gross_margin', 0):.1f}%")
    else:
        print(f"  Upload failed: {r2.json()}")

print("\n=== Setup Complete ===")
print("Open http://localhost:5173 and log in with:")
print("  Email:    poojitha@adyapan.com")
print("  Password: Poojitha@123")
print()
print("You now have 3 companies with 4 years of data each:")
print("  1. TechCorp Solutions  — high growth tech, Health 8/10")
print("  2. RetailMart Inc.     — struggling retail, Health 2.6/10")
print("  3. PharmaPlus Ltd.     — strong pharma,    Health 8/10")
