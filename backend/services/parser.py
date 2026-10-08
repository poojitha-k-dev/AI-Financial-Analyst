"""
Financial document parser.
Supports: PDF, CSV, Excel (.xlsx/.xls)
Extracts raw financial data and normalises into a standard dict.
"""
import io
import re
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import pdfplumber


# ─── field aliases ────────────────────────────────────────────────────────────
FIELD_ALIASES: Dict[str, list] = {
    # Income Statement
    "revenue": ["revenue", "total revenue", "net sales", "net revenue", "sales"],
    "cost_of_goods_sold": ["cost of goods sold", "cogs", "cost of revenue", "cost of sales"],
    "gross_profit": ["gross profit", "gross income"],
    "operating_expenses": ["operating expenses", "opex", "total operating expenses"],
    "operating_income": ["operating income", "operating profit", "ebit", "income from operations"],
    "ebitda": ["ebitda"],
    "interest_expense": ["interest expense", "interest charges"],
    "income_before_tax": ["income before tax", "pretax income", "earnings before tax"],
    "income_tax": ["income tax", "tax expense", "provision for taxes"],
    "net_income": ["net income", "net profit", "net earnings", "profit after tax", "profit after tax and minority interest", "pat", "net profit after tax"],
    "gross_profit": ["gross profit", "gross income", "gross margin amount"],
    "operating_income": ["operating income", "operating profit", "ebit", "income from operations", "profit before interest and tax", "pbit"],
    "total_equity": ["total equity", "shareholders equity", "stockholders equity", "total stockholders equity", "net worth", "owners equity"],
    "total_assets": ["total assets", "total asset"],
    "total_liabilities": ["total liabilities", "total liability"],
    "revenue": ["revenue", "total revenue", "net sales", "net revenue", "sales", "turnover", "total turnover", "income from operations"],
    "cost_of_goods_sold": ["cost of goods sold", "cogs", "cost of revenue", "cost of sales", "cost of production", "material costs"],
    "operating_expenses": ["operating expenses", "opex", "total operating expenses", "total expenses"],
    "interest_expense": ["interest expense", "interest charges", "finance costs", "finance charges"],
    "income_tax": ["income tax", "tax expense", "provision for taxes", "tax", "taxation"],
    "cash_and_equivalents": ["cash and cash equivalents", "cash & equivalents", "cash"],
    "accounts_receivable": ["accounts receivable", "trade receivables"],
    "inventory": ["inventory", "inventories"],
    "total_current_assets": ["total current assets", "current assets"],
    "total_assets": ["total assets"],
    "accounts_payable": ["accounts payable", "trade payables"],
    "short_term_debt": ["short-term debt", "short term borrowings", "current portion of long-term debt"],
    "total_current_liabilities": ["total current liabilities", "current liabilities"],
    "long_term_debt": ["long-term debt", "long term debt", "long-term borrowings"],
    "total_liabilities": ["total liabilities"],
    "total_equity": ["total equity", "shareholders equity", "stockholders equity", "total stockholders equity"],
    "total_debt": ["total debt"],
    # Cash Flow
    "operating_cash_flow": ["operating cash flow", "cash from operations", "net cash from operating activities"],
    "capex": ["capital expenditures", "capex", "purchases of property plant and equipment", "ppe purchases"],
    "investing_cash_flow": ["investing activities", "cash from investing", "net cash from investing activities"],
    "financing_cash_flow": ["financing activities", "cash from financing", "net cash from financing activities"],
    "free_cash_flow": ["free cash flow", "fcf"],
    "dividends_paid": ["dividends paid", "dividends"],
}


def _normalise_key(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower().strip())


def _match_field(label: str) -> Optional[str]:
    norm = _normalise_key(label)
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in norm or norm in alias:
                return field
    return None


# ─── PDF parser ───────────────────────────────────────────────────────────────
def parse_pdf(file_bytes: bytes) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    text_lines = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # Try tables first
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) >= 2:
                        label = str(row[0] or "").strip()
                        # Take the last numeric value in the row
                        for cell in reversed(row[1:]):
                            val = _parse_numeric(str(cell or ""))
                            if val is not None:
                                field = _match_field(label)
                                if field and field not in data:
                                    data[field] = val
                                break

            # Fallback: plain text lines
            text = page.extract_text() or ""
            text_lines.extend(text.split("\n"))

    # Parse key-value pairs from text
    for line in text_lines:
        parts = re.split(r"\s{2,}|\t", line)
        if len(parts) >= 2:
            label = parts[0].strip()
            for part in reversed(parts[1:]):
                val = _parse_numeric(part)
                if val is not None:
                    field = _match_field(label)
                    if field and field not in data:
                        data[field] = val
                    break

    return data


# ─── CSV / Excel parser ────────────────────────────────────────────────────────
def parse_spreadsheet(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Could not read file: {e}")

    if df.empty:
        return {}

    data: Dict[str, Any] = {}

    # Detect if header row looks like periods (years / quarters)
    # e.g. columns: Metric | 2021 | 2022 | 2023
    def _looks_like_period(col_name: str) -> bool:
        s = str(col_name).strip()
        return bool(re.match(r'^(19|20)\d{2}', s) or
                    re.match(r'^Q[1-4]', s, re.I) or
                    re.match(r'^\d{4}-?(FY|Q[1-4]|H[12])', s, re.I))

    # Format 1: two-column (label, value) — exactly 2 cols
    if df.shape[1] == 2:
        for _, row in df.iterrows():
            label = str(row.iloc[0])
            val = _parse_numeric(str(row.iloc[1]))
            if val is not None:
                field = _match_field(label)
                if field and field not in data:
                    data[field] = val
        return data

    # Format 2: columns are periods, rows are line items (3+ cols)
    if df.shape[1] >= 3:
        label_col = df.columns[0]
        period_cols = df.columns[1:]

        # Use the last period column (most recent)
        value_col = period_cols[-1]
        for _, row in df.iterrows():
            label = str(row[label_col])
            val = _parse_numeric(str(row[value_col]))
            if val is not None:
                field = _match_field(label)
                if field and field not in data:
                    data[field] = val

        # Multi-period dict
        multi: Dict[str, Dict] = {}
        for col in period_cols:
            col_str = str(col).strip()
            period_data: Dict[str, Any] = {}
            for _, row in df.iterrows():
                label = str(row[label_col])
                val = _parse_numeric(str(row[col]))
                if val is not None:
                    field = _match_field(label)
                    if field:
                        period_data[field] = val
            if period_data:
                multi[col_str] = period_data

        if multi:
            data["__multi_period__"] = multi

        return data

    # Format 3: wide format — rows are periods, columns are metrics
    # Detect if first column looks like dates/periods
    first_col_vals = df.iloc[:, 0].astype(str).tolist()
    if any(_looks_like_period(v) for v in first_col_vals):
        # Transpose: use most recent row
        latest_row = df.iloc[-1]
        for col in df.columns[1:]:
            val = _parse_numeric(str(latest_row[col]))
            if val is not None:
                field = _match_field(str(col))
                if field and field not in data:
                    data[field] = val
        return data

    return data


# ─── Unified entry point ───────────────────────────────────────────────────────
def parse_financial_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext in (".csv", ".xlsx", ".xls"):
        return parse_spreadsheet(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _parse_numeric(text: str) -> Optional[float]:
    """Convert strings like '1,234.56', '(1234)', '1.2B', '3.4M' to float."""
    text = text.strip().replace(",", "").replace("$", "").replace("%", "")
    # Handle parentheses as negatives
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    # Handle suffixes
    multipliers = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}
    if text and text[-1].lower() in multipliers:
        mult = multipliers[text[-1].lower()]
        text = text[:-1]
        try:
            return float(text) * mult
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None
