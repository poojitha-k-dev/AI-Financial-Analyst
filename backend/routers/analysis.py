import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.company import Company, FinancialStatement
from backend.models.report import AnalysisReport
from backend.models.user import User
from backend.services.auth_service import get_current_active_user
from backend.services.kpi_engine import calculate_kpis
from backend.services.risk_engine import analyse_risk
from backend.services.forecasting import forecast_metrics, build_historical_series
from backend.services.llm_service import (
    generate_financial_insights,
    generate_risk_narrative,
    generate_forecast_narrative,
    generate_executive_summary,
)
from backend.services.report_generator import generate_pdf_report, generate_excel_report
from backend.services.benchmarks import get_industry_benchmarks
from backend.config import settings

router = APIRouter(prefix="/analysis", tags=["Analysis"])


def _get_company(company_id: int, db: Session, user: User) -> Company:
    co = db.query(Company).filter(
        Company.id == company_id, Company.owner_id == user.id
    ).first()
    if not co:
        raise HTTPException(404, "Company not found")
    return co


@router.post("/{company_id}/full")
async def run_full_analysis(
    company_id: int,
    statement_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_company(company_id, db, current_user)

    query = db.query(FinancialStatement).filter(FinancialStatement.company_id == company_id)
    stmt = (
        query.filter(FinancialStatement.id == statement_id).first()
        if statement_id else
        query.order_by(FinancialStatement.period.desc()).first()
    )
    if not stmt:
        raise HTTPException(404, "No financial statements found. Upload data first.")

    prev_stmt = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.id != stmt.id,
        )
        .order_by(FinancialStatement.period.desc())
        .first()
    )

    current_data = stmt.raw_data or {}
    prev_data = prev_stmt.raw_data if prev_stmt else None

    kpis = calculate_kpis(current_data, prev_data)
    risk = analyse_risk(current_data, kpis, prev_data)

    all_stmts = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.asc())
        .all()
    )
    historical = [s.raw_data for s in all_stmts if s.raw_data]
    forecasts = {}
    if len(historical) >= 2:
        series = build_historical_series(historical)
        forecasts = forecast_metrics(series, periods_ahead=4)

    benchmarks = get_industry_benchmarks(company.sector)

    # AI narrative — optional, requires API key
    insights = ""
    exec_summary = ""
    try:
        insights = await generate_financial_insights(
            company_name=company.name,
            period=stmt.period,
            financial_data=current_data,
            kpis=kpis,
            risk_data=risk,
            benchmarks=benchmarks,
        )
        exec_summary = await generate_executive_summary(company.name, insights)
    except Exception:
        insights = "AI narrative unavailable — add an OpenAI or Gemini API key to your .env file to enable full AI analysis."
        exec_summary = f"Financial summary for {company.name} ({stmt.period}). Run with a valid API key for AI-generated insights."

    # Extract overall rating from insights
    rating = _extract_rating(insights)

    report = AnalysisReport(
        company_id=company_id,
        user_id=current_user.id,
        report_type="full",
        title=f"Full Analysis – {company.name} ({stmt.period})",
        content=insights,
        executive_summary=exec_summary,
        overall_rating=rating,
        kpis=kpis,
        risk_scores=risk,
        forecasts=forecasts,
        benchmarks=benchmarks,
        llm_provider=settings.llm_provider,
        model_used="gpt-4o" if settings.llm_provider == "openai" else "gemini-1.5-pro",
    )
    db.add(report)
    stmt.computed_kpis = kpis
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "company": company.name,
        "period": stmt.period,
        "kpis": kpis,
        "risk_analysis": risk,
        "forecasts": forecasts,
        "benchmarks": benchmarks,
        "insights": insights,
        "executive_summary": exec_summary,
        "overall_rating": rating,
    }


@router.get("/{company_id}/kpis")
def get_kpis(
    company_id: int,
    statement_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_company(company_id, db, current_user)
    query = db.query(FinancialStatement).filter(FinancialStatement.company_id == company_id)
    stmt = (
        query.filter(FinancialStatement.id == statement_id).first()
        if statement_id else
        query.order_by(FinancialStatement.period.desc()).first()
    )
    if not stmt:
        raise HTTPException(404, "Statement not found")

    kpis = stmt.computed_kpis or calculate_kpis(stmt.raw_data or {})
    return {"period": stmt.period, "kpis": kpis}


@router.get("/{company_id}/risk")
async def get_risk_analysis(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_company(company_id, db, current_user)
    stmt = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.desc()).first()
    )
    if not stmt:
        raise HTTPException(404, "No statements found")

    prev_stmt = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id, FinancialStatement.id != stmt.id)
        .order_by(FinancialStatement.period.desc()).first()
    )
    kpis = stmt.computed_kpis or calculate_kpis(stmt.raw_data or {})
    risk = analyse_risk(stmt.raw_data or {}, kpis, prev_stmt.raw_data if prev_stmt else None)

    # Narrative is optional — only attempt if API key is configured
    narrative = ""
    try:
        narrative = await generate_risk_narrative(company.name, risk, kpis)
    except Exception:
        narrative = "AI narrative unavailable — add an OpenAI or Gemini API key to .env to enable."

    return {"risk_analysis": risk, "narrative": narrative, "period": stmt.period}


@router.get("/{company_id}/forecast")
async def get_forecast(
    company_id: int,
    periods: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_company(company_id, db, current_user)
    all_stmts = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.asc()).all()
    )
    if len(all_stmts) < 2:
        raise HTTPException(400, "Need at least 2 periods of data for forecasting")

    historical = [s.raw_data for s in all_stmts if s.raw_data]
    series = build_historical_series(historical)
    forecasts = forecast_metrics(series, periods_ahead=periods)

    # Narrative is optional
    narrative = ""
    try:
        narrative = await generate_forecast_narrative(company.name, forecasts, historical)
    except Exception:
        narrative = "AI narrative unavailable — add an OpenAI or Gemini API key to .env to enable."

    return {"forecasts": forecasts, "periods_ahead": periods, "narrative": narrative}


@router.get("/{company_id}/reports")
def list_reports(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_company(company_id, db, current_user)
    reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.company_id == company_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "overall_rating": r.overall_rating,
            "executive_summary": r.executive_summary,
            "llm_provider": r.llm_provider,
            "is_pinned": r.is_pinned,
            "has_pdf": bool(r.pdf_path),
            "has_excel": bool(r.excel_path),
            "created_at": str(r.created_at),
        }
        for r in reports
    ]


@router.post("/{company_id}/export/pdf")
async def export_pdf(
    company_id: int,
    report_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_company(company_id, db, current_user)
    stmt = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.desc()).first()
    )
    if not stmt:
        raise HTTPException(404, "No statements found")

    report = (
        db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
        if report_id else
        db.query(AnalysisReport)
        .filter(AnalysisReport.company_id == company_id)
        .order_by(AnalysisReport.created_at.desc()).first()
    )

    output_path = os.path.join(
        settings.upload_dir, "reports", f"{uuid.uuid4().hex}_report.pdf"
    )
    generate_pdf_report(
        company_name=company.name,
        period=stmt.period,
        financial_data=stmt.raw_data or {},
        kpis=stmt.computed_kpis or {},
        risk_data=report.risk_scores if report else {},
        insights_text=report.content if report else "Run full analysis first.",
        output_path=output_path,
    )

    if report:
        report.pdf_path = output_path
        db.commit()

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"{company.name}_{stmt.period}_report.pdf",
    )


@router.post("/{company_id}/export/excel")
async def export_excel(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = _get_company(company_id, db, current_user)
    stmt = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.company_id == company_id)
        .order_by(FinancialStatement.period.desc()).first()
    )
    if not stmt:
        raise HTTPException(404, "No statements found")

    output_path = os.path.join(
        settings.upload_dir, "reports", f"{uuid.uuid4().hex}_report.xlsx"
    )
    generate_excel_report(
        company_name=company.name,
        period=stmt.period,
        financial_data=stmt.raw_data or {},
        kpis=stmt.computed_kpis or {},
        output_path=output_path,
    )

    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{company.name}_{stmt.period}_report.xlsx",
    )


def _extract_rating(insights: str) -> Optional[str]:
    ratings = ["Excellent", "Good", "Fair", "Weak", "Critical"]
    lower = insights.lower()
    for r in ratings:
        if r.lower() in lower:
            return r
    return None
