"""
Pydantic schemas for the FastAPI backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StartupManualEntry(BaseModel):
    """Schema for manually entered startup data."""
    company_name: str = Field(..., description="Startup Name")
    industry: str = Field(..., description="Industry")
    founding_year: int = Field(2020, description="Founding Year")
    funding_stage: str = Field("Seed", description="Funding Stage")
    headcount: int = Field(1, description="Number of Employees")
    total_funding_usd: float = Field(0.0, description="Total Funding Raised (USD)")
    funding_rounds_count: int = Field(1, description="Number of Funding Rounds")
    monthly_revenue: float = Field(0.0, description="Average Monthly Revenue (USD)")
    monthly_expenses: float = Field(0.0, description="Average Monthly Expenses (USD)")
    cogs: float = Field(0.0, description="Cost of Goods Sold (Monthly, USD)")
    operating_expenses: float = Field(0.0, description="Operating Expenses (Monthly, USD)")
    marketing_spend: float = Field(0.0, description="Marketing Spend (Monthly, USD)")
    customer_count: int = Field(0, description="Total Customer Count")
    new_customers_monthly: int = Field(0, description="New Customers Acquired Monthly")
    avg_revenue_per_customer: float = Field(0.0, description="Average Revenue Per Customer (USD)")
    avg_customer_lifetime_months: float = Field(12.0, description="Estimated Customer Lifetime (Months)")
    mom_revenue_growth: float = Field(0.0, description="Month-over-Month Revenue Growth (Decimal)")


class RecommendationSchema(BaseModel):
    """Schema for a single recommendation."""
    rank: int
    title: str
    category: str
    impact_level: str
    explanation: str
    supporting_data: Dict[str, Any]


class DeviationSchema(BaseModel):
    """Schema for a metric deviation."""
    metric: str
    label: str
    your_value: float
    benchmark_mean: float
    benchmark_median: float
    z_score: float
    percentile: float
    direction: str
    is_favorable: bool
    severity: str


class AnalysisResponse(BaseModel):
    """Schema for a full analysis result."""
    analysis_id: int
    startup_id: int
    company_name: str
    efficiency_score: float
    peer_group_label: str
    computed_metrics: Dict[str, float]
    peer_benchmarks: Dict[str, Any]
    deviations: List[DeviationSchema]
    recommendations: List[RecommendationSchema]
    
    class Config:
        orm_mode = True
