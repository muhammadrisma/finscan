import os
import json
from datetime import datetime

from app.schema.processing_log import AgentResult
from app.schema.result_log import ResultLogResponse

class FileService:
    def __init__(self):
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        os.makedirs(self.results_dir, exist_ok=True)

    def convert_to_dict(self, obj):
        """Convert objects to dictionaries for JSON serialization."""
        if isinstance(obj, AgentResult):
            return obj.model_dump()
        return obj

    def save_processing_log(self, data: dict, id: str) -> str:
        """Save the processing log results to a text file."""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"process_log_{id}_{timestamp}.txt"
            filepath = os.path.join(self.results_dir, filename)

            # Convert AgentResult objects to dictionaries
            serializable_data = {
                "id": data["id"],
                "original_description": data["original_description"],
                "agent_1_result": self.convert_to_dict(data["agent_1_result"]),
                "agent_2_result": self.convert_to_dict(data["agent_2_result"]),
                "agent_3_result": self.convert_to_dict(data["agent_3_result"])
            }

            # Format the data for better readability
            formatted_data = json.dumps(serializable_data, indent=2)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_data)

            return filepath
        except Exception as e:
            raise Exception(f"Error saving results to file: {str(e)}")

    def save_result_log(self, data: ResultLogResponse, id: str) -> str:
        """Save the result log to a text file."""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_log_{id}_{timestamp}.txt"
            filepath = os.path.join(self.results_dir, filename)

            # Convert to dictionary and format the data
            formatted_data = json.dumps(data.model_dump(), indent=2)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_data)

            return filepath
        except Exception as e:
            raise Exception(f"Error saving result log to file: {str(e)}") 