import os
import logging
from dotenv import load_dotenv
from app.setting.setting import AGENT_EXTRACT_TEXT
from app.util.load_prompt import load_prompt
from app.util.api_utils import create_llm_request, make_llm_request

load_dotenv()

logger = logging.getLogger(__name__)

extract_text_prompt = load_prompt('extract_text')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

class TextExtractionService:
    def __init__(self):
        if not api_key or not api_base:
            logger.error("Missing required environment variables for API key or base URL.")
            raise ValueError("Missing required environment variables for API key or base URL.")
        logger.info("TextExtractionService initialized successfully.")

    def create_agent(self, prompt_template: str, input_text: dict, model: str):
        """Create an agent with the specified prompt template and model."""
        logger.info(f"Creating text extraction agent with model: {model}")
        prompt = prompt_template
        for k, v in input_text.items():
            prompt = prompt.replace(f"{{{{ {k} }}}}", str(v))
        request_data = create_llm_request(prompt, model)
        try:
            response = make_llm_request(request_data)
            logger.info(f"Successfully received response from text extraction agent {model}.")
            return response
        except Exception as e:
            logger.error(f"Error during text extraction agent call with model {model}: {str(e)}")
            raise

    def extract_text(self, text: str) -> str:
        """Extract fish name from product description."""
        logger.info("Starting fish name extraction from product description.")
        try:
            response = self.create_agent(extract_text_prompt, {"product_description": text}, AGENT_EXTRACT_TEXT)
            content = response['choices'][0]['message']['content']
            logger.info(f"Successfully extracted fish name: {content.strip()}")
            return content.strip()
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting content from text extraction agent response: {str(e)}")
            raise Exception("Error parsing agent response")
        except Exception as e:
            logger.error(f"An unexpected error occurred during fish name extraction: {str(e)}")
            raise 