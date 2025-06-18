from sqlalchemy.orm import Session
from app.db.database import AuditLog, ProcessingLog, ResultLog, CacheLog
from datetime import datetime

class AuditService:
    def __init__(self):
        pass

    def get_latest_audit_log(self, db: Session) -> AuditLog:
        """
        Get the latest audit log entry with current counts.
        If no audit log exists, create a new one.
        """
        try:
            # Get the latest audit log
            latest_audit = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
            
            # Get current counts
            total_processing_logs = db.query(ProcessingLog).count()
            total_result_logs = db.query(ResultLog).count()
            total_cache_logs = db.query(CacheLog).count()

            # If no audit log exists or counts have changed, create a new one
            if not latest_audit or (
                latest_audit.total_processing_logs != total_processing_logs or
                latest_audit.total_result_logs != total_result_logs or
                latest_audit.total_cache_logs != total_cache_logs
            ):
                audit_log = AuditLog(
                    total_processing_logs=total_processing_logs,
                    total_result_logs=total_result_logs,
                    total_cache_logs=total_cache_logs
                )
                db.add(audit_log)
                db.commit()
                db.refresh(audit_log)
                return audit_log
            
            return latest_audit
        except Exception as e:
            # If there's an error, return a default audit log
            return AuditLog(
                id=datetime.now(),
                total_processing_logs=0,
                total_result_logs=0,
                total_cache_logs=0
            ) 