import os
from pathlib import Path

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the prompts directory.
    Args:
        prompt_name: Name of the prompt file without extension
    Returns:
        The content of the prompt file
    """
    current_dir = Path(__file__).parent.parent
    prompt_path = current_dir / 'prompt' / f'{prompt_name}.md'
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{prompt_name}.md' not found in {prompt_path.parent}")

def get_all_prompts() -> dict:
    """
    Load all prompt files from the prompts directory.
    Returns:
        Dictionary of prompt names and their contents
    """
    prompts = {}
    prompt_dir = Path(__file__).parent.parent / 'prompt'
    
    # Get all .md files in the prompt directory
    for file in prompt_dir.glob('*.md'):
        prompt_name = file.stem
        prompts[prompt_name] = load_prompt(prompt_name)
    
    return prompts 