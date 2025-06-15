from pydantic import BaseModel
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: datetime
    total_processing_logs: int
    total_result_logs: int
    total_cache_logs: int 