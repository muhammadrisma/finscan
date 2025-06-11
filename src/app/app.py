import json
import time

from typing import Dict, Optional
from app.api.agent import agent1, agent2, agent3, extract_text
from app.setting.setting import AGENT1, AGENT2, AGENT3, AGENT_EXTRACT_TEXT

def test_fish_extraction(product_desc: str) -> Optional[str]:
    """
    Test fish name extraction from product description.

    Args:
        product_desc: Product description text

    Returns:
        Extracted fish name, or None if an error occurred
    """
    try:
        response = extract_text(product_desc)
        print("Raw extract_text response:", response)
        fish_name = response['choices'][0]['message']['content'].strip()
        print(f"Input: {product_desc}")
        print(f"Extracted fish name: {fish_name}")
        return fish_name
    except Exception as e:
        print(f"Error extracting fish name: {e}")
        return None


def test_agent_analysis(fish_name: str) -> Dict[str, Optional[str]]:
    """
    Test all agents with the extracted fish name.

    Args:
        fish_name: Extracted fish name

    Returns:
        Dictionary containing results from all agents
    """
    results = {}
    agents = {
        "Agent 1": (agent1, AGENT1),
        "Agent 2": (agent2, AGENT2),
        "Agent 3": (agent3, AGENT3)
    }

    for agent_name, (agent_func, model_name) in agents.items():
        try:
            print(f"\nTesting {agent_name} (Model: {model_name})...")
            response = agent_func(fish_name)
            content = response['choices'][0]['message']['content'].strip()
            model = response.get('model', None)

            try:
                result_json = json.loads(content)
                # Update the 'agent' and 'model' fields in the JSON output
                result_json['agent'] = agent_name
                result_json['model'] = model_name
                print(json.dumps(result_json, indent=2))
                results[agent_name] = json.dumps(result_json)
            except json.JSONDecodeError:
                print(content)
                results[agent_name] = content

            time.sleep(1)  # Avoid rate limiting
        except Exception as e:
            print(f"Error with {agent_name}: {e}")
            results[agent_name] = None

    return results


def main():
    # Test product descriptions
    test_cases = [
        "Iwak tenggiri 10 box per box 100 gram",
        "Fish sardine frozen block 5kg",
        "Ikan tongkol 2kg",
        "Poisson maquereau entier 1kg"
    ]

    print("=== Starting Fish Name Extraction Tests ===")
    for desc in test_cases:
        print("\n" + "=" * 50)
        fish_name = test_fish_extraction(desc)
        if fish_name:
            test_agent_analysis(fish_name)


if __name__ == "__main__":
    main()
