import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.setting.setting import LIMIT
from app.db.database import AuditLog, ProcessingLog, ResultLog, CacheLog
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self):
        logger.info("AuditService initialized successfully.")

    def get_latest_audit_log(self, db: Session) -> AuditLog:
        """
        Get the latest audit log entry with current counts.
        If no audit log exists, create a new one.
        """
        logger.info("Getting latest audit log.")
        try:
            # Get the latest audit log
            latest_audit = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
            
            # Get current counts
            total_processing_logs = db.query(ProcessingLog).count()
            total_result_logs = db.query(ResultLog).count()
            total_cache_logs = db.query(CacheLog).count()
            logger.info(f"Current counts: Processing={total_processing_logs}, Result={total_result_logs}, Cache={total_cache_logs}")

            # If no audit log exists or counts have changed, create a new one
            if not latest_audit or (
                latest_audit.total_processing_logs != total_processing_logs or
                latest_audit.total_result_logs != total_result_logs or
                latest_audit.total_cache_logs != total_cache_logs
            ):
                logger.info("Creating new audit log entry.")
                audit_log = AuditLog(
                    total_processing_logs=total_processing_logs,
                    total_result_logs=total_result_logs,
                    total_cache_logs=total_cache_logs
                )
                db.add(audit_log)
                db.commit()
                db.refresh(audit_log)
                logger.info("New audit log entry created.")
                return audit_log
            
            logger.info("Returning existing audit log entry.")
            return latest_audit
        except Exception as e:
            logger.error(f"Error getting latest audit log: {str(e)}", exc_info=True)
            db.rollback()
            # If there's an error, return a default audit log
            return AuditLog(
                id=datetime.now(),
                total_processing_logs=0,
                total_result_logs=0,
                total_cache_logs=0
            )

    def get_top_fish(self, db: Session):
        """Get top N identified fish based on result logs"""
        logger.info("Getting top fish.")
        try:
            top_fish = db.query(
                ResultLog.fish_name_english,
                ResultLog.fish_name_latin,
                func.count(ResultLog.id).label('count')
            ).filter(
                ResultLog.fish_name_english.isnot(None),
                ResultLog.fish_name_latin.isnot(None),
                ResultLog.flag == True
            ).group_by(
                ResultLog.fish_name_english,
                ResultLog.fish_name_latin
            ).order_by(
                func.count(ResultLog.id).desc()
            ).limit(LIMIT).all()

            result = []
            for fish in top_fish:
                result.append({
                    "fish_name_english": fish.fish_name_english,
                    "fish_name_latin": fish.fish_name_latin,
                    "count": fish.count
                })
            logger.info(f"Found {len(result)} top fish.")
            return result
        except Exception as e:
            logger.error(f"Error in get_top_fish: {str(e)}", exc_info=True)
            return [] 