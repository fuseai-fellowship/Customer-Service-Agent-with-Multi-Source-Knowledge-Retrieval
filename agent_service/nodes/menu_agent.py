import requests
from agent_service.config import BASE_URL

def menu_agent(state: dict) -> dict:
    """
    Retrieves restaurant menu items based on the provided criteria
    and returns in the structured format for subagent aggregation.
    """
    menu_params = state.get("params", {})
    items_url = BASE_URL + "/items"

    try:
        response = requests.get(items_url, params=menu_params, timeout=10)
        response.raise_for_status()
        menu_data = response.json()
    except requests.exceptions.RequestException as e:
        menu_data = {"error": str(e)}

    # Return wrapped in subagent_outputs for operator.add merging
    return {
        "subagent_outputs": [
            {
                "type": "menu",
                "parameters": menu_params,  # only non-None params if you want
                "output": menu_data
            }
        ]
    }
