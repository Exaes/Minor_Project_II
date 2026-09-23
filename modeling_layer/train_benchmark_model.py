"""
Train the LightGBM benchmarking model on the reference startup dataset.

Approach:
- Binary classification: success (1) vs fail (0)
- Features: all engineered metrics + encoded categoricals
- Evaluation: accuracy, F1, precision, recall, ROC-AUC
- Also computes and saves peer-group benchmark statistics
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, classification_report, confusion_matrix,
)
import lightgbm as lgb

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import (
    REFERENCE_DATASET_PATH, BENCHMARK_MODEL_PATH,
    PEER_BENCHMARKS_PATH, FEATURE_COLUMNS_PATH, SAVED_MODELS_DIR,
)

# Import processing layer modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from importlib import import_module

# Direct imports using sys.path manipulation
_processing_dir = os.path.join(os.path.dirname(__file__), "..", "processing_layer")
sys.path.insert(0, _processing_dir)
import cleaner
import feature_engineer
import peer_grouper
import normalizer


# Feature columns for the model (engineered + encoded categoricals)
MODEL_FEATURES = [
    # Engineered financial/operational metrics
    "burn_rate", "runway_months", "cac", "ltv", "ltv_cac_ratio",
    "gross_margin", "opex_to_revenue", "revenue_per_employee",
    "mom_revenue_growth", "yoy_revenue_growth", "mom_customer_growth",
    "funding_efficiency", "hc_vs_rev_growth", "capital_to_revenue",
    "dilution_per_round", "payback_period",
    # Encoded categoricals
    "industry_encoded", "funding_stage_encoded",
    # Raw numeric features that add signal
    "headcount", "funding_rounds_count",
]

TARGET_COLUMN = "status"


def load_and_prepare_data(data_path: str = None) -> tuple[pd.DataFrame, list[str]]:
    """
    Load reference dataset and run the full processing pipeline.

    Returns:
        Tuple of (processed DataFrame, list of feature column names used).
    """
    path = data_path or str(REFERENCE_DATASET_PATH)
    print(f"Loading dataset from: {path}")
    df = pd.read_csv(path)
    print(f"  Raw records: {len(df)}")

    # Clean
    df = cleaner.clean_dataframe(df, cap_outliers=True)
    print(f"  After cleaning: {len(df)} records")

    # Feature engineering
    df = feature_engineer.compute_all_features(df)
    print(f"  Engineered features: {len(feature_engineer.ENGINEERED_FEATURES)}")

    # Peer grouping
    df = peer_grouper.assign_peer_groups(df, method="rule")
    print(f"  Peer groups: {df['peer_group_id'].nunique()}")

    # Normalization (encode categoricals, but don't scale — LightGBM handles raw values)
    _, _, label_encoders = normalizer.normalize_dataframe(
        df, apply_log=False, apply_scaling=False
    )

    # Ensure all model features exist
    available_features = [f for f in MODEL_FEATURES if f in df.columns]
    print(f"  Available model features: {len(available_features)}/{len(MODEL_FEATURES)}")

    return df, available_features


def train_model(
    df: pd.DataFrame,
    feature_columns: list[str],
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[lgb.LGBMClassifier, dict]:
    """
    Train a LightGBM classifier on the reference dataset.

    Args:
        df: Processed DataFrame with features and target.
        feature_columns: List of feature column names.
        test_size: Fraction for test split.
        random_state: Random seed.

    Returns:
        Tuple of (trained model, evaluation metrics dict).
    """
    # Prepare X and y
    X = df[feature_columns].fillna(0)
    y = df[TARGET_COLUMN]

    print(f"\nTraining data: {len(X)} samples, {len(feature_columns)} features")
    print(f"Class distribution: {dict(y.value_counts())}")

    # Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # LightGBM model
    model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        class_weight="balanced",
        verbose=-1,
    )

    # Train
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
    )

    # Predict
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Evaluate
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "n_features": len(feature_columns),
    }

    # Feature importances
    importances = dict(zip(
        feature_columns,
        [float(x) for x in model.feature_importances_]
    ))
    metrics["feature_importances"] = dict(
        sorted(importances.items(), key=lambda x: x[1], reverse=True)
    )

    # Print report
    print(f"\n{'='*60}")
    print("MODEL EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Fail", "Success"]))
    print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    print(f"\nTop 5 Features:")
    for feat, imp in list(metrics["feature_importances"].items())[:5]:
        print(f"  {feat}: {imp:.0f}")

    return model, metrics


def compute_and_save_benchmarks(
    df: pd.DataFrame,
    metric_columns: list[str],
) -> dict:
    """
    Compute peer-group benchmark statistics and save to JSON.

    Returns:
        Benchmark statistics dict.
    """
    benchmarks = peer_grouper.get_peer_group_stats(df, metric_columns)

    # Also compute global benchmarks (all startups)
    global_stats = {}
    for metric in metric_columns:
        if metric not in df.columns:
            continue
        values = df[metric].dropna()
        if len(values) == 0:
            continue
        global_stats[metric] = {
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()) if len(values) > 1 else 0.0,
            "p25": float(values.quantile(0.25)),
            "p75": float(values.quantile(0.75)),
            "min": float(values.min()),
            "max": float(values.max()),
            "count": int(len(values)),
        }
    benchmarks["_global"] = global_stats

    return benchmarks


def save_artifacts(
    model: lgb.LGBMClassifier,
    metrics: dict,
    benchmarks: dict,
    feature_columns: list[str],
):
    """Save model, metrics, benchmarks, and feature columns to disk."""
    os.makedirs(str(SAVED_MODELS_DIR), exist_ok=True)

    # Save model
    joblib.dump(model, str(BENCHMARK_MODEL_PATH))
    print(f"\nModel saved to: {BENCHMARK_MODEL_PATH}")

    # Save benchmarks
    with open(str(PEER_BENCHMARKS_PATH), "w") as f:
        json.dump(benchmarks, f, indent=2)
    print(f"Benchmarks saved to: {PEER_BENCHMARKS_PATH}")

    # Save feature columns
    with open(str(FEATURE_COLUMNS_PATH), "w") as f:
        json.dump(feature_columns, f, indent=2)
    print(f"Feature columns saved to: {FEATURE_COLUMNS_PATH}")

    # Save metrics
    metrics_path = SAVED_MODELS_DIR / "training_metrics.json"
    with open(str(metrics_path), "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {metrics_path}")


def run_full_training_pipeline(data_path: str = None) -> tuple:
    """
    Execute the complete training pipeline:
    1. Load and prepare data
    2. Train model
    3. Compute benchmarks
    4. Save all artifacts

    Returns:
        Tuple of (model, metrics, benchmarks).
    """
    # Load & prepare
    df, feature_columns = load_and_prepare_data(data_path)

    # Train
    model, metrics = train_model(df, feature_columns)

    # Benchmarks
    benchmarks = compute_and_save_benchmarks(
        df, feature_engineer.ENGINEERED_FEATURES
    )

    # Save
    save_artifacts(model, metrics, benchmarks, feature_columns)

    return model, metrics, benchmarks
