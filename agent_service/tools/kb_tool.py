from langchain_core.tools import tool
import os, requests

@tool
def kb_tool(query:str) -> str:
    """
    Retrieves restaurant knowledge base information based on a user query.

    Args:
        query (str): Question or topic related to restaurant policies, FAQs, or general info.

    Returns:
        str: Retreived info
    """
    base_url = os.getenv("BASE_URL")
    kb_url = kb_url + "/knowledge/semantic-search"
    params = {
        "query": query,
        "threshold": 0.7
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend: {e}")
        return {"error": str(e)}
