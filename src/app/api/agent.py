import os
import json
import re
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
import requests

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.setting.setting import AGENT_EXTRACT_TEXT, AGENT1, AGENT2, AGENT3
from app.util.load_prompt import load_prompt
from app.schema.processing_log import AgentResult
from app.schema.result_log import ResultLogResponse

load_dotenv()

# Load prompts
agent_prompt = load_prompt('agent')
extract_text_prompt = load_prompt('extract_text')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

def convert_to_dict(obj):
    """
    Convert objects to dictionaries for JSON serialization.
    """
    if isinstance(obj, AgentResult):
        return obj.model_dump()
    return obj

def save_to_file(data: dict, id: str):
    """
    Save the processing log results to a text file.
    Args:
        data: The processing log data to save
        id: The unique identifier for the log entry
    """
    try:
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"process_log_{id}_{timestamp}.txt"
        filepath = os.path.join(results_dir, filename)

        # Convert AgentResult objects to dictionaries
        serializable_data = {
            "id": data["id"],
            "original_description": data["original_description"],
            "agent_1_result": convert_to_dict(data["agent_1_result"]),
            "agent_2_result": convert_to_dict(data["agent_2_result"]),
            "agent_3_result": convert_to_dict(data["agent_3_result"])
        }

        # Format the data for better readability
        formatted_data = json.dumps(serializable_data, indent=2)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_data)

        return filepath
    except Exception as e:
        raise Exception(f"Error saving results to file: {str(e)}")

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


def process_log(id: str, extracted_fish_name: str):
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
        agent1_response = agent1(extracted_fish_name)
        agent2_response = agent2(extracted_fish_name)
        agent3_response = agent3(extracted_fish_name)

        # Extract content from each agent's response
        agent1_result = extract_agent_content(agent1_response)
        agent2_result = extract_agent_content(agent2_response)
        agent3_result = extract_agent_content(agent3_response)

        # Create the processing log
        processing_log = {
            "id": id,
            "original_description": extracted_fish_name,
            "agent_1_result": agent1_result,
            "agent_2_result": agent2_result,
            "agent_3_result": agent3_result
        }

        # Save results to file
        filepath = save_to_file(processing_log, id)
        print(f"Results saved to: {filepath}")

        return processing_log
    except Exception as e:
        raise Exception(f"Error in processing log: {str(e)}")

def normalize_latin_name(name: str) -> str:
    """
    Normalize a latin name for comparison.
    - Convert to lowercase
    - Remove extra spaces
    - Remove special characters
    - Handle common variations
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Remove special characters except spaces and dots
    name = re.sub(r'[^a-z\s.]', '', name)
    
    # Handle common variations
    replacements = {
        'spp': 'species',
        'sp': 'species',
        'subsp': 'subspecies',
        'var': 'variety',
        'cv': 'cultivar'
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name.strip()

def check_agent_agreement(agent_results: list[AgentResult]) -> tuple[bool, str, str, str]:
    """
    Check if at least 2 agents agree on the latin name.
    Returns:
        tuple: (flag, fish_name_english, fish_name_latin, extracted_fish_name)
    """
    # Normalize and count occurrences of each latin name
    normalized_latin_names = [normalize_latin_name(result.latin_name) for result in agent_results]
    latin_name_counts = Counter(normalized_latin_names)
    
    # Get the most common latin name
    most_common_latin = latin_name_counts.most_common(1)[0]
    
    # Check if at least 2 agents agree
    flag = most_common_latin[1] >= 2
    
    # Find the agent that provided the most common latin name
    majority_latin = most_common_latin[0]
    majority_agent = next(
        (agent for agent in agent_results 
         if normalize_latin_name(agent.latin_name) == majority_latin),
        agent_results[0]  # Fallback to first agent if not found
    )
    
    return (
        flag,
        majority_agent.fish_common_name,
        majority_agent.latin_name,  # Use the original (non-normalized) latin name
        majority_agent.fish_common_name  # Using common name as extracted name
    )

def save_result_log(data: ResultLogResponse, id: str):
    """
    Save the result log to a text file.
    Args:
        data: The result log data to save
        id: The unique identifier for the log entry
    """
    try:
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_log_{id}_{timestamp}.txt"
        filepath = os.path.join(results_dir, filename)

        # Convert to dictionary and format the data
        formatted_data = json.dumps(data.model_dump(), indent=2)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_data)

        return filepath
    except Exception as e:
        raise Exception(f"Error saving result log to file: {str(e)}")

def process_result_log(id: str, original_description: str) -> ResultLogResponse:
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
        extract_text_response = extract_text(original_description)
        content = extract_text_response['choices'][0]['message']['content']
        # The content should be just the fish name as a string
        extracted_fish_name = content.strip()
        
        # Then get the processing log using the extracted fish name
        processing_log = process_log(id, extracted_fish_name)
        
        # Get agent results
        agent_results = [
            processing_log["agent_1_result"],
            processing_log["agent_2_result"],
            processing_log["agent_3_result"]
        ]
        
        # Check agent agreement
        flag, fish_name_english, fish_name_latin, _ = check_agent_agreement(agent_results)
        
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
        filepath = save_result_log(result_log, id)
        print(f"Result log saved to: {filepath}")
        
        return result_log
    except Exception as e:
        raise Exception(f"Error in processing result log: {str(e)}")

