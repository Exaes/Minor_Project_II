"""
Data cleaning module.

Handles:
- Missing value imputation (median for numeric, mode for categorical)
- Outlier capping (IQR-based)
- Type coercion and validation
- Column name standardization
"""

import numpy as np
import pandas as pd


# Columns that should be numeric
NUMERIC_COLUMNS = [
    "total_funding_usd", "funding_rounds_count",
    "monthly_revenue", "monthly_expenses", "cogs", "operating_expenses",
    "gross_profit", "headcount", "customer_count", "monthly_burn",
    "marketing_spend", "avg_revenue_per_customer", "avg_customer_lifetime_months",
    "new_customers_monthly", "mom_revenue_growth", "mom_customer_growth",
    "yoy_revenue_growth", "founding_year",
]

# Columns that should not be negative
NON_NEGATIVE_COLUMNS = [
    "total_funding_usd", "monthly_revenue", "monthly_expenses", "cogs",
    "operating_expenses", "headcount", "customer_count", "marketing_spend",
    "avg_revenue_per_customer", "avg_customer_lifetime_months",
    "new_customers_monthly", "funding_rounds_count",
]

# Columns to apply IQR-based outlier capping
OUTLIER_CAP_COLUMNS = [
    "total_funding_usd", "monthly_revenue", "monthly_expenses",
    "cogs", "operating_expenses", "marketing_spend",
    "avg_revenue_per_customer", "headcount", "customer_count",
]


def clean_dataframe(df: pd.DataFrame, cap_outliers: bool = True) -> pd.DataFrame:
    """
    Full cleaning pipeline for a startup DataFrame.

    Steps:
        1. Coerce types
        2. Impute missing values
        3. Enforce non-negative constraints
        4. Cap outliers (optional)

    Args:
        df: Raw DataFrame.
        cap_outliers: Whether to apply IQR-based outlier capping.

    Returns:
        Cleaned DataFrame (copy — original is not modified).
    """
    df = df.copy()

    # Step 1: Type coercion
    df = _coerce_types(df)

    # Step 2: Impute missing values
    df = _impute_missing(df)

    # Step 3: Non-negative enforcement
    df = _enforce_non_negative(df)

    # Step 4: Outlier capping
    if cap_outliers:
        df = _cap_outliers(df)

    # Step 5: Derive missing computed fields
    df = _derive_fields(df)

    return df


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce numeric columns to float, handling parse errors gracefully."""
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing values:
    - Numeric columns: median (per-industry if 'industry' column exists)
    - Categorical: mode or default
    """
    # Industry-aware imputation for numeric columns
    has_industry = "industry" in df.columns

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        if df[col].isna().sum() == 0:
            continue

        if has_industry and df[col].isna().sum() < len(df):
            # Per-industry median
            industry_medians = df.groupby("industry")[col].transform("median")
            df[col] = df[col].fillna(industry_medians)

        # Global median for remaining NAs
        median_val = df[col].median()
        if pd.isna(median_val):
            median_val = 0
        df[col] = df[col].fillna(median_val)

    # Categorical defaults
    if "industry" in df.columns:
        df["industry"] = df["industry"].fillna("Other")
    if "funding_stage" in df.columns:
        df["funding_stage"] = df["funding_stage"].fillna("Seed")
    if "company_name" in df.columns:
        df["company_name"] = df["company_name"].fillna("Unknown")

    return df


def _enforce_non_negative(df: pd.DataFrame) -> pd.DataFrame:
    """Clamp non-negative columns to 0 minimum."""
    for col in NON_NEGATIVE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)
    return df


def _cap_outliers(df: pd.DataFrame, multiplier: float = 1.5) -> pd.DataFrame:
    """
    Cap outliers using IQR method.
    Values beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR are clamped.
    """
    for col in OUTLIER_CAP_COLUMNS:
        if col not in df.columns:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        df[col] = df[col].clip(lower=max(0, lower), upper=upper)
    return df


def _derive_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Derive computed fields if they're missing but their inputs exist."""
    # Gross profit
    if "gross_profit" in df.columns and "monthly_revenue" in df.columns and "cogs" in df.columns:
        mask = df["gross_profit"] == 0
        df.loc[mask, "gross_profit"] = df.loc[mask, "monthly_revenue"] - df.loc[mask, "cogs"]

    # Monthly burn
    if "monthly_burn" in df.columns and "monthly_expenses" in df.columns and "monthly_revenue" in df.columns:
        mask = df["monthly_burn"] == 0
        df.loc[mask, "monthly_burn"] = (
            df.loc[mask, "monthly_expenses"] - df.loc[mask, "monthly_revenue"]
        ).clip(lower=0)

    # Operating expenses
    if "operating_expenses" in df.columns and "monthly_expenses" in df.columns and "cogs" in df.columns:
        mask = df["operating_expenses"] == 0
        df.loc[mask, "operating_expenses"] = (
            df.loc[mask, "monthly_expenses"] - df.loc[mask, "cogs"]
        ).clip(lower=0)

    return df
