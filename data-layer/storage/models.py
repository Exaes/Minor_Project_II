"""
SQLAlchemy ORM models for the startup analysis system.

Models:
- Startup: uploaded startup data (both reference and target)
- AnalysisResult: benchmarking/scoring results for a target startup
- Recommendation: individual recommendation items per analysis
"""

import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from .database import Base


class Startup(Base):
    """Stores uploaded startup data (both reference and target startups)."""
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=False)
    founding_year = Column(Integer)
    funding_stage = Column(String(50))
    total_funding_usd = Column(Float, default=0)
    funding_rounds_count = Column(Integer, default=0)
    monthly_revenue = Column(Float, default=0)
    monthly_expenses = Column(Float, default=0)
    cogs = Column(Float, default=0)
    operating_expenses = Column(Float, default=0)
    gross_profit = Column(Float, default=0)
    headcount = Column(Integer, default=1)
    customer_count = Column(Integer, default=0)
    monthly_burn = Column(Float, default=0)
    marketing_spend = Column(Float, default=0)
    avg_revenue_per_customer = Column(Float, default=0)
    avg_customer_lifetime_months = Column(Float, default=12)
    new_customers_monthly = Column(Integer, default=0)
    mom_revenue_growth = Column(Float, default=0)
    mom_customer_growth = Column(Float, default=0)
    yoy_revenue_growth = Column(Float, default=0)
    status = Column(Integer, nullable=True)  # 1=success, 0=fail, NULL=target

    is_reference = Column(Integer, default=0)  # 1=reference dataset, 0=user-uploaded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    analyses = relationship(
        "AnalysisResult", back_populates="startup", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Startup(id={self.id}, name='{self.company_name}')>"


class AnalysisResult(Base):
    """Stores results of analyzing a target startup against benchmarks."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    efficiency_score = Column(Float, default=0)  # 0–100 composite score
    peer_group_id = Column(String(100))
    peer_group_label = Column(String(255))

    # Serialized JSON (stored as text for SQLite compatibility)
    computed_metrics_json = Column(Text, default="{}")
    peer_benchmarks_json = Column(Text, default="{}")
    deviations_json = Column(Text, default="[]")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    startup = relationship("Startup", back_populates="analyses")
    recommendations = relationship(
        "Recommendation", back_populates="analysis", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, score={self.efficiency_score:.1f})>"


class Recommendation(Base):
    """Individual recommendation from an analysis."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    rank = Column(Integer, default=0)
    category = Column(String(50))       # Cost-cutting | Margin improvement | Growth efficiency | Hiring pace
    impact_level = Column(String(20))   # High | Medium | Low
    title = Column(String(500))
    explanation = Column(Text)
    supporting_data_json = Column(Text, default="{}")  # JSON: metric details

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, cat='{self.category}')>"
