from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys, os
import json

_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data-layer")
sys.path.insert(0, _data_dir)
from storage.database import get_db
from storage import models as db_models

_app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _app_dir)
from schemas import AnalysisResponse

router = APIRouter()

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_report(analysis_id: int, db: Session = Depends(get_db)):
    """Fetch full analysis result."""
    analysis = db.query(db_models.AnalysisResult).filter(db_models.AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    startup = analysis.startup
    
    recommendations = []
    for rec in analysis.recommendations:
        recommendations.append({
            "rank": rec.rank,
            "title": rec.title,
            "category": rec.category,
            "impact_level": rec.impact_level,
            "explanation": rec.explanation,
            "supporting_data": json.loads(rec.supporting_data_json)
        })
        
    recommendations.sort(key=lambda x: x["rank"])

    return {
        "analysis_id": analysis.id,
        "startup_id": analysis.startup_id,
        "company_name": startup.company_name,
        "efficiency_score": analysis.efficiency_score,
        "peer_group_label": analysis.peer_group_label,
        "computed_metrics": json.loads(analysis.computed_metrics_json),
        "peer_benchmarks": json.loads(analysis.peer_benchmarks_json),
        "deviations": json.loads(analysis.deviations_json),
        "recommendations": recommendations
    }
