from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    currency = Column(String(10), default="USD", nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="companies")
    financials = relationship(
        "FinancialStatement", back_populates="company", cascade="all, delete-orphan"
    )
    reports = relationship(
        "AnalysisReport", back_populates="company", cascade="all, delete-orphan"
    )
    watchlist_items = relationship(
        "WatchlistItem", back_populates="company", cascade="all, delete-orphan"
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    __table_args__ = (
        UniqueConstraint("company_id", "period", "statement_type", name="uq_stmt_period_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String(20), nullable=False)
    period_type = Column(String(10), nullable=False)       # annual | quarterly
    statement_type = Column(String(30), nullable=False)    # combined | income | balance | cashflow

    raw_data = Column(JSON, nullable=True)
    computed_kpis = Column(JSON, nullable=True)

    # Income Statement
    revenue = Column(Float, nullable=True)
    cost_of_goods_sold = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    operating_expenses = Column(Float, nullable=True)
    operating_income = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)
    interest_expense = Column(Float, nullable=True)
    income_before_tax = Column(Float, nullable=True)
    income_tax = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)

    # Balance Sheet
    cash_and_equivalents = Column(Float, nullable=True)
    accounts_receivable = Column(Float, nullable=True)
    inventory = Column(Float, nullable=True)
    total_current_assets = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    accounts_payable = Column(Float, nullable=True)
    short_term_debt = Column(Float, nullable=True)
    total_current_liabilities = Column(Float, nullable=True)
    long_term_debt = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    total_equity = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)

    # Cash Flow
    operating_cash_flow = Column(Float, nullable=True)
    capex = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)
    investing_cash_flow = Column(Float, nullable=True)
    financing_cash_flow = Column(Float, nullable=True)
    dividends_paid = Column(Float, nullable=True)

    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="financials")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="watchlist_items")
