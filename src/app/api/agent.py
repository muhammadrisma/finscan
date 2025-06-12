import os
import json
from dotenv import load_dotenv
import requests

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.setting.setting import AGENT_EXTRACT_TEXT, AGENT1, AGENT2, AGENT3
from app.util.load_prompt import load_prompt
from app.schema.processing_log import AgentResult

load_dotenv()

# Load prompts
agent_prompt = load_prompt('agent')
extract_text_prompt = load_prompt('extract_text')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

def extract_agent_content(response: dict) -> AgentResult:
    """
    Extract the essential content from an agent's response.
    """
    try:
        content = response['choices'][0]['message']['content']
        # Remove markdown code block if present
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        return AgentResult(
            agent=result['agent'],
            fish_common_name=result['fish_common_name'],
            latin_name=result['latin_name'],
            reasoning=result['reasoning']
        )
    except Exception as e:
        raise Exception(f"Error extracting agent content: {str(e)}")

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
        "agent_name": AGENT1,
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
        "agent_name": AGENT2,
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
        "agent_name": AGENT3,
        "fish_input": input_text
    }, AGENT3)


def process_log(id: str, original_description: str):
    """
    Process the input through all three agents and return a structured log.
    Args:
        id: The unique identifier for the log entry
        original_description: The original product description
    Returns:
        A dictionary containing the processing log with all agent results
    """
    try:
        # Process through all three agents
        agent1_response = agent1(original_description)
        agent2_response = agent2(original_description)
        agent3_response = agent3(original_description)

        # Extract content from each agent's response
        agent1_result = extract_agent_content(agent1_response)
        agent2_result = extract_agent_content(agent2_response)
        agent3_result = extract_agent_content(agent3_response)

        # Create the processing log
        processing_log = {
            "id": id,
            "original_description": original_description,
            "agent_1_result": agent1_result,
            "agent_2_result": agent2_result,
            "agent_3_result": agent3_result
        }

        return processing_log
    except Exception as e:
        raise Exception(f"Error in processing log: {str(e)}")

