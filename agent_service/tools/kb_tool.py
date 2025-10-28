from langchain_core.tools import tool
@tool
def kb_tool(query:str) -> str:
    """
    Retrieves restaurant knowledge base information based on a user query.

    Args:
        query (str): Question or topic related to restaurant policies, FAQs, or general info.

    Returns:
        str: Retreived info
    """
    return "Lumina Bistro is a restaurant located at Jhamsikhel, Lalitpur."