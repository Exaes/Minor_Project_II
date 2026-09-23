"""
CSV/Excel file upload handler.

Validates, parses, and stores uploaded startup data files.
Used by both the FastAPI upload endpoint and Streamlit UI.
"""

import io
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import TEMPLATES_DIR

from .dataset_loader import _standardize_columns, validate_columns, CANONICAL_COLUMNS


def parse_upload(file_content: bytes, filename: str) -> dict:
    """
    Parse an uploaded CSV or Excel file.

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename (used to determine format).

    Returns:
        {
            "success": bool,
            "data": pd.DataFrame or None,
            "validation": validation dict,
            "error": str or None,
            "row_count": int,
        }
    """
    try:
        # Determine file type and parse
        if filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_content))
        elif filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            return {
                "success": False,
                "data": None,
                "validation": None,
                "error": f"Unsupported file format: {filename}. Use .csv or .xlsx.",
                "row_count": 0,
            }

        if df.empty:
            return {
                "success": False,
                "data": None,
                "validation": None,
                "error": "Uploaded file is empty.",
                "row_count": 0,
            }

        # Standardize columns
        df = _standardize_columns(df)

        # Validate
        validation = validate_columns(df)

        if not validation["valid"]:
            return {
                "success": False,
                "data": df,
                "validation": validation,
                "error": (
                    f"Missing required columns: {validation['missing_required']}. "
                    f"Download the template from /api/template for the expected format."
                ),
                "row_count": len(df),
            }

        return {
            "success": True,
            "data": df,
            "validation": validation,
            "error": None,
            "row_count": len(df),
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "validation": None,
            "error": f"Failed to parse file: {str(e)}",
            "row_count": 0,
        }


def get_template_path() -> str:
    """Return the path to the upload template CSV."""
    return str(TEMPLATES_DIR / "upload_template.csv")


def dataframe_to_startup_dicts(df: pd.DataFrame) -> list[dict]:
    """
    Convert a DataFrame into a list of dicts matching the Startup model fields.
    Fills missing optional columns with sensible defaults.
    """
    defaults = {
        "founding_year": 2020,
        "funding_stage": "Seed",
        "total_funding_usd": 0,
        "funding_rounds_count": 1,
        "monthly_revenue": 0,
        "monthly_expenses": 0,
        "cogs": 0,
        "operating_expenses": 0,
        "gross_profit": 0,
        "headcount": 1,
        "customer_count": 0,
        "monthly_burn": 0,
        "marketing_spend": 0,
        "avg_revenue_per_customer": 0,
        "avg_customer_lifetime_months": 12,
        "new_customers_monthly": 0,
        "mom_revenue_growth": 0,
        "mom_customer_growth": 0,
        "yoy_revenue_growth": 0,
        "status": None,
    }

    records = []
    for _, row in df.iterrows():
        record = {}
        for col in CANONICAL_COLUMNS:
            if col in df.columns and pd.notna(row.get(col)):
                record[col] = row[col]
            else:
                record[col] = defaults.get(col)
        records.append(record)
    return records
