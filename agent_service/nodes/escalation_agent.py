import os
import requests

def escalation_agent(state: dict) -> dict:
    """
    Triggers a notification to the admin and informs the user that
    the message has been forwarded to the admin.

    Args:
        state (dict): The current conversation state. Should include:
            - user_name (str): Name of the user.
            - parameters (dict): Should include 'topic' describing the reason for escalation.

    Returns:
        dict: Status and message of the escalation attempt.
    """
    user_name = state.get("user_name", "Unknown User")
    parameters = state.get("parameters", {})
    escalation_topic = parameters.get("topic", "(No topic provided)")

    base_url = os.getenv("BASE_URL")
    notify_url = f"{base_url}/notify"

    json_data = {
        "to_emails": ["user@example.com"], 
        "subject": f"{user_name} needs assistance",
        "body_html": (
            f"<p><b>User: {user_name}</b> needs assistance with the following topic:<br>"
            f"{escalation_topic}</p>"
        ),
    }

    try:
        response = requests.post(notify_url, json=json_data, timeout=10)
        response.raise_for_status()
        return {"status": "success", "message": "Admin has been notified."}
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend: {e}")
        return {"status": "error", "message": str(e)}
