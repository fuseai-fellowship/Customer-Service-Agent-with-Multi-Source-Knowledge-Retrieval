from langchain_core.tools import tool
import os
import requests

@tool
def escalation_tool(user_request: str) -> dict:
    """
    Triggers a notification to the admin and informs the user that
    the message has been forwarded to the admin.

    Args:
        user_name (str): Name of the user.
        user_request (str): User request that needs admin support.

    Returns:
        str: Confirmation or error message.
    """
    base_url = os.getenv("BASE_URL")
    # notify_url = f"{base_url}/notify"
    notify_url = "https://15db7069f2dc.ngrok-free.app/notify"
    user_name = "Inu gay boy"
    

    json_data = {
        "to_emails": ["user@example.com"],
        "subject": f"{user_name} needs assistance",
        "body_html": (
            f"<p><b>User: {user_name}</b> needs assistance with the following request:<br>"
            f"{user_request}</p>"
        ),
    }

    try:
        response = requests.post(notify_url, json=json_data, timeout=10)
        response.raise_for_status()
        # return "Your request has been forwarded to the admin. They’ll contact you soon."
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend: {e}")
        return f"Error: {e}"
