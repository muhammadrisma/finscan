from fastapi import APIRouter, HTTPException
from app.schema.processing_log import ProcessingLogRequest, ProcessingLogResponse
from app.api.agent import process_log

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

@router.post("/processing/log", response_model=ProcessingLogResponse)
async def create_processing_log(request: ProcessingLogRequest):
    """
    Create a new processing log by running the input through all agents.
    """
    try:
        result = process_log(request.id, request.original_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 