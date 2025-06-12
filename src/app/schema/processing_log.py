from pydantic import BaseModel
from typing import Dict, Any, List

class ProcessingLogRequest(BaseModel):
    id: str
    original_description: str

class AgentResult(BaseModel):
    agent: str
    fish_common_name: str
    latin_name: str
    reasoning: str

class ProcessingLogResponse(BaseModel):
    id: str
    original_description: str
    agent_1_result: AgentResult
    agent_2_result: AgentResult
    agent_3_result: AgentResult