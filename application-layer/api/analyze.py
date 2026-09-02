from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys, os

_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data-layer")
sys.path.insert(0, _data_dir)
from storage.database import get_db
from storage import models as db_models

_app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _app_dir)
from services import pipeline

router = APIRouter()

@router.post("/{startup_id}")
def analyze_startup(startup_id: int, use_llm: bool = True, db: Session = Depends(get_db)):
    """Trigger the analysis pipeline for a startup."""
    startup = db.query(db_models.Startup).filter(db_models.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
        
    try:
        analysis_id = pipeline.run_analysis_pipeline(db, startup_id, use_llm=use_llm)
        return {"message": "Analysis complete", "analysis_id": analysis_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
