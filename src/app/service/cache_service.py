from sqlalchemy.orm import Session
from app.db.database import CacheLog, ResultLog

class CacheService:
    def __init__(self):
        pass

    def get_cached_result(self, db: Session, extracted_fish_name: str) -> tuple[bool, tuple[str, str] | None]:
        """
        Check if the extracted fish name exists in cache and return the cached result if found.
        
        Args:
            db: Database session
            extracted_fish_name: The extracted fish name to look up
            
        Returns:
            Tuple of (found_in_cache: bool, (fish_name_english: str, fish_name_latin: str) | None)
        """
        cached_entry = db.query(CacheLog).filter(
            CacheLog.extracted_fish_name == extracted_fish_name
        ).first()
        
        if cached_entry:
            return True, (cached_entry.fish_name_english, cached_entry.fish_name_latin)
        return False, None

    def add_to_cache(self, db: Session, result_log: ResultLog) -> None:
        """
        Add a new entry to the cache if the result log has flag=True.
        
        Args:
            db: Database session
            result_log: The ResultLog entry to cache
        """
        if not result_log.flag:
            return
                    
        existing = db.query(CacheLog).filter(
            CacheLog.extracted_fish_name == result_log.extracted_fish_name
        ).first()
        
        if existing:
            return
            
        cache_entry = CacheLog(
            id=result_log.id,
            extracted_fish_name=result_log.extracted_fish_name,
            fish_name_english=result_log.fish_name_english,
            fish_name_latin=result_log.fish_name_latin,
            result_log_id=result_log.id
        )
        
        db.add(cache_entry)
        db.commit() 