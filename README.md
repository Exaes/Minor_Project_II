# AI-Driven Startup Analysis & Business Recommendation System

An end-to-end prototype that ingests a target startup's operational and financial data, benchmarks it against patterns learned from a dataset of successful startups, and produces a prioritised, explainable set of business recommendations — delivered through an interactive dashboard.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (Streamlit)                    │
│   Upload UI  │  Analysis Dashboard  │  Recommendation Report        │
├─────────────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER (FastAPI)                       │
│   /upload  │  /analyze  │  /report  │  /export/pdf                  │
├─────────────────────────────────────────────────────────────────────┤
│                     MODELING LAYER                                   │
│   LightGBM Benchmark Model  │  LLM Recommendation Engine           │
├─────────────────────────────────────────────────────────────────────┤
│                    PROCESSING LAYER                                  │
│   Cleaner  │  Normalizer  │  Feature Engineer  │  Peer Grouper      │
├─────────────────────────────────────────────────────────────────────┤
│                      DATA LAYER                                      │
│   CSV/Excel Uploader  │  Dataset Loader  │  SQLite Storage          │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Local Setup

```bash
# 1. Clone and install
cd "MINI project"
pip install -r requirements.txt

# 2. Set up environment
copy .env.example .env
# Edit .env — add HF_API_TOKEN if you want LLM recommendations (optional)

# 3. Generate reference data & train model
python scripts/generate_synthetic_data.py
python scripts/train_model.py

# 4. Start the backend API
python -m uvicorn application-layer.main:app --host 0.0.0.0 --port 8000

# 5. Start the dashboard (in a new terminal)
streamlit run presentation-layer/app.py --server.port 8501
```

### Option 2: Docker Compose

```bash
docker-compose up --build
```

Then open:
- **Dashboard**: http://localhost:8501
- **API docs**: http://localhost:8000/docs

---

## Project Structure

```
├── data-layer/              # Data ingestion, storage, templates
│   ├── collectors/          # Dataset loader, CSV/Excel uploader
│   ├── storage/             # SQLAlchemy models, database engine
│   ├── raw/                 # Raw data files
│   ├── processed/           # Cleaned/engineered data
│   └── templates/           # Upload template CSV
│
├── processing-layer/        # Data cleaning, feature engineering
│   ├── cleaner.py           # Missing values, outliers, type coercion
│   ├── normalizer.py        # Scaling, log transforms
│   ├── feature_engineer.py  # 15+ financial/operational metrics
│   └── peer_grouper.py      # Industry-stage-size peer bucketing
│
├── modeling-layer/          # ML models + LLM integration
│   ├── train_benchmark_model.py  # Train LightGBM success-pattern model
│   ├── scorer.py            # Score startups, compute deviations
│   ├── llm/                 # LLM prompt templates + generators
│   └── saved_models/        # Serialized models (joblib)
│
├── application-layer/       # FastAPI backend
│   ├── main.py              # App entry point
│   ├── api/                 # REST endpoints
│   ├── services/            # Pipeline orchestration, PDF generation
│   └── schemas.py           # Pydantic request/response models
│
├── presentation-layer/      # Streamlit dashboard
│   ├── app.py               # Main app entry point
│   ├── pages/               # Multi-page UI (Upload, Dashboard, Recommendations)
│   └── components/          # Charts, styling
│
├── scripts/                 # CLI utilities
│   ├── generate_synthetic_data.py
│   ├── train_model.py
│   └── seed_db.py
│
└── tests/                   # Pytest test suite
```

## Key Metrics Computed

| Category | Metrics |
|---|---|
| Financial Efficiency | Gross margin, OpEx-to-revenue, burn rate, runway (months) |
| Growth & Traction | MoM/YoY revenue growth, customer growth rate |
| Unit Economics | CAC, LTV, LTV:CAC ratio, payback period |
| Operational Efficiency | Revenue per employee, headcount vs revenue growth |
| Funding Efficiency | Capital raised vs revenue, funding efficiency ratio |

## Recommendation Engine

Recommendations are **constrained and explainable**, not free-form LLM output:

1. **Deviation Detection** — z-score/percentile vs peer-group benchmarks
2. **Prioritisation** — ranked by estimated financial impact
3. **Grounded Generation** — LLM explains deviations using actual computed numbers
4. **Actionability Tags** — Cost-cutting / Margin improvement / Growth efficiency / Hiring pace

## Model Training & Evaluation

```bash
# Train and evaluate
python scripts/train_model.py

# Expected metrics:
# Accuracy: > 0.75
# F1 Score: > 0.70
# ROC-AUC:  > 0.80
```

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| ML Modeling | LightGBM, scikit-learn |
| LLM | HuggingFace Inference API (Mistral-7B) + rule-based fallback |
| Backend | FastAPI + Uvicorn |
| Database | SQLite (SQLAlchemy ORM) |
| Frontend | Streamlit + Plotly |
| PDF Export | fpdf2 |
| Deployment | Docker Compose |

## License

This project is a B.Tech mini-project prototype for educational purposes.
