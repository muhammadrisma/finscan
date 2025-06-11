import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough

from app.setting.setting import AGENT_EXTRACT_TEXT, AGENT1, AGENT2, AGENT3
from app.util.load_prompt import load_prompt

load_dotenv()



# Load prompts
agent_prompt = load_prompt('agent')
extract_text_prompt = load_prompt('extract_text')

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

def create_agent(prompt_template: str, input_text: dict, model: str = "gpt-4o-mini"):
    """
    Create an agent with the specified prompt template and model.
    Args:
        prompt_template: The prompt template to use
        input_text: The input text to process as a dictionary
        model: The model to use (default: gpt-4o-mini)
    Returns:
        The processed response from the agent
    """
    llm = ChatOpenAI(
        model=model,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
    )
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    return chain.invoke(input_text)

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
    return create_agent(agent_prompt, {"agent_name": get_model_display_name(AGENT1), "fish_input": input_text}, AGENT1)

def agent2(input_text: str):
    """
    Create an agent using the model specified in AGENT2 setting.
    Args:
        input_text: The input text to process
    Returns:
        The answer from the agent
    """
    return create_agent(agent_prompt, {"agent_name": get_model_display_name(AGENT2), "fish_input": input_text}, AGENT2)

def agent3(input_text: str):
    """
    Create an agent using the model specified in AGENT3 setting.
    Args:
        input_text: The input text to process
    Returns:
        The answer from the agent
    """
    return create_agent(agent_prompt, {"agent_name": get_model_display_name(AGENT3), "fish_input": input_text}, AGENT3)

