from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.models.company import Company, FinancialStatement
from backend.models.user import User
from backend.services.auth_service import get_current_active_user

router = APIRouter(prefix="/companies", tags=["Companies"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class CompanyCreate(BaseModel):
    name: str
    ticker: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    currency: str = "USD"
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    ticker: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    ticker: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    currency: str
    description: Optional[str]
    website: Optional[str]
    statement_count: int = 0
    latest_period: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/", response_model=CompanyOut, status_code=201)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = Company(**payload.model_dump(), owner_id=current_user.id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return _enrich(company, db)


@router.get("/", response_model=List[CompanyOut])
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Company).filter(Company.owner_id == current_user.id)
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))
    if sector:
        query = query.filter(Company.sector == sector)
    companies = query.order_by(Company.created_at.desc()).offset(skip).limit(limit).all()
    return [_enrich(c, db) for c in companies]


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_owned(company_id, db, current_user)
    return _enrich(company, db)


@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_owned(company_id, db, current_user)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return _enrich(company, db)


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_owned(company_id, db, current_user)
    db.delete(company)
    db.commit()


@router.get("/{company_id}/statements")
def get_statements(
    company_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_owned(company_id, db, current_user)   # auth check
    stmts = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.desc())
        .offset(skip).limit(limit)
        .all()
    )
    return [
        {
            "id": s.id,
            "period": s.period,
            "period_type": s.period_type,
            "statement_type": s.statement_type,
            "revenue": s.revenue,
            "net_income": s.net_income,
            "gross_profit": s.gross_profit,
            "total_assets": s.total_assets,
            "total_equity": s.total_equity,
            "free_cash_flow": s.free_cash_flow,
            "computed_kpis": s.computed_kpis,
            "created_at": str(s.created_at),
        }
        for s in stmts
    ]


@router.delete("/{company_id}/statements/{stmt_id}", status_code=204)
def delete_statement(
    company_id: int,
    stmt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_owned(company_id, db, current_user)
    stmt = db.query(FinancialStatement).filter(
        FinancialStatement.id == stmt_id,
        FinancialStatement.company_id == company_id,
    ).first()
    if not stmt:
        raise HTTPException(404, "Statement not found")
    db.delete(stmt)
    db.commit()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_owned(company_id: int, db: Session, user: User) -> Company:
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == user.id,
    ).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


def _enrich(company: Company, db: Session) -> CompanyOut:
    count = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company.id
    ).count()
    latest_row = (
        db.query(FinancialStatement.period)
        .filter(FinancialStatement.company_id == company.id)
        .order_by(FinancialStatement.period.desc())
        .first()
    )
    latest_period = latest_row[0] if latest_row else None
    return CompanyOut(
        id=company.id,
        name=company.name,
        ticker=company.ticker,
        sector=company.sector,
        industry=company.industry,
        country=company.country,
        currency=company.currency,
        description=company.description,
        website=company.website,
        statement_count=count,
        latest_period=latest_period,
        created_at=str(company.created_at),
    )
