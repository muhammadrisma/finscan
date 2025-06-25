import os
import json
import re
import logging
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
import requests

from app.setting.setting import AGENT_EXTRACT_TEXT, AGENT1, AGENT2, AGENT3
from app.util.load_prompt import load_prompt
from app.schema.processing_log import AgentResult
from app.schema.result_log import ResultLogResponse

load_dotenv()

logger = logging.getLogger(__name__)

agent_prompt = load_prompt('agent')
api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE")

class FishIdentificationService:
    def __init__(self):
        if not api_key or not api_base:
            logger.error("Missing required environment variables for API key or base URL.")
            raise ValueError("Missing required environment variables for API key or base URL.")
        logger.info("FishIdentificationService initialized successfully.")

    def create_agent(self, prompt_template: str, input_text: dict, model: str):
        """
        Create an agent with the specified prompt template and model.
        """
        logger.info(f"Creating agent with model: {model}")
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
            logger.info(f"Successfully received response from agent {model}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating agent with model {model}: {str(e)}")
            if e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            raise Exception(f"Error creating agent: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while creating agent with model {model}: {str(e)}")
            raise Exception(f"Error creating agent: {str(e)}")

    def agent1(self, input_text: str):
        """Create an agent using the model specified in AGENT1 setting."""
        logger.info("Calling agent 1.")
        return self.create_agent(agent_prompt, {
            "agent_name": AGENT1,
            "fish_input": input_text
        }, AGENT1)

    def agent2(self, input_text: str):
        """Create an agent using the model specified in AGENT2 setting."""
        logger.info("Calling agent 2.")
        return self.create_agent(agent_prompt, {
            "agent_name": AGENT2,
            "fish_input": input_text
        }, AGENT2)

    def agent3(self, input_text: str):
        """Create an agent using the model specified in AGENT3 setting."""
        logger.info("Calling agent 3.")
        return self.create_agent(agent_prompt, {
            "agent_name": AGENT3,
            "fish_input": input_text
        }, AGENT3)

    def extract_agent_content(self, response: dict) -> AgentResult:
        """Extract the essential content from an agent's response."""
        logger.info("Extracting content from agent response.")
        try:
            content = response['choices'][0]['message']['content']
            content = content.replace('```json', '').replace('```', '').strip()
            result = json.loads(content)
            logger.info("Successfully extracted and parsed agent content.")
            return AgentResult(
                agent=result['agent'],
                fish_common_name=result['fish_common_name'],
                latin_name=result['latin_name'],
                reasoning=result['reasoning']
            )
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error extracting agent content: {str(e)}. Response: {response}")
            raise Exception(f"Error extracting agent content: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during content extraction: {str(e)}. Response: {response}")
            raise Exception(f"Error extracting agent content: {str(e)}")

    def normalize_latin_name(self, name: str) -> str:
        """Normalize a latin name for comparison."""
        if not name:
            return ""
        
        name = name.lower()
        
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

    def check_agent_agreement(self, agent_results: list[AgentResult]) -> tuple[bool, str, str, str]:
        """Check if at least 2 agents agree on the latin name."""
        logger.info("Checking agent agreement.")
        # Normalize and count occurrences of each latin name
        normalized_latin_names = [self.normalize_latin_name(result.latin_name) for result in agent_results if result.latin_name]

        if not normalized_latin_names:
            logger.warning("No valid latin names found to check for agreement.")
            first_agent = agent_results[0] if agent_results else None
            common_name = first_agent.fish_common_name if first_agent else ""
            latin_name = first_agent.latin_name if first_agent else ""
            return (False, common_name, latin_name, common_name)

        latin_name_counts = Counter(normalized_latin_names)
        logger.info(f"Latin name counts: {latin_name_counts}")
        
        # Get the most common latin name
        most_common_latin = latin_name_counts.most_common(1)[0]
        
        # Check if at least 2 agents agree
        flag = most_common_latin[1] >= 2
        logger.info(f"Agreement check result: {flag}. Most common: '{most_common_latin[0]}' ({most_common_latin[1]} votes)")
        
        # Find the agent that provided the most common latin name
        majority_latin = most_common_latin[0]
        majority_agent = next(
            (agent for agent in agent_results 
             if self.normalize_latin_name(agent.latin_name) == majority_latin),
            agent_results[0]  # Fallback to first agent if not found
        )
        
        return (
            flag,
            majority_agent.fish_common_name,
            majority_agent.latin_name,  # Use the original (non-normalized) latin name
            majority_agent.fish_common_name  # Using common name as extracted name
        ) 