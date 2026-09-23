import pandas as pd
import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from processing_layer.feature_engineer import compute_all_features

@pytest.fixture
def sample_data():
    return pd.DataFrame([{
        "monthly_revenue": 100000.0,
        "monthly_expenses": 120000.0,
        "cogs": 30000.0,
        "operating_expenses": 90000.0,
        "total_funding_usd": 2400000.0,
        "funding_rounds_count": 2,
        "headcount": 20,
        "marketing_spend": 20000.0,
        "new_customers_monthly": 100,
        "avg_revenue_per_customer": 500.0,
        "avg_customer_lifetime_months": 24.0,
        "mom_revenue_growth": 0.1,
        "mom_customer_growth": 0.08
    }])

def test_financial_efficiency(sample_data):
    df = compute_all_features(sample_data)
    
    assert df["burn_rate"].iloc[0] == 20000.0
    assert df["runway_months"].iloc[0] == 120.0 # 2.4m / 20k
    assert df["gross_margin"].iloc[0] == 0.7 # (100k - 30k) / 100k
    assert df["opex_to_revenue"].iloc[0] == 0.9 # 90k / 100k

def test_unit_economics(sample_data):
    df = compute_all_features(sample_data)
    
    assert df["cac"].iloc[0] == 200.0 # 20k / 100
    assert df["ltv"].iloc[0] == 12000.0 # 500 * 24
    assert df["ltv_cac_ratio"].iloc[0] == 50.0 # 12k / 200 capped at 50
    
def test_growth_and_efficiency(sample_data):
    df = compute_all_features(sample_data)
    
    assert df["revenue_per_employee"].iloc[0] == 5000.0 # 100k / 20
    assert df["funding_efficiency"].iloc[0] == 0.5 # (100k * 12) / 2.4m
    assert df["capital_to_revenue"].iloc[0] == 2.0 # 2.4m / 1.2m
