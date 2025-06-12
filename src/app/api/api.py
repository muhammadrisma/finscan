from fastapi import APIRouter, HTTPException
from app.schema.processing_log import ProcessingLogRequest, ProcessingLogResponse
from app.schema.result_log import ResultLogRequest, ResultLogResponse
from app.service.processing_service import ProcessingService

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

processing_service = ProcessingService()

@router.post("/processing/log", response_model=ProcessingLogResponse)
async def create_processing_log(request: ProcessingLogRequest):
    """
    Create a new processing log by running the input through all agents.
    """
    try:
        result = processing_service.process_log(request.id, request.original_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/result/log", response_model=ResultLogResponse)
async def create_result_log(request: ResultLogRequest):
    """
    Create a new result log with agent agreement check.
    """
    try:
        result = processing_service.process_result_log(request.id, request.original_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 