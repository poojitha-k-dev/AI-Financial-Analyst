import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend.models.company import Company, FinancialStatement
from backend.models.report import ChatMessage, AnalysisReport
from backend.models.user import User
from backend.services.auth_service import get_current_active_user
from backend.services.llm_service import chat_with_financials
from backend.services.chatbot_engine import generate_response as chatbot_respond

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    company_id: Optional[int] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session_id = payload.session_id or str(uuid.uuid4())
    context = {}
    company_name = "FinanceAI Assistant"

    # Build context if a company is selected
    if payload.company_id:
        company = db.query(Company).filter(
            Company.id == payload.company_id,
            Company.owner_id == current_user.id,
        ).first()

        if company:
            company_name = company.name
            context["company_name"] = company.name
            context["sector"]       = company.sector or "General"
            context["industry"]     = company.industry or ""
            context["currency"]     = company.currency or "USD"

            all_stmts = (
                db.query(FinancialStatement)
                .filter(FinancialStatement.company_id == payload.company_id)
                .order_by(FinancialStatement.period.asc()).all()
            )
            stmt = all_stmts[-1] if all_stmts else None
            context["total_periods"] = len(all_stmts)

            if stmt:
                from backend.services.kpi_engine import calculate_kpis
                raw  = stmt.raw_data or {}
                kpis = stmt.computed_kpis or calculate_kpis(raw)
                context["financial_data"] = raw
                context["kpis"]           = kpis
                context["period"]         = stmt.period

            if len(all_stmts) >= 2:
                context["all_periods"] = [
                    {
                        "period":        s.period,
                        "revenue":       s.raw_data.get("revenue")       if s.raw_data else None,
                        "net_income":    s.raw_data.get("net_income")    if s.raw_data else None,
                        "free_cash_flow":s.raw_data.get("free_cash_flow")if s.raw_data else None,
                    }
                    for s in all_stmts
                ]

            report = (
                db.query(AnalysisReport)
                .filter(AnalysisReport.company_id == payload.company_id)
                .order_by(AnalysisReport.created_at.desc()).first()
            )
            if report:
                context["risk_scores"]       = report.risk_scores or {}
                context["overall_rating"]    = report.overall_rating
                context["executive_summary"] = report.executive_summary or ""

    # No financial data — use general advisor mode
    if not context.get("financial_data"):
        answer = _handle_general_question(payload.question, current_user.full_name)
        _save_messages(db, payload.company_id, current_user.id, session_id, payload.question, answer)
        return ChatResponse(answer=answer, session_id=session_id)

    # Has financial data — use full chatbot engine
    history = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == current_user.id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(20).all()
    )
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    answer = await chat_with_financials(
        question=payload.question,
        company_name=company_name,
        financial_context=context,
        chat_history=history_dicts,
    )
    if not answer or "unavailable" in answer.lower():
        answer = chatbot_respond(payload.question, company_name, context)

    _save_messages(db, payload.company_id, current_user.id, session_id, payload.question, answer)
    return ChatResponse(answer=answer, session_id=session_id)


def _save_messages(db, company_id, user_id, session_id, question, answer):
    db.add(ChatMessage(company_id=company_id, user_id=user_id,
        session_id=session_id, role="user", content=question))
    db.add(ChatMessage(company_id=company_id, user_id=user_id,
        session_id=session_id, role="assistant", content=answer))
    db.commit()


def _handle_general_question(question: str, user_name: str) -> str:
    """Answer questions even without uploaded company data."""
    try:
        from backend.services.chatbot_ml_trainer import predict_intent
        intent = predict_intent(question)
    except Exception:
        intent = "help"

    name = (user_name or "there").split()[0]
    q = question.lower()

    if intent == "greeting":
        return (
            f"Hello {name}! I'm your AI Financial Analyst.\n\n"
            "I can help you with:\n"
            "- Analysing company financials after you upload data\n"
            "- Personalised investment advice based on your numbers\n"
            "- Risk assessment using Altman Z, Piotroski F, Beneish M\n"
            "- Portfolio recommendations and growth strategies\n\n"
            "**To get started with personalised analysis:**\n"
            "1. Go to **Companies** in the sidebar → Add your company\n"
            "2. Go to **Upload Data** → Upload your CSV or Excel file\n"
            "3. Come back and ask me anything!\n\n"
            "You can also ask me general financial questions right now — no data needed!"
        )

    if intent == "thanks":
        return f"You're welcome, {name}! Upload your financial data to get personalised analysis."

    if intent == "help":
        return (
            f"Hi {name}! Here's what I can do:\n\n"
            "**With uploaded data (full power):**\n"
            "- Answer any question about your company's financials\n"
            "- Give personalised investment and portfolio advice\n"
            "- Run risk analysis (Altman Z, Piotroski F, Beneish M)\n"
            "- Show KPIs, margins, cash flow, debt levels\n"
            "- Compare against industry benchmarks\n\n"
            "**Right now (no data needed):**\n"
            "- Explain any financial concept\n"
            "- Teach you what KPIs to look for\n"
            "- Explain risk models\n"
            "- Give general investment principles\n\n"
            "**To get started:** Add a company → Upload data → Ask anything!"
        )

    if intent in ("should_invest", "where_invest", "growth_potential", "investment_risk", "personal_advice", "portfolio_advice"):
        return (
            f"**Investment Guidance for {name}:**\n\n"
            "To give personalised investment advice, I need your company's financial data.\n\n"
            "**How to get personalised advice:**\n"
            "1. Click **Companies** in the sidebar → Add your company\n"
            "2. Click **Upload Data** → Upload your CSV/Excel financial statement\n"
            "3. Ask me again — I'll analyse your exact numbers\n\n"
            "**General Investment Principles (while you set up):**\n"
            "- Gross margin above 40% = strong pricing power\n"
            "- Net margin above 10% = good profitability\n"
            "- Current ratio above 1.5 = healthy short-term liquidity\n"
            "- Debt/Equity below 1.0 = safe leverage level\n"
            "- ROE above 15% = strong returns to shareholders\n"
            "- Positive free cash flow = company generates real cash\n\n"
            "Upload your data and I'll give you specific numbers for your company!"
        )

    if intent in ("revenue", "net_profit", "gross_profit", "total_profit", "total_loss",
                  "kpi_overall", "health_score", "free_cash_flow", "cash_position"):
        return (
            f"Hi {name}! To show specific financial metrics, I need your data.\n\n"
            "**Upload your data in 2 steps:**\n"
            "1. Go to **Companies** → Add your company\n"
            "2. Go to **Upload Data** → Upload your financial statement CSV\n\n"
            "**Your CSV format:**\n"
            "```\nMetric,2021,2022,2023\n"
            "Revenue,5000000,6500000,8000000\n"
            "Net Income,500000,750000,1000000\n"
            "Total Assets,10000000,12000000,15000000\n"
            "Total Equity,6000000,7000000,8500000\n```\n\n"
            "Once uploaded, I'll give you specific numbers, charts, and advice!"
        )

    if intent in ("risk_overall", "altman_z", "piotroski", "beneish", "risk_flags"):
        return (
            f"**Risk Analysis Explained — {name}:**\n\n"
            "I use 3 academic models to assess financial risk:\n\n"
            "**Altman Z-Score** — Bankruptcy prediction\n"
            "- Above 2.99 = Safe Zone ✅\n"
            "- 1.81 to 2.99 = Grey Zone ⚠️\n"
            "- Below 1.81 = Distress Zone ❌\n\n"
            "**Piotroski F-Score** — Financial strength (0-9)\n"
            "- 7-9 = Financially strong ✅\n"
            "- 4-6 = Moderate strength ⚠️\n"
            "- 0-3 = Weak fundamentals ❌\n\n"
            "**Beneish M-Score** — Earnings manipulation\n"
            "- Below -2.22 = Low risk ✅\n"
            "- Above -2.22 = Possible manipulation ⚠️\n\n"
            "Upload your data and I'll calculate all three for your company!"
        )

    # Generic financial education
    return (
        f"Hi {name}! I'm ready to help with financial analysis.\n\n"
        "You haven't uploaded any company data yet. To get personalised answers:\n\n"
        "1. **Add a company** → Sidebar → Companies\n"
        "2. **Upload data** → Sidebar → Upload Data (CSV or Excel)\n"
        "3. **Ask anything** → I'll answer with your exact numbers\n\n"
        "**You can still ask me general questions like:**\n"
        "- 'What is a good net margin?'\n"
        "- 'Explain the Altman Z-Score'\n"
        "- 'What KPIs should I track?'\n"
        "- 'What makes a good investment?'\n"
        "- 'How do I read a balance sheet?'"
    )


@router.get("/history/{company_id}")
def get_history(
    company_id: int,
    session_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.user_id == current_user.id,
    )
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    msgs = query.order_by(ChatMessage.created_at.asc()).limit(limit).all()
    return [{"role": m.role, "content": m.content, "created_at": str(m.created_at)} for m in msgs]


@router.delete("/history/{company_id}")
def clear_history(
    company_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.user_id == current_user.id,
    )
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    deleted = query.delete()
    db.commit()
    return {"deleted_messages": deleted}
