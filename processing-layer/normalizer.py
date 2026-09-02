"""
Data normalization and scaling module.

Handles:
- Log transformation for skewed financial features
- Standard scaling (z-score normalization)
- Min-max scaling for bounded features
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder


# Columns to log-transform (highly right-skewed financial distributions)
LOG_TRANSFORM_COLUMNS = [
    "total_funding_usd", "monthly_revenue", "monthly_expenses",
    "cogs", "operating_expenses", "marketing_spend",
    "customer_count", "headcount",
]

# Columns to standard-scale for model input
SCALE_COLUMNS = [
    "total_funding_usd", "monthly_revenue", "monthly_expenses",
    "cogs", "operating_expenses", "gross_profit",
    "headcount", "customer_count", "monthly_burn",
    "marketing_spend", "avg_revenue_per_customer",
    "avg_customer_lifetime_months", "new_customers_monthly",
    "mom_revenue_growth", "mom_customer_growth", "yoy_revenue_growth",
    "founding_year", "funding_rounds_count",
]

# Categorical columns for encoding
CATEGORICAL_COLUMNS = ["industry", "funding_stage"]


def normalize_dataframe(
    df: pd.DataFrame,
    apply_log: bool = True,
    apply_scaling: bool = True,
    scaler: StandardScaler | None = None,
    fit_scaler: bool = True,
) -> tuple[pd.DataFrame, StandardScaler | None, dict]:
    """
    Normalize a DataFrame for model consumption.

    Args:
        df: Cleaned DataFrame.
        apply_log: Whether to apply log1p transformation.
        apply_scaling: Whether to apply standard scaling.
        scaler: Pre-fitted scaler (for scoring new data with training scaler).
        fit_scaler: Whether to fit the scaler (True for training, False for inference).

    Returns:
        Tuple of (normalized DataFrame, fitted scaler, label_encoders dict).
    """
    df = df.copy()
    label_encoders = {}

    # Step 1: Log transform skewed features
    if apply_log:
        for col in LOG_TRANSFORM_COLUMNS:
            if col in df.columns:
                log_col = f"{col}_log"
                df[log_col] = np.log1p(df[col].clip(lower=0))

    # Step 2: Encode categoricals
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    # Step 3: Standard scaling
    if apply_scaling:
        cols_to_scale = [c for c in SCALE_COLUMNS if c in df.columns]
        if cols_to_scale:
            if scaler is None:
                scaler = StandardScaler()
            if fit_scaler:
                df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
            else:
                df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    return df, scaler, label_encoders


def inverse_scale(
    df: pd.DataFrame,
    scaler: StandardScaler,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Reverse standard scaling for interpretability."""
    df = df.copy()
    cols = columns or [c for c in SCALE_COLUMNS if c in df.columns]
    if cols and scaler is not None:
        df[cols] = scaler.inverse_transform(df[cols])
    return df
