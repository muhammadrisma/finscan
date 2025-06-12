import re

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

def clean_json_content(content: str) -> str:
    """
    Clean JSON content by removing markdown code blocks and extra whitespace.
    """
    return content.replace('```json', '').replace('```', '').strip() 