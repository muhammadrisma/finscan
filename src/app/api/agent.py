import os
from dotenv import load_dotenv
import requests

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.setting.setting import AGENT_EXTRACT_TEXT, AGENT1, AGENT2, AGENT3
from app.util.load_prompt import load_prompt

load_dotenv()

# Load prompts
agent_prompt = load_prompt('agent')
extract_text_prompt = load_prompt('extract_text')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")


def get_model_display_name(model: str) -> str:
    """
    Get a human-readable display name for the model.
    Args:
        model: The model identifier
    Returns:
        A human-readable name for the model
    """
    model_names = {
        "gpt-4o-mini": "GPT-4o-mini",
        "claude-3.7-sonnet": "Claude 3.7 Sonnet",
        "deepseek-v3-0324": "DeepSeek V3 0324"
    }
    return model_names.get(model, model)


def create_agent(prompt_template: str, input_text: dict, model: str):
    """
    Create an agent with the specified prompt template and model.
    Args:
        prompt_template: The prompt template to use
        input_text: The input text to process as a dictionary
        model: The model to use
    Returns:
        The processed response from the agent
    Raises:
        ValueError: If required environment variables are missing
        Exception: For other API or processing errors
    """
    if not api_key or not api_base:
        raise ValueError("Missing required environment variables for API key or base URL.")

    # Render the prompt with input_text
    prompt = prompt_template
    for k, v in input_text.items():
        prompt = prompt.replace(f"{{{{ {k} }}}}", str(v))

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

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error creating agent: {str(e)}")


def extract_text(text: str):
    """
    Extract fish name from product description.
    Args:
        text: The product description text
    Returns:
        The extracted fish name
    """
    return create_agent(extract_text_prompt, {"product_description": text}, AGENT_EXTRACT_TEXT)


def agent1(input_text: str):
    """
    Create an agent using the model specified in AGENT1 setting.
    Args:
        input_text: The input text to process
    Returns:
        The answer from the agent
    """
    return create_agent(agent_prompt, {
        "agent_name": get_model_display_name(AGENT1),
        "fish_input": input_text
    }, AGENT1)


def agent2(input_text: str):
    """
    Create an agent using the model specified in AGENT2 setting.
    Args:
        input_text: The input text to process
    Returns:
        The answer from the agent
    """
    return create_agent(agent_prompt, {
        "agent_name": get_model_display_name(AGENT2),
        "fish_input": input_text
    }, AGENT2)


def agent3(input_text: str):
    """
    Create an agent using the model specified in AGENT3 setting.
    Args:
        input_text: The input text to process
    Returns:
        The answer from the agent
    """
    return create_agent(agent_prompt, {
        "agent_name": get_model_display_name(AGENT3),
        "fish_input": input_text
    }, AGENT3)

