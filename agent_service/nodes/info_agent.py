import requests
from agent_service.config import BASE_URL

def info_agent(state:dict) -> dict:
    """
    Retrieves restaurant knowledge base information based on a user query.
    """
    info_params = state.get("params", {})
    query_str = info_params.get("topic", "")

    kb_url = BASE_URL + "/knowledge/semantic-search"
    params = {
        "search": query_str
    }

    try:
        response = requests.get(kb_url, params=params, timeout=10)
        response.raise_for_status()
        info_data= response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend: {e}")
        info_data ={"error": str(e)}
    
    return {
        "subagent_outputs": [
            {
                "type": "menu",
                "parameters": info_params,  # only non-None params if you want
                "output": info_data
            }
        ]
    }
