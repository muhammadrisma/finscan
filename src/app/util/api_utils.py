import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

def create_llm_request(prompt: str, model: str) -> dict:
    """
    Create a standardized LLM API request.
    """
    if not api_key or not api_base:
        raise ValueError("Missing required environment variables for API key or base URL.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = api_base.rstrip("/") + "/api/v1/chat/completions"

    return {
        "url": url,
        "payload": payload,
        "headers": headers
    }

def make_llm_request(request_data: dict) -> dict:
    """
    Make an LLM API request and return the response.
    """
    try:
        response = requests.post(
            request_data["url"],
            json=request_data["payload"],
            headers=request_data["headers"]
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error making LLM request: {str(e)}") 