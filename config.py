"""
Central configuration and path management.

Resolves the hyphenated-folder-name import problem by providing
a clean config module at the project root.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()

# Layer directories
DATA_LAYER_DIR = PROJECT_ROOT / "data-layer"
PROCESSING_LAYER_DIR = PROJECT_ROOT / "processing-layer"
MODELING_LAYER_DIR = PROJECT_ROOT / "modeling-layer"
APPLICATION_LAYER_DIR = PROJECT_ROOT / "application-layer"
PRESENTATION_LAYER_DIR = PROJECT_ROOT / "presentation-layer"

# Data paths
RAW_DATA_DIR = DATA_LAYER_DIR / "raw"
PROCESSED_DATA_DIR = DATA_LAYER_DIR / "processed"
TEMPLATES_DIR = DATA_LAYER_DIR / "templates"

# Model paths
SAVED_MODELS_DIR = MODELING_LAYER_DIR / "saved_models"
BENCHMARK_MODEL_PATH = SAVED_MODELS_DIR / "benchmark_model.joblib"
PEER_BENCHMARKS_PATH = SAVED_MODELS_DIR / "peer_benchmarks.json"
FEATURE_COLUMNS_PATH = SAVED_MODELS_DIR / "feature_columns.json"

# Reference dataset
REFERENCE_DATASET_PATH = RAW_DATA_DIR / "reference_startups.csv"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'startup_analysis.db'}")

# LLM
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
