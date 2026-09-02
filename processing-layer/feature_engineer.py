"""
Feature engineering module.

Computes all 15+ financial, operational, and efficiency metrics
required by the benchmarking model and recommendation engine.

Every metric is documented with its formula and interpretation.
"""

import numpy as np
import pandas as pd


# ── Metric Definitions ──
# Each function computes one metric and adds it as a column.

def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all engineered features from raw/cleaned startup data.

    This is the main entry point — calls every individual metric function.

    Args:
        df: Cleaned startup DataFrame with standard column names.

    Returns:
        DataFrame with all original + engineered feature columns.
    """
    df = df.copy()

    df = compute_burn_rate(df)
    df = compute_runway(df)
    df = compute_cac(df)
    df = compute_ltv(df)
    df = compute_ltv_cac_ratio(df)
    df = compute_gross_margin(df)
    df = compute_opex_to_revenue(df)
    df = compute_revenue_per_employee(df)
    df = compute_growth_rates(df)
    df = compute_funding_efficiency(df)
    df = compute_headcount_vs_revenue_growth(df)
    df = compute_capital_vs_revenue(df)
    df = compute_dilution_per_round(df)
    df = compute_payback_period(df)

    return df


# ── Individual Metric Functions ──

def compute_burn_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Burn Rate = monthly_expenses - monthly_revenue (if negative cash flow, else 0).
    Interpretation: How much cash the company loses per month.
    """
    if "monthly_burn" not in df.columns or df["monthly_burn"].sum() == 0:
        df["burn_rate"] = (df["monthly_expenses"] - df["monthly_revenue"]).clip(lower=0)
    else:
        df["burn_rate"] = df["monthly_burn"]
    return df


def compute_runway(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runway (months) = total_funding / burn_rate.
    Interpretation: How many months the company can survive at current burn.
    Capped at 120 months for companies with no/minimal burn.
    """
    df["runway_months"] = np.where(
        df["burn_rate"] > 0,
        (df["total_funding_usd"] / df["burn_rate"]).clip(upper=120),
        120.0  # Effectively infinite runway
    )
    return df


def compute_cac(df: pd.DataFrame) -> pd.DataFrame:
    """
    Customer Acquisition Cost = marketing_spend / new_customers_monthly.
    Interpretation: Cost to acquire one new customer.
    """
    df["cac"] = np.where(
        df["new_customers_monthly"] > 0,
        df["marketing_spend"] / df["new_customers_monthly"],
        0.0
    )
    return df


def compute_ltv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lifetime Value = avg_revenue_per_customer × avg_customer_lifetime_months.
    Interpretation: Total revenue expected from a single customer.
    """
    df["ltv"] = df["avg_revenue_per_customer"] * df["avg_customer_lifetime_months"]
    return df


def compute_ltv_cac_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    LTV:CAC Ratio = LTV / CAC.
    Interpretation: >3 is healthy, <1 means losing money per customer.
    """
    # Ensure ltv and cac are computed
    if "ltv" not in df.columns:
        df = compute_ltv(df)
    if "cac" not in df.columns:
        df = compute_cac(df)

    df["ltv_cac_ratio"] = np.where(
        df["cac"] > 0,
        (df["ltv"] / df["cac"]).clip(upper=50),  # Cap extreme values
        0.0
    )
    return df


def compute_gross_margin(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gross Margin = (revenue - COGS) / revenue.
    Interpretation: Percentage of revenue retained after direct costs.
    """
    df["gross_margin"] = np.where(
        df["monthly_revenue"] > 0,
        (df["monthly_revenue"] - df["cogs"]) / df["monthly_revenue"],
        0.0
    )
    df["gross_margin"] = df["gross_margin"].clip(-1, 1)
    return df


def compute_opex_to_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    OpEx-to-Revenue = operating_expenses / revenue.
    Interpretation: <1 means revenue covers operating costs. Lower is better.
    """
    df["opex_to_revenue"] = np.where(
        df["monthly_revenue"] > 0,
        df["operating_expenses"] / df["monthly_revenue"],
        0.0
    )
    df["opex_to_revenue"] = df["opex_to_revenue"].clip(0, 10)
    return df


def compute_revenue_per_employee(df: pd.DataFrame) -> pd.DataFrame:
    """
    Revenue per Employee = monthly_revenue / headcount.
    Interpretation: Operational efficiency — higher is better.
    """
    df["revenue_per_employee"] = np.where(
        df["headcount"] > 0,
        df["monthly_revenue"] / df["headcount"],
        0.0
    )
    return df


def compute_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    MoM and YoY revenue growth rates.
    If not already present, use the raw column values.
    Also computes annualized YoY from MoM if missing.
    """
    # MoM growth — use existing column or default
    if "mom_revenue_growth" not in df.columns:
        df["mom_revenue_growth"] = 0.0

    # YoY growth — compute from MoM if missing
    if "yoy_revenue_growth" not in df.columns or df["yoy_revenue_growth"].sum() == 0:
        df["yoy_revenue_growth"] = (1 + df["mom_revenue_growth"]).pow(12) - 1

    # Customer growth
    if "mom_customer_growth" not in df.columns:
        df["mom_customer_growth"] = 0.0

    return df


def compute_funding_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Funding Efficiency = (annual revenue) / total_funding.
    Interpretation: Revenue generated per dollar of funding raised. Higher = more efficient.
    """
    annual_revenue = df["monthly_revenue"] * 12
    df["funding_efficiency"] = np.where(
        df["total_funding_usd"] > 0,
        annual_revenue / df["total_funding_usd"],
        0.0
    )
    return df


def compute_headcount_vs_revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Headcount Growth vs Revenue Growth ratio.
    Interpretation: <1 means revenue growing faster than headcount (good efficiency).
    Approximated from MoM growth if individual rates not available.
    """
    # Use mom_customer_growth as proxy for operational growth
    df["hc_vs_rev_growth"] = np.where(
        df["mom_revenue_growth"].abs() > 0.001,
        df["mom_customer_growth"] / df["mom_revenue_growth"],
        1.0
    )
    df["hc_vs_rev_growth"] = df["hc_vs_rev_growth"].clip(-5, 5)
    return df


def compute_capital_vs_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Capital Raised vs Revenue = total_funding / annual_revenue.
    Interpretation: How many years of revenue were raised as capital. Lower = more efficient.
    """
    annual_revenue = df["monthly_revenue"] * 12
    df["capital_to_revenue"] = np.where(
        annual_revenue > 0,
        df["total_funding_usd"] / annual_revenue,
        0.0
    )
    df["capital_to_revenue"] = df["capital_to_revenue"].clip(0, 100)
    return df


def compute_dilution_per_round(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimated Dilution per Round = 1 / (funding_rounds + 1).
    Simplified estimate — in reality depends on valuation, but this approximates
    ~50% dilution at round 1, ~33% at round 2, etc.
    """
    df["dilution_per_round"] = 1 / (df["funding_rounds_count"] + 1)
    return df


def compute_payback_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Payback Period = CAC / monthly_revenue_per_customer.
    Interpretation: Months to recover customer acquisition cost. Lower is better.
    """
    if "cac" not in df.columns:
        df = compute_cac(df)

    df["payback_period"] = np.where(
        df["avg_revenue_per_customer"] > 0,
        (df["cac"] / df["avg_revenue_per_customer"]).clip(upper=120),
        0.0
    )
    return df


# ── Feature Column Lists ──

ENGINEERED_FEATURES = [
    "burn_rate", "runway_months", "cac", "ltv", "ltv_cac_ratio",
    "gross_margin", "opex_to_revenue", "revenue_per_employee",
    "mom_revenue_growth", "yoy_revenue_growth", "mom_customer_growth",
    "funding_efficiency", "hc_vs_rev_growth", "capital_to_revenue",
    "dilution_per_round", "payback_period",
]

# Human-readable labels for each metric
METRIC_LABELS = {
    "burn_rate": "Monthly Burn Rate ($)",
    "runway_months": "Runway (months)",
    "cac": "Customer Acquisition Cost ($)",
    "ltv": "Customer Lifetime Value ($)",
    "ltv_cac_ratio": "LTV:CAC Ratio",
    "gross_margin": "Gross Margin (%)",
    "opex_to_revenue": "OpEx-to-Revenue Ratio",
    "revenue_per_employee": "Revenue per Employee ($)",
    "mom_revenue_growth": "MoM Revenue Growth (%)",
    "yoy_revenue_growth": "YoY Revenue Growth (%)",
    "mom_customer_growth": "MoM Customer Growth (%)",
    "funding_efficiency": "Funding Efficiency Ratio",
    "hc_vs_rev_growth": "Headcount vs Revenue Growth",
    "capital_to_revenue": "Capital-to-Revenue Ratio",
    "dilution_per_round": "Dilution per Round",
    "payback_period": "Payback Period (months)",
}

# Whether higher is better (True) or lower is better (False) for each metric
METRIC_DIRECTION = {
    "burn_rate": False,           # Lower burn = better
    "runway_months": True,        # More runway = better
    "cac": False,                 # Lower CAC = better
    "ltv": True,                  # Higher LTV = better
    "ltv_cac_ratio": True,        # Higher ratio = better
    "gross_margin": True,         # Higher margin = better
    "opex_to_revenue": False,     # Lower ratio = better
    "revenue_per_employee": True, # Higher = better
    "mom_revenue_growth": True,   # Higher growth = better
    "yoy_revenue_growth": True,   # Higher growth = better
    "mom_customer_growth": True,  # Higher growth = better
    "funding_efficiency": True,   # Higher = better
    "hc_vs_rev_growth": False,    # Lower = revenue outpacing headcount growth = better
    "capital_to_revenue": False,  # Lower = more efficient use of capital
    "dilution_per_round": False,  # Lower dilution = better
    "payback_period": False,      # Shorter payback = better
}
