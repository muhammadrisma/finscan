import json

from app.core.fish_identification_service import FishIdentificationService
from app.core.text_extraction_service import TextExtractionService
from app.core.file_service import FileService
from app.schema.result_log import ResultLogResponse
from app.db.database import SessionLocal, ProcessingLog, ResultLog
from app.service.cache_service import CacheService
from app.service.audit_service import AuditService

class ProcessingService:
    def __init__(self):
        self.fish_service = FishIdentificationService()
        self.text_service = TextExtractionService()
        self.file_service = FileService()
        self.cache_service = CacheService()
        self.audit_service = AuditService()

    def process_log(self, extracted_fish_name: str):
        """
        Process the input through all three agents and return a structured log.
        Args:
            extracted_fish_name: The extracted fish name to process
        Returns:
            A dictionary containing the processing log with all agent results
        """
        try:
            db = SessionLocal()
            try:
                found_in_cache, cached_latin_name = self.cache_service.get_cached_result(db, extracted_fish_name)
                if found_in_cache:
                    db_log = ProcessingLog(
                        original_description=extracted_fish_name,
                        agent_1_result=json.dumps({"cached": True, "latin_name": cached_latin_name}),
                        agent_2_result=json.dumps({"cached": True, "latin_name": cached_latin_name}),
                        agent_3_result=json.dumps({"cached": True, "latin_name": cached_latin_name})
                    )
                    db.add(db_log)
                    db.commit()
                    db.refresh(db_log)
                    
                    self.audit_service.get_latest_audit_log(db)
                    
                    return {
                        "id": db_log.id,
                        "original_description": extracted_fish_name,
                        "cached_result": True,
                        "fish_name_latin": cached_latin_name
                    }
            finally:
                db.close()

            agent1_response = self.fish_service.agent1(extracted_fish_name)
            agent2_response = self.fish_service.agent2(extracted_fish_name)
            agent3_response = self.fish_service.agent3(extracted_fish_name)

            agent1_result = self.fish_service.extract_agent_content(agent1_response)
            agent2_result = self.fish_service.extract_agent_content(agent2_response)
            agent3_result = self.fish_service.extract_agent_content(agent3_response)

            db = SessionLocal()
            try:
                db_log = ProcessingLog(
                    original_description=extracted_fish_name,
                    agent_1_result=json.dumps(agent1_result.model_dump()),
                    agent_2_result=json.dumps(agent2_result.model_dump()),
                    agent_3_result=json.dumps(agent3_result.model_dump())
                )
                db.add(db_log)
                db.commit()
                db.refresh(db_log)
                
                self.audit_service.get_latest_audit_log(db)
                
                processing_log = {
                    "id": db_log.id,
                    "original_description": extracted_fish_name,
                    "agent_1_result": agent1_result,
                    "agent_2_result": agent2_result,
                    "agent_3_result": agent3_result
                }
    
                filepath = self.file_service.save_processing_log(processing_log, str(db_log.id))
                print(f"Results saved to: {filepath}")

                return processing_log
            finally:
                db.close()
        except Exception as e:
            raise Exception(f"Error in processing log: {str(e)}")

    def process_result_log(self, original_description: str):
        """
        Process the result log and check agent agreement.
        Args:
            original_description: The original product description
        Returns:
            A ResultLogResponse object
        """
        try:
            extracted_fish_name = self.text_service.extract_text(original_description)
            
            db = SessionLocal()
            try:
                found_in_cache, cached_names = self.cache_service.get_cached_result(db, extracted_fish_name)
                if found_in_cache:
                    fish_name_english, fish_name_latin = cached_names
                    
                    db_log = ResultLog(
                        original_description=original_description,
                        extracted_fish_name=extracted_fish_name,
                        fish_name_english=fish_name_english,
                        fish_name_latin=fish_name_latin,
                        flag=True,
                        from_cache=True
                    )
                    db.add(db_log)
                    db.commit()
                    db.refresh(db_log)
                    
                    self.audit_service.get_latest_audit_log(db)
                    
                    result_log = ResultLogResponse(
                        id=db_log.id,
                        original_description=original_description,
                        extracted_fish_name=extracted_fish_name,
                        fish_name_english=fish_name_english,
                        fish_name_latin=fish_name_latin,
                        flag=True,
                        from_cache=True
                    )
                    
                    filepath = self.file_service.save_result_log(result_log, str(db_log.id))
                    print(f"Cached results saved to: {filepath}")
                    
                    return result_log
            finally:
                db.close()

            processing_result = self.process_log(extracted_fish_name)
            
            flag, fish_name_english, fish_name_latin, _ = self.fish_service.check_agent_agreement([
                processing_result["agent_1_result"],
                processing_result["agent_2_result"],
                processing_result["agent_3_result"]
            ])

            db = SessionLocal()
            try:
                db_log = ResultLog(
                    original_description=original_description,
                    extracted_fish_name=extracted_fish_name,
                    fish_name_english=fish_name_english,
                    fish_name_latin=fish_name_latin,
                    flag=flag,
                    from_cache=False
                )
                db.add(db_log)
                db.commit()
                db.refresh(db_log)
                
                if flag:
                    self.cache_service.add_to_cache(db, db_log)
                
                self.audit_service.get_latest_audit_log(db)
                
                result_log = ResultLogResponse(
                    id=db_log.id,
                    original_description=original_description,
                    extracted_fish_name=extracted_fish_name,
                    fish_name_english=fish_name_english,
                    fish_name_latin=fish_name_latin,
                    flag=flag,
                    from_cache=False
                )

                filepath = self.file_service.save_result_log(result_log, str(db_log.id))
                print(f"Results saved to: {filepath}")

                return result_log
            finally:
                db.close()
        except Exception as e:
            raise Exception(f"Error in processing result log: {str(e)}") 