import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.company import Company, FinancialStatement
from backend.models.user import User
from backend.services.auth_service import get_current_active_user
from backend.services.parser import parse_financial_document
from backend.services.kpi_engine import calculate_kpis
from backend.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls"}


@router.post("/statement")
async def upload_financial_statement(
    file: UploadFile = File(...),
    company_id: int = Form(...),
    period: str = Form(...),
    period_type: str = Form("annual"),
    statement_type: str = Form("combined"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Auth: user must own this company
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(404, "Company not found")

    content = await file.read()

    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb}MB limit")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Use: {', '.join(ALLOWED_EXTENSIONS)}")

    # Save file
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.upload_dir, unique_name)
    with open(save_path, "wb") as f:
        f.write(content)

    # Parse
    try:
        parsed_data = parse_financial_document(content, file.filename or "file" + ext)
    except Exception as e:
        os.remove(save_path)
        raise HTTPException(422, f"Parse failed: {str(e)}")

    if not parsed_data:
        os.remove(save_path)
        raise HTTPException(422, "No financial data could be extracted from this file")

    # Prior period for growth KPIs
    prior_stmt = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.period_type == period_type,
        )
        .order_by(FinancialStatement.period.desc())
        .first()
    )
    prior_data = prior_stmt.raw_data if prior_stmt else None

    kpis = calculate_kpis(parsed_data, prior_data)
    multi_period = parsed_data.pop("__multi_period__", None)

    def _make_stmt(cid, p, pt, st, data, k, path=None):
        return FinancialStatement(
            company_id=cid, period=p, period_type=pt, statement_type=st,
            raw_data=data, computed_kpis=k,
            revenue=data.get("revenue"),
            cost_of_goods_sold=data.get("cost_of_goods_sold"),
            gross_profit=data.get("gross_profit"),
            operating_income=data.get("operating_income"),
            net_income=data.get("net_income"),
            ebitda=data.get("ebitda"),
            interest_expense=data.get("interest_expense"),
            income_before_tax=data.get("income_before_tax"),
            income_tax=data.get("income_tax"),
            total_assets=data.get("total_assets"),
            total_liabilities=data.get("total_liabilities"),
            total_equity=data.get("total_equity"),
            cash_and_equivalents=data.get("cash_and_equivalents"),
            accounts_receivable=data.get("accounts_receivable"),
            inventory=data.get("inventory"),
            total_current_assets=data.get("total_current_assets"),
            total_current_liabilities=data.get("total_current_liabilities"),
            short_term_debt=data.get("short_term_debt"),
            long_term_debt=data.get("long_term_debt"),
            total_debt=data.get("total_debt"),
            accounts_payable=data.get("accounts_payable"),
            operating_cash_flow=data.get("operating_cash_flow"),
            capex=data.get("capex"),
            free_cash_flow=data.get("free_cash_flow"),
            investing_cash_flow=data.get("investing_cash_flow"),
            financing_cash_flow=data.get("financing_cash_flow"),
            dividends_paid=data.get("dividends_paid"),
            file_path=path,
        )

    stmt = _make_stmt(company_id, period, period_type, statement_type, parsed_data, kpis, save_path)
    db.add(stmt)

    imported_periods = [period]
    if multi_period:
        for p_label, p_data in multi_period.items():
            if str(p_label) == period:
                continue
            exists = db.query(FinancialStatement).filter(
                FinancialStatement.company_id == company_id,
                FinancialStatement.period == str(p_label),
            ).first()
            if not exists:
                p_kpis = calculate_kpis(p_data)
                db.add(_make_stmt(company_id, str(p_label), period_type, statement_type, p_data, p_kpis))
                imported_periods.append(str(p_label))

    db.commit()
    db.refresh(stmt)

    return {
        "message": "Statement uploaded and parsed successfully",
        "statement_id": stmt.id,
        "fields_extracted": len(parsed_data),
        "kpis_calculated": sum(len(v) for v in kpis.values() if isinstance(v, dict)),
        "periods_imported": imported_periods,
        "preview": {
            "revenue": parsed_data.get("revenue"),
            "net_income": parsed_data.get("net_income"),
            "total_assets": parsed_data.get("total_assets"),
            "gross_margin": kpis.get("profitability", {}).get("gross_margin"),
            "net_margin": kpis.get("profitability", {}).get("net_margin"),
            "current_ratio": kpis.get("liquidity", {}).get("current_ratio"),
        },
    }
