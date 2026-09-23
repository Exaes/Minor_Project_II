"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os

# Add project root and app dir to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

_app_dir = os.path.dirname(__file__)
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

_data_dir = os.path.join(PROJECT_ROOT, "data_layer")
if _data_dir not in sys.path:
    sys.path.insert(0, _data_dir)

from application_layer.api import upload, analyze, report, export
from data_layer.storage import database

# Initialize database tables
database.init_db()

app = FastAPI(
    title="Startup Analysis API",
    description="API for the AI-Driven Startup Analysis & Business Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analyze"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
