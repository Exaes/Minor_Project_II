"""
Peer grouping module.

Assigns startups to peer groups for apples-to-apples comparison.
Two strategies:
1. Rule-based bucketing (primary): industry × funding_stage × size_bucket
2. K-means clustering (optional): finer-grained grouping on financial features
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ── Size Buckets ──
SIZE_BUCKETS = {
    "Small":  (0, 20),      # 1–20 employees
    "Medium": (21, 100),    # 21–100 employees
    "Large":  (101, 10000), # 101+ employees
}


def assign_peer_groups(df: pd.DataFrame, method: str = "rule") -> pd.DataFrame:
    """
    Assign each startup to a peer group.

    Args:
        df: DataFrame with industry, funding_stage, headcount columns.
        method: 'rule' for rule-based bucketing, 'kmeans' for clustering.

    Returns:
        DataFrame with added 'peer_group_id' and 'peer_group_label' columns.
    """
    df = df.copy()

    if method == "rule":
        df = _rule_based_grouping(df)
    elif method == "kmeans":
        df = _kmeans_grouping(df)
    else:
        raise ValueError(f"Unknown peer grouping method: {method}")

    return df


def _get_size_bucket(headcount: int) -> str:
    """Classify headcount into a size bucket."""
    for bucket_name, (lo, hi) in SIZE_BUCKETS.items():
        if lo <= headcount <= hi:
            return bucket_name
    return "Large"  # Default for very large companies


def _rule_based_grouping(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule-based peer grouping: industry × funding_stage × size_bucket.

    Creates a composite key like 'SaaS_SeriesA_Medium'.
    """
    # Compute size bucket
    df["size_bucket"] = df["headcount"].apply(_get_size_bucket)

    # Create composite peer group
    df["peer_group_label"] = (
        df["industry"].astype(str) + " / " +
        df["funding_stage"].astype(str) + " / " +
        df["size_bucket"].astype(str)
    )
    df["peer_group_id"] = (
        df["industry"].astype(str).str.replace(" ", "") + "_" +
        df["funding_stage"].astype(str).str.replace(" ", "").str.replace("+", "plus") + "_" +
        df["size_bucket"].astype(str)
    )

    return df


def _kmeans_grouping(
    df: pd.DataFrame,
    n_clusters: int = 8,
    features: list[str] | None = None,
) -> pd.DataFrame:
    """
    K-means clustering on financial features for finer-grained peer groups.

    Falls back to rule-based if not enough data points.
    """
    if features is None:
        features = [
            "total_funding_usd", "monthly_revenue", "headcount",
            "monthly_expenses", "customer_count",
        ]

    available = [f for f in features if f in df.columns]
    if len(available) < 2 or len(df) < n_clusters * 2:
        # Not enough data — fall back to rule-based
        return _rule_based_grouping(df)

    # Scale features for clustering
    scaler = StandardScaler()
    X = df[available].fillna(0).values
    X_scaled = scaler.fit_transform(X)

    # Fit K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df["peer_group_id"] = [f"cluster_{l}" for l in labels]
    df["peer_group_label"] = [f"Cluster {l}" for l in labels]

    return df


def get_peer_group_stats(df: pd.DataFrame, metric_columns: list[str]) -> dict:
    """
    Compute benchmark statistics per peer group.

    Args:
        df: DataFrame with peer_group_id and metric columns.
        metric_columns: List of metric column names to compute stats for.

    Returns:
        Dict: {peer_group_id: {metric: {mean, median, std, p25, p75, count}}}
    """
    if "peer_group_id" not in df.columns:
        raise ValueError("DataFrame must have 'peer_group_id' column. Run assign_peer_groups first.")

    stats = {}
    for group_id, group_df in df.groupby("peer_group_id"):
        group_stats = {}
        for metric in metric_columns:
            if metric not in group_df.columns:
                continue
            values = group_df[metric].dropna()
            if len(values) == 0:
                continue
            group_stats[metric] = {
                "mean": float(values.mean()),
                "median": float(values.median()),
                "std": float(values.std()) if len(values) > 1 else 0.0,
                "p25": float(values.quantile(0.25)),
                "p75": float(values.quantile(0.75)),
                "min": float(values.min()),
                "max": float(values.max()),
                "count": int(len(values)),
            }
        stats[str(group_id)] = group_stats

    return stats


def find_peer_group(
    target_industry: str,
    target_stage: str,
    target_headcount: int,
    available_groups: list[str],
) -> str:
    """
    Find the best matching peer group for a target startup.

    Tries exact match first, then relaxes constraints progressively.

    Args:
        target_industry: Target's industry.
        target_stage: Target's funding stage.
        target_headcount: Target's headcount.
        available_groups: List of peer_group_ids from the reference dataset.

    Returns:
        Best matching peer_group_id string.
    """
    size_bucket = _get_size_bucket(target_headcount)
    stage_clean = target_stage.replace(" ", "").replace("+", "plus")
    industry_clean = target_industry.replace(" ", "")

    # Try exact match
    exact = f"{industry_clean}_{stage_clean}_{size_bucket}"
    if exact in available_groups:
        return exact

    # Try industry + stage (any size)
    partial_matches = [g for g in available_groups if g.startswith(f"{industry_clean}_{stage_clean}_")]
    if partial_matches:
        return partial_matches[0]

    # Try industry only (any stage, any size)
    industry_matches = [g for g in available_groups if g.startswith(f"{industry_clean}_")]
    if industry_matches:
        return industry_matches[0]

    # Try stage + size (any industry)
    stage_size_matches = [g for g in available_groups if g.endswith(f"_{stage_clean}_{size_bucket}")]
    if stage_size_matches:
        return stage_size_matches[0]

    # Fallback: return the largest group
    if available_groups:
        return available_groups[0]

    return "unknown"
