from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import sys, os

_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data-layer")
sys.path.insert(0, _data_dir)
from storage.database import get_db
from storage import models as db_models
from collectors import csv_uploader

_app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _app_dir)
from schemas import StartupManualEntry

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Handle CSV/Excel file upload."""
    content = await file.read()
    result = csv_uploader.parse_upload(content, file.filename)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
        
    records = csv_uploader.dataframe_to_startup_dicts(result["data"])
    if not records:
        raise HTTPException(status_code=400, detail="No valid records found.")
        
    # Take the first record for the target startup
    record = records[0]
    
    startup = db_models.Startup(**record, is_reference=0)
    db.add(startup)
    db.commit()
    db.refresh(startup)
    
    return {"message": "File uploaded successfully", "startup_id": startup.id}

@router.post("/manual-entry")
def manual_entry(entry: StartupManualEntry, db: Session = Depends(get_db)):
    """Handle manual startup data entry."""
    startup = db_models.Startup(**entry.dict(), is_reference=0)
    db.add(startup)
    db.commit()
    db.refresh(startup)
    return {"message": "Data saved successfully", "startup_id": startup.id}
