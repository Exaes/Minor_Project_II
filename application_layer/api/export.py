from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import sys, os
import json

_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data_layer")
sys.path.insert(0, _data_dir)
from storage.database import get_db
from storage import models as db_models

_app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _app_dir)
from services import report_generator

router = APIRouter()

@router.get("/{analysis_id}/pdf")
def export_pdf(analysis_id: int, db: Session = Depends(get_db)):
    """Generate and return a PDF report."""
    analysis = db.query(db_models.AnalysisResult).filter(db_models.AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    startup = analysis.startup
    
    recommendations = analysis.recommendations
    recommendations.sort(key=lambda x: x.rank)
    
    try:
        pdf_path = report_generator.generate_pdf_report(analysis, startup, recommendations)
        return FileResponse(
            pdf_path, 
            media_type="application/pdf", 
            filename=f"Startup_Analysis_{startup.company_name}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
