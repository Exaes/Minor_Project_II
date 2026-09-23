"""
Scoring module for target startups.

Takes a target startup's data, runs it through the feature pipeline,
finds its peer group, and computes:
1. Efficiency score (0–100 composite)
2. Per-metric z-scores against peer benchmarks
3. Ranked deviation list (largest deviations first)
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import BENCHMARK_MODEL_PATH, PEER_BENCHMARKS_PATH, FEATURE_COLUMNS_PATH

_processing_dir = os.path.join(os.path.dirname(__file__), "..", "processing_layer")
sys.path.insert(0, _processing_dir)
import cleaner
import feature_engineer
import peer_grouper


def load_model_artifacts() -> tuple:
    """
    Load the trained model, peer benchmarks, and feature columns from disk.

    Returns:
        Tuple of (model, benchmarks dict, feature_columns list).
    """
    model = joblib.load(str(BENCHMARK_MODEL_PATH))

    with open(str(PEER_BENCHMARKS_PATH)) as f:
        benchmarks = json.load(f)

    with open(str(FEATURE_COLUMNS_PATH)) as f:
        feature_columns = json.load(f)

    return model, benchmarks, feature_columns


def score_startup(startup_data: dict) -> dict:
    """
    Score a single target startup against peer benchmarks.

    Args:
        startup_data: Dict with startup fields (same as CSV columns).

    Returns:
        {
            "efficiency_score": float (0-100),
            "success_probability": float (0-1),
            "peer_group_id": str,
            "peer_group_label": str,
            "computed_metrics": {metric: value},
            "peer_benchmarks": {metric: {mean, median, std, ...}},
            "deviations": [
                {
                    "metric": str,
                    "label": str,
                    "your_value": float,
                    "benchmark_mean": float,
                    "benchmark_median": float,
                    "z_score": float,
                    "percentile": float,
                    "direction": "above" | "below",
                    "is_favorable": bool,
                    "severity": "critical" | "warning" | "ok",
                },
                ...
            ]  # sorted by |z_score| descending
        }
    """
    model, benchmarks, feature_columns = load_model_artifacts()

    # Create single-row DataFrame
    df = pd.DataFrame([startup_data])

    # Run processing pipeline
    df = cleaner.clean_dataframe(df, cap_outliers=False)  # Don't cap target's values
    df = feature_engineer.compute_all_features(df)

    # Find peer group
    industry = str(startup_data.get("industry", "Other"))
    stage = str(startup_data.get("funding_stage", "Seed"))
    headcount = int(startup_data.get("headcount", 1))

    available_groups = [g for g in benchmarks.keys() if g != "_global"]
    peer_group_id = peer_grouper.find_peer_group(
        industry, stage, headcount, available_groups
    )

    # Get peer benchmarks (fall back to global if peer group not found)
    peer_stats = benchmarks.get(peer_group_id, benchmarks.get("_global", {}))

    # Label encode categoricals (needed for model prediction)
    from sklearn.preprocessing import LabelEncoder
    industry_encoder = LabelEncoder()
    industry_encoder.classes_ = np.array([
        "CleanTech", "E-commerce", "EdTech", "Fintech", "HealthTech", "SaaS", "Other"
    ])
    stage_encoder = LabelEncoder()
    stage_encoder.classes_ = np.array([
        "Pre-seed", "Seed", "Series A", "Series B", "Series C+"
    ])

    try:
        df["industry_encoded"] = industry_encoder.transform(df["industry"].astype(str))
    except ValueError:
        df["industry_encoded"] = 0
    try:
        df["funding_stage_encoded"] = stage_encoder.transform(df["funding_stage"].astype(str))
    except ValueError:
        df["funding_stage_encoded"] = 1

    # Extract computed metrics
    computed_metrics = {}
    for metric in feature_engineer.ENGINEERED_FEATURES:
        if metric in df.columns:
            val = df[metric].iloc[0]
            computed_metrics[metric] = float(val) if pd.notna(val) else 0.0

    # Compute deviations
    deviations = _compute_deviations(computed_metrics, peer_stats)

    # Model prediction
    available_features = [f for f in feature_columns if f in df.columns]
    X = df[available_features].fillna(0)

    # Pad missing features with zeros
    for f in feature_columns:
        if f not in X.columns:
            X[f] = 0
    X = X[feature_columns]

    success_prob = float(model.predict_proba(X)[0][1])

    # Composite efficiency score (0-100)
    efficiency_score = _compute_efficiency_score(computed_metrics, peer_stats, success_prob)

    # Determine peer group label
    parts = peer_group_id.split("_")
    if len(parts) >= 3:
        peer_group_label = f"{parts[0]} / {parts[1]} / {parts[2]}"
    else:
        peer_group_label = peer_group_id

    return {
        "efficiency_score": round(efficiency_score, 1),
        "success_probability": round(success_prob, 4),
        "peer_group_id": peer_group_id,
        "peer_group_label": peer_group_label,
        "computed_metrics": computed_metrics,
        "peer_benchmarks": peer_stats,
        "deviations": deviations,
    }


def _compute_deviations(
    computed_metrics: dict,
    peer_stats: dict,
) -> list[dict]:
    """
    Compute z-score deviations for each metric against peer benchmarks.
    Returns list sorted by absolute z-score (largest deviations first).
    """
    deviations = []

    for metric, value in computed_metrics.items():
        if metric not in peer_stats:
            continue

        stats = peer_stats[metric]
        mean = stats.get("mean", 0)
        std = stats.get("std", 1)
        median = stats.get("median", mean)

        # Z-score
        if std > 0:
            z_score = (value - mean) / std
        else:
            z_score = 0.0

        # Percentile approximation (using normal distribution)
        from scipy.stats import norm
        percentile = float(norm.cdf(z_score) * 100)

        # Direction
        direction = "above" if value > mean else "below"

        # Is this deviation favorable?
        higher_is_better = feature_engineer.METRIC_DIRECTION.get(metric, True)
        if higher_is_better:
            is_favorable = value >= mean
        else:
            is_favorable = value <= mean

        # Severity
        abs_z = abs(z_score)
        if abs_z >= 2.0 and not is_favorable:
            severity = "critical"
        elif abs_z >= 1.0 and not is_favorable:
            severity = "warning"
        else:
            severity = "ok"

        deviations.append({
            "metric": metric,
            "label": feature_engineer.METRIC_LABELS.get(metric, metric),
            "your_value": round(value, 4),
            "benchmark_mean": round(mean, 4),
            "benchmark_median": round(median, 4),
            "z_score": round(z_score, 4),
            "percentile": round(percentile, 1),
            "direction": direction,
            "is_favorable": is_favorable,
            "severity": severity,
        })

    # Sort by absolute z-score descending (largest deviations first)
    deviations.sort(key=lambda d: abs(d["z_score"]), reverse=True)

    return deviations


def _compute_efficiency_score(
    computed_metrics: dict,
    peer_stats: dict,
    success_probability: float,
) -> float:
    """
    Compute a composite efficiency score (0–100).

    Weighted combination of:
    - Success probability from model (40%)
    - Favorable metric percentile average (60%)
    """
    # Metric-based component
    percentile_scores = []
    weights = {
        "gross_margin": 3,
        "ltv_cac_ratio": 3,
        "runway_months": 2,
        "funding_efficiency": 2,
        "revenue_per_employee": 2,
        "opex_to_revenue": 2,
        "mom_revenue_growth": 2,
        "burn_rate": 1,
        "cac": 1,
        "payback_period": 1,
    }

    for metric, weight in weights.items():
        if metric not in computed_metrics or metric not in peer_stats:
            continue

        value = computed_metrics[metric]
        stats = peer_stats[metric]
        std = stats.get("std", 1)
        mean = stats.get("mean", 0)

        if std > 0:
            z = (value - mean) / std
        else:
            z = 0

        higher_is_better = feature_engineer.METRIC_DIRECTION.get(metric, True)

        # Convert z-score to a 0–100 percentile score
        from scipy.stats import norm
        if higher_is_better:
            score = norm.cdf(z) * 100
        else:
            score = (1 - norm.cdf(z)) * 100

        percentile_scores.extend([score] * weight)

    if percentile_scores:
        metric_score = np.mean(percentile_scores)
    else:
        metric_score = 50.0  # Neutral

    # Composite
    efficiency_score = (
        0.40 * success_probability * 100 +
        0.60 * metric_score
    )

    return float(np.clip(efficiency_score, 0, 100))
