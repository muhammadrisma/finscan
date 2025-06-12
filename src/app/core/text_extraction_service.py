import os
from dotenv import load_dotenv
from app.setting.setting import AGENT_EXTRACT_TEXT
from app.util.load_prompt import load_prompt
from app.util.api_utils import create_llm_request, make_llm_request

load_dotenv()

# Load prompts
extract_text_prompt = load_prompt('extract_text')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

class TextExtractionService:
    def __init__(self):
        if not api_key or not api_base:
            raise ValueError("Missing required environment variables for API key or base URL.")

    def create_agent(self, prompt_template: str, input_text: dict, model: str):
        """Create an agent with the specified prompt template and model."""
        prompt = prompt_template
        for k, v in input_text.items():
            prompt = prompt.replace(f"{{{{ {k} }}}}", str(v))
        request_data = create_llm_request(prompt, model)
        return make_llm_request(request_data)

    def extract_text(self, text: str) -> str:
        """Extract fish name from product description."""
        response = self.create_agent(extract_text_prompt, {"product_description": text}, AGENT_EXTRACT_TEXT)
        content = response['choices'][0]['message']['content']
        return content.strip() 