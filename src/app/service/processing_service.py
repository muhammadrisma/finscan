from app.core.fish_identification_service import FishIdentificationService
from app.core.text_extraction_service import TextExtractionService
from app.core.file_service import FileService
from app.schema.result_log import ResultLogResponse

class ProcessingService:
    def __init__(self):
        self.fish_service = FishIdentificationService()
        self.text_service = TextExtractionService()
        self.file_service = FileService()

    def process_log(self, id: str, extracted_fish_name: str):
        """
        Process the input through all three agents and return a structured log.
        Args:
            id: The unique identifier for the log entry
            extracted_fish_name: The extracted fish name to process
        Returns:
            A dictionary containing the processing log with all agent results
        """
        try:
            # Process through all three agents
            agent1_response = self.fish_service.agent1(extracted_fish_name)
            agent2_response = self.fish_service.agent2(extracted_fish_name)
            agent3_response = self.fish_service.agent3(extracted_fish_name)

            # Extract content from each agent's response
            agent1_result = self.fish_service.extract_agent_content(agent1_response)
            agent2_result = self.fish_service.extract_agent_content(agent2_response)
            agent3_result = self.fish_service.extract_agent_content(agent3_response)

            # Create the processing log
            processing_log = {
                "id": id,
                "original_description": extracted_fish_name,
                "agent_1_result": agent1_result,
                "agent_2_result": agent2_result,
                "agent_3_result": agent3_result
            }

            # Save results to file
            filepath = self.file_service.save_processing_log(processing_log, id)
            print(f"Results saved to: {filepath}")

            return processing_log
        except Exception as e:
            raise Exception(f"Error in processing log: {str(e)}")

    def process_result_log(self, id: str, original_description: str) -> ResultLogResponse:
        """
        Process the input and create a result log with agent agreement check.
        Args:
            id: The unique identifier for the log entry
            original_description: The original product description
        Returns:
            ResultLogResponse containing the processed results
        """
        try:
            # First extract fish name from the input
            extracted_fish_name = self.text_service.extract_text(original_description)
            
            # Then get the processing log using the extracted fish name
            processing_log = self.process_log(id, extracted_fish_name)
            
            # Get agent results
            agent_results = [
                processing_log["agent_1_result"],
                processing_log["agent_2_result"],
                processing_log["agent_3_result"]
            ]
            
            # Check agent agreement
            flag, fish_name_english, fish_name_latin, _ = self.fish_service.check_agent_agreement(agent_results)
            
            # Create result log
            result_log = ResultLogResponse(
                id=id,
                original_description=original_description,
                extracted_fish_name=extracted_fish_name,
                fish_name_english=fish_name_english,
                fish_name_latin=fish_name_latin,
                flag=flag
            )
            
            # Save result log to file
            filepath = self.file_service.save_result_log(result_log, id)
            print(f"Result log saved to: {filepath}")
            
            return result_log
        except Exception as e:
            raise Exception(f"Error in processing result log: {str(e)}") 