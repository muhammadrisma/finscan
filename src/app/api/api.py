from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.schema.processing_log import ProcessingLogRequest, ProcessingLogResponse, ProcessingLogDBResponse
from app.schema.result_log import ResultLogRequest, ResultLogResponse, ResultLogDBResponse
from app.schema.audit_log import AuditLogResponse
from app.schema.top_fish import TopFishResponse
from app.service.processing_service import ProcessingService
from app.service.audit_service import AuditService
from app.db.database import get_db, ProcessingLog, ResultLog, CacheLog

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

processing_service = ProcessingService()
audit_service = AuditService()

@router.post("/processing/log", response_model=ProcessingLogResponse)
async def create_processing_log(request: ProcessingLogRequest, db: Session = Depends(get_db)):
    """
    Create a new processing log by running the input through all agents.
    """
    try:
        result = processing_service.process_log(
            request.original_description,
            request.no_peb,
            request.no_seri
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing/logs", response_model=List[ProcessingLogDBResponse])
async def get_processing_logs(db: Session = Depends(get_db)):
    """
    Get all processing logs from the database.
    """
    try:
        logs = db.query(ProcessingLog).all()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing/log/{log_id}", response_model=ProcessingLogDBResponse)
async def get_processing_log(log_id: int, db: Session = Depends(get_db)):
    """
    Get a specific processing log by ID.
    """
    try:
        log = db.query(ProcessingLog).filter(ProcessingLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Processing log not found")
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/result/log", response_model=ResultLogResponse)
async def create_result_log(request: ResultLogRequest, db: Session = Depends(get_db)):
    """
    Create a new result log with agent agreement check.
    """
    try:
        result = processing_service.process_result_log(
            request.original_description,
            request.no_peb,
            request.no_seri
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/logs", response_model=List[ResultLogDBResponse])
async def get_result_logs(db: Session = Depends(get_db)):
    """
    Get all result logs from the database.
    """
    try:
        logs = db.query(ResultLog).all()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/log/{log_id}", response_model=ResultLogDBResponse)
async def get_result_log(log_id: int, db: Session = Depends(get_db)):
    """
    Get a specific result log by ID.
    """
    try:
        log = db.query(ResultLog).filter(ResultLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Result log not found")
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/processing/log/{log_id}")
async def delete_processing_log(log_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific processing log by ID.
    """
    try:
        log = db.query(ProcessingLog).filter(ProcessingLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Processing log not found")
        db.delete(log)
        db.commit()
        return {"message": "Processing log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/result/log/{log_id}")
async def delete_result_log(log_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific result log by ID.
    """
    try:
        log = db.query(ResultLog).filter(ResultLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Result log not found")
        db.delete(log)
        db.commit()
        return {"message": "Result log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/latest", response_model=AuditLogResponse)
async def get_latest_audit_log(db: Session = Depends(get_db)):
    """
    Get the latest audit log entry with current counts.
    """
    try:
        audit_log = audit_service.get_latest_audit_log(db)
        return {
            "id": audit_log.id,
            "total_processing_logs": audit_log.total_processing_logs,
            "total_result_logs": audit_log.total_result_logs,
            "total_cache_logs": audit_log.total_cache_logs
        }
    except Exception as e:
        logger.error(f"Error getting latest audit log: {str(e)}")
        return {
            "id": datetime.now(),
            "total_processing_logs": 0,
            "total_result_logs": 0,
            "total_cache_logs": 0
        }

@router.get("/cache/logs", response_model=List[dict])
async def get_cache_logs(db: Session = Depends(get_db)):
    """
    Get all cache logs from the database.
    """
    try:
        logs = db.query(CacheLog).all()
        return [
            {
                "id": log.id,
                "extracted_fish_name": log.extracted_fish_name,
                "fish_name_english": log.fish_name_english,
                "fish_name_latin": log.fish_name_latin
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/top-fish", response_model=TopFishResponse)
async def get_top_fish(db: Session = Depends(get_db)):
    """
    Get the top 5 most frequently identified fish.
    """
    try:
        top_fish = audit_service.get_top_fish(db)
        if not top_fish:
            return {"items": []}
        
        formatted_items = []
        for fish in top_fish:
            item = {
                "fish_name_english": fish["fish_name_english"],
                "fish_name_latin": fish["fish_name_latin"],
                "count": fish["count"]
            }
            formatted_items.append(item)
        
        return {"items": formatted_items}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching top fish data: {str(e)}"
        )