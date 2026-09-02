"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api import upload, analyze, report, export
from importlib import import_module

_data_dir = os.path.join(os.path.dirname(__file__), "..", "data-layer")
sys.path.insert(0, _data_dir)
from storage import database

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
