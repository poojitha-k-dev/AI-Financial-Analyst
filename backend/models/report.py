from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    report_type = Column(String(50), nullable=False)    # full | kpi | risk | trend | chat
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)               # AI-generated markdown
    executive_summary = Column(Text, nullable=True)
    overall_rating = Column(String(20), nullable=True)  # Excellent/Good/Fair/Weak/Critical
    kpis = Column(JSON, nullable=True)
    risk_scores = Column(JSON, nullable=True)
    forecasts = Column(JSON, nullable=True)
    anomalies = Column(JSON, nullable=True)
    benchmarks = Column(JSON, nullable=True)
    llm_provider = Column(String(30), nullable=True)
    model_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    pdf_path = Column(String(500), nullable=True)
    excel_path = Column(String(500), nullable=True)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="reports")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(10), nullable=False)   # user | assistant
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
