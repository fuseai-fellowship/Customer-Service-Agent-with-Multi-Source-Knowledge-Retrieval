from langchain_core.tools import tool
@tool
def escalation_tool(user_request:str) -> str:
    """
    Triggers notification to the admin and responds to inform that the message has been forwarded to admin.

    Args:
        user_request (str): User request that needs admin support.

    Returns:
        str: Retreived info
    """
    response = f"Your request: '{user_request}' has been forwarded to admin and they will contact you soon."
    return response