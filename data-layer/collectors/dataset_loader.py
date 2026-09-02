"""
Load reference startup datasets from CSV files.

Supports:
- Our synthetic reference dataset (primary)
- Kaggle-format startup datasets (supplementary)
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import REFERENCE_DATASET_PATH, RAW_DATA_DIR


# Canonical column names used throughout the system
CANONICAL_COLUMNS = [
    "company_name", "industry", "founding_year", "funding_stage",
    "total_funding_usd", "funding_rounds_count",
    "monthly_revenue", "monthly_expenses", "cogs", "operating_expenses",
    "gross_profit", "headcount", "customer_count", "monthly_burn",
    "marketing_spend", "avg_revenue_per_customer", "avg_customer_lifetime_months",
    "new_customers_monthly", "mom_revenue_growth", "mom_customer_growth",
    "yoy_revenue_growth", "status",
]

# Minimum required columns for analysis
REQUIRED_COLUMNS = [
    "company_name", "industry", "monthly_revenue", "monthly_expenses", "headcount",
]


def load_reference_dataset(path: str = None) -> pd.DataFrame:
    """
    Load the reference startup dataset.

    Args:
        path: Path to CSV file. Defaults to REFERENCE_DATASET_PATH.

    Returns:
        DataFrame with standardized column names.

    Raises:
        FileNotFoundError: If the dataset file doesn't exist.
    """
    path = path or str(REFERENCE_DATASET_PATH)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Reference dataset not found at {path}. "
            "Run 'python scripts/generate_synthetic_data.py' first."
        )

    df = pd.read_csv(path)
    df = _standardize_columns(df)
    return df


def load_any_csv(path: str) -> pd.DataFrame:
    """
    Load any CSV file and standardize column names.

    Args:
        path: Absolute path to the CSV file.

    Returns:
        DataFrame with standardized columns.
    """
    if path.endswith(".xlsx") or path.endswith(".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    df = _standardize_columns(df)
    return df


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names: lowercase, replace spaces/hyphens with underscores.
    """
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9_]", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return df


def validate_columns(df: pd.DataFrame) -> dict:
    """
    Validate that a DataFrame has the required columns.

    Returns:
        {
            "valid": bool,
            "present": list of matching columns,
            "missing_required": list of missing required columns,
            "extra": list of unrecognized columns,
        }
    """
    present = [c for c in CANONICAL_COLUMNS if c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in CANONICAL_COLUMNS]

    return {
        "valid": len(missing) == 0,
        "present": present,
        "missing_required": missing,
        "extra": extra,
    }
