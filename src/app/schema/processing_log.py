from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ProcessingLogRequest(BaseModel):
    original_description: str
    no_peb: str
    no_seri: str

class AgentResult(BaseModel):
    agent: str
    fish_common_name: str
    latin_name: str
    reasoning: str

class ProcessingLogResponse(BaseModel):
    id: int
    no_peb: str
    no_seri: str
    original_description: str
    agent_1_result: AgentResult
    agent_2_result: AgentResult
    agent_3_result: AgentResult

class ProcessingLogDBResponse(BaseModel):
    id: int
    no_peb: str
    no_seri: str
    original_description: str
    agent_1_result: str  # JSON string
    agent_2_result: str  # JSON string
    agent_3_result: str  # JSON string