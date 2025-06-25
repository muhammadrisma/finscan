import logging
from sqlalchemy.orm import Session
from app.db.database import CacheLog, ResultLog

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        logger.info("CacheService initialized successfully.")

    def get_cached_result(self, db: Session, extracted_fish_name: str) -> tuple[bool, tuple[str, str, str] | None]:
        """
        Check if the extracted fish name exists in cache and return the cached result if found.
        
        Args:
            db: Database session
            extracted_fish_name: The extracted fish name to look up
            
        Returns:
            Tuple of (found_in_cache: bool, (fish_name_english: str, fish_name_latin: str, extracted_fish_name: str) | None)
        """
        logger.info(f"Checking cache for extracted fish name: '{extracted_fish_name}'")
        try:
            cached_entry = db.query(CacheLog).filter(
                CacheLog.extracted_fish_name == extracted_fish_name
            ).first()
            
            if cached_entry:
                logger.info(f"Cache hit for '{extracted_fish_name}'.")
                return True, (
                    cached_entry.fish_name_english,
                    cached_entry.fish_name_latin,
                    cached_entry.extracted_fish_name
                )
            
            logger.info(f"Cache miss for '{extracted_fish_name}'.")
            return False, None
        except Exception as e:
            logger.error(f"Error getting cached result for '{extracted_fish_name}': {str(e)}", exc_info=True)
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
        
        logger.info(f"Attempting to add result to cache for extracted fish name: '{result_log.extracted_fish_name}'")
        try:
            existing = db.query(CacheLog).filter(
                CacheLog.extracted_fish_name == result_log.extracted_fish_name
            ).first()
            
            if existing:
                logger.info(f"Cache entry for '{result_log.extracted_fish_name}' already exists. Skipping.")
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
            logger.info(f"Successfully added cache entry for '{result_log.extracted_fish_name}'.")
        except Exception as e:
            logger.error(f"Error adding to cache for '{result_log.extracted_fish_name}': {str(e)}", exc_info=True)
            db.rollback() 