from pydantic import BaseModel
from typing import Dict, Any

class ProcessingLogRequest(BaseModel):
    id: str
    original_description: str

class ProcessingLogResponse(BaseModel):
    id: str
    original_description: str
    agent_1_result: Dict[str, Any]
    agent_2_result: Dict[str, Any]
    agent_3_result: Dict[str, Any] 