import json
import time
import logging

from app.core.fish_identification_service import FishIdentificationService
from app.core.text_extraction_service import TextExtractionService
from app.core.file_service import FileService
from app.schema.result_log import ResultLogResponse
from app.db.database import SessionLocal, ProcessingLog, ResultLog
from app.service.cache_service import CacheService
from app.service.audit_service import AuditService

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self):
        self.fish_service = FishIdentificationService()
        self.text_service = TextExtractionService()
        self.file_service = FileService()
        self.cache_service = CacheService()
        self.audit_service = AuditService()
        logger.info("ProcessingService initialized successfully.")

    def process_log(self, extracted_fish_name: str, no_peb: str, no_seri: str):
        """
        Process the input through all three agents and return a structured log.
        Temporarily save results to file instead of DB.
        """
        logger.info(f"Processing log for extracted fish name: '{extracted_fish_name}', PEB: '{no_peb}', SERI: '{no_seri}'")
        try:
            # Simulate an ID using timestamp
            temp_id = str(int(time.time() * 1000))
            # db = SessionLocal()
            # try:
            #     found_in_cache, cached_result = self.cache_service.get_cached_result(db, extracted_fish_name)
            #     if found_in_cache:
            #         fish_name_english, fish_name_latin, cached_fish_name = cached_result
            #         db_log = ProcessingLog(
            #             original_description=extracted_fish_name,
            #             no_peb=no_peb,
            #             no_seri=no_seri,
            #             agent_1_result=json.dumps({
            #                 "cached": True,
            #                 "fish_common_name": fish_name_english,
            #                 "latin_name": fish_name_latin,
            #                 "extracted_fish_name": cached_fish_name
            #             }),
            #             agent_2_result=json.dumps({
            #                 "cached": True,
            #                 "fish_common_name": fish_name_english,
            #                 "latin_name": fish_name_latin,
            #                 "extracted_fish_name": cached_fish_name
            #             }),
            #             agent_3_result=json.dumps({
            #                 "cached": True,
            #                 "fish_common_name": fish_name_english,
            #                 "latin_name": fish_name_latin,
            #                 "extracted_fish_name": cached_fish_name
            #             })
            #         )
            #         db.add(db_log)
            #         db.commit()
            #         db.refresh(db_log)
                    
            #         self.audit_service.get_latest_audit_log(db)
                    
            #         return {
            #             "id": db_log.id,
            #             "no_peb": no_peb,
            #             "no_seri": no_seri,
            #             "original_description": extracted_fish_name,
            #             "cached_result": True,
            #             "fish_name_english": fish_name_english,
            #             "fish_name_latin": fish_name_latin,
            #             "extracted_fish_name": cached_fish_name
            #         }
            # finally:
            #     db.close()
            logger.info("Calling agents for fish identification.")
            agent1_response = self.fish_service.agent1(extracted_fish_name)
            agent2_response = self.fish_service.agent2(extracted_fish_name)
            agent3_response = self.fish_service.agent3(extracted_fish_name)
            logger.info("Received responses from all agents.")

            logger.info("Extracting content from agent responses.")
            agent1_result = self.fish_service.extract_agent_content(agent1_response)
            agent2_result = self.fish_service.extract_agent_content(agent2_response)
            agent3_result = self.fish_service.extract_agent_content(agent3_response)
            logger.info("Successfully extracted content from all agent responses.")
            db = SessionLocal()
            # try:
            #     db_log = ProcessingLog(
            #         original_description=extracted_fish_name,
            #         no_peb=no_peb,
            #         no_seri=no_seri,
            #         agent_1_result=json.dumps(agent1_result.model_dump()),
            #         agent_2_result=json.dumps(agent2_result.model_dump()),
            #         agent_3_result=json.dumps(agent3_result.model_dump())
            #     )
            #     db.add(db_log)
            #     db.commit()
            #     db.refresh(db_log)
                
            #     self.audit_service.get_latest_audit_log(db)
            processing_log = {
                "id": temp_id,
                "no_peb": no_peb,
                "no_seri": no_seri,
                "original_description": extracted_fish_name,
                "agent_1_result": agent1_result,
                "agent_2_result": agent2_result,
                "agent_3_result": agent3_result
            }

            self.file_service.save_processing_log(processing_log, temp_id)
            logger.info(f"Successfully processed log for extracted fish name: '{extracted_fish_name}'.")
            return processing_log
            # finally:
            #     db.close()
        except Exception as e:
            logger.error(f"Error in process_log for '{extracted_fish_name}': {str(e)}", exc_info=True)
            raise Exception(f"Error in processing log: {str(e)}")

    def process_result_log(self, original_description: str, no_peb: str, no_seri: str):
        """
        Process the result log and check agent agreement.
        Temporarily save results to file instead of DB.
        """
        logger.info(f"Processing result log for description: '{original_description}', PEB: '{no_peb}', SERI: '{no_seri}'")
        try:
            # Simulate an ID using timestamp
            temp_id = str(int(time.time() * 1000))
            logger.info("Extracting fish name from description.")
            extracted_fish_name = self.text_service.extract_text(original_description)
            logger.info(f"Extracted fish name: '{extracted_fish_name}'")

            processing_result = self.process_log(extracted_fish_name, no_peb, no_seri)

            logger.info("Checking agent agreement.")
            flag, fish_name_english, fish_name_latin, _ = self.fish_service.check_agent_agreement([
                processing_result["agent_1_result"],
                processing_result["agent_2_result"],
                processing_result["agent_3_result"]
            ])
            logger.info(f"Agent agreement check completed. Flag: {flag}, English: '{fish_name_english}', Latin: '{fish_name_latin}'")

            result_log = ResultLogResponse(
                id=temp_id,
                no_peb=no_peb,
                no_seri=no_seri,
                original_description=original_description,
                extracted_fish_name=extracted_fish_name,
                fish_name_english=fish_name_english,
                fish_name_latin=fish_name_latin,
                flag=flag,
                from_cache=False
            )
            self.file_service.save_result_log(result_log, temp_id)
            logger.info(f"Successfully processed result log for description: '{original_description}'.")
            return result_log
        except Exception as e:
            logger.error(f"Error in process_result_log for '{original_description}': {str(e)}", exc_info=True)
            raise Exception(f"Error in processing result log: {str(e)}") 