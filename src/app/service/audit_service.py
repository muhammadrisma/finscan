from sqlalchemy.orm import Session
from app.db.database import AuditLog, ProcessingLog, ResultLog, CacheLog

class AuditService:
    def __init__(self):
        pass

    def get_latest_audit_log(self, db: Session) -> AuditLog:
        """
        Get the latest audit log entry with current counts.
        """
        total_processing_logs = db.query(ProcessingLog).count()
        total_result_logs = db.query(ResultLog).count()
        total_cache_logs = db.query(CacheLog).count()

        audit_log = AuditLog(
            total_processing_logs=total_processing_logs,
            total_result_logs=total_result_logs,
            total_cache_logs=total_cache_logs
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log 