"""
CLI script to train the benchmarking model.

Usage:
    python scripts/train_model.py
    python scripts/train_model.py --data path/to/custom_dataset.csv
"""

import os
import sys
import argparse

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from config import REFERENCE_DATASET_PATH


def main():
    parser = argparse.ArgumentParser(description="Train the startup benchmarking model")
    parser.add_argument(
        "--data", type=str, default=str(REFERENCE_DATASET_PATH),
        help="Path to the reference dataset CSV"
    )
    args = parser.parse_args()

    # Check if data exists
    if not os.path.exists(args.data):
        print(f"Dataset not found: {args.data}")
        print("Run 'python scripts/generate_synthetic_data.py' first.")
        sys.exit(1)

    # Import and run training pipeline
    _modeling_dir = os.path.join(PROJECT_ROOT, "modeling-layer")
    sys.path.insert(0, _modeling_dir)
    import train_benchmark_model

    print("=" * 60)
    print("STARTUP BENCHMARKING MODEL TRAINING")
    print("=" * 60)

    model, metrics, benchmarks = train_benchmark_model.run_full_training_pipeline(args.data)

    print(f"\n{'='*60}")
    print("TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Peer groups: {len(benchmarks) - 1}")  # -1 for _global
    print(f"Model accuracy: {metrics['accuracy']:.4f}")
    print(f"Model F1: {metrics['f1_score']:.4f}")
    print(f"Model ROC-AUC: {metrics['roc_auc']:.4f}")


if __name__ == "__main__":
    main()
