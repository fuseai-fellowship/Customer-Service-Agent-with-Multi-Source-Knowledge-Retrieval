from fastapi import FastAPI, Request, HTTPException
from starlette.responses import PlainTextResponse
from typing import Dict, List
import json
import os
import requests
from agent_service.runner import code_runner
# Import the ReviewDecision model for state creation if it's in runner.py
# If not, you might need to import it from agent_service.state
# from agent_service.state import ReviewDecision 


FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "MY_DEFAULT_VERIFY_TOKEN")

app = FastAPI(title="Messenger AI Chatbot")

user_histories: Dict[str, str] = {}

def get_user_profile(sender_id: str) -> str:
    """
    Calls the Facebook Graph API to get the user's first and last name.
    """
    if not FB_PAGE_ACCESS_TOKEN:
        print("WARNING: FB_PAGE_ACCESS_TOKEN is not set. Cannot fetch user name.")
        return f"User {sender_id}" 

    url = f"https://graph.facebook.com/{sender_id}"
    params = {
        "fields": "first_name,last_name",
        "access_token": FB_PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        else:
            return f"User {sender_id}"
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching user profile for {sender_id}: {e}")
        return f"User {sender_id}"

def send_to_meta_api(recipient_id: str, text: str):
    if not FB_PAGE_ACCESS_TOKEN:
        print("ERROR: Missing FB_PAGE_ACCESS_TOKEN")
        return
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Reply sent to {recipient_id}: {text[:30]}...")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token and challenge:
        if token == FB_VERIFY_TOKEN:
            return PlainTextResponse(content=challenge)
        raise HTTPException(status_code=403, detail="Token mismatch")
    raise HTTPException(status_code=400, detail="Invalid verification request")



@app.post("/webhook")
async def handle_messages(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"status": "ok", "detail": "Invalid JSON"}

    try:
        messaging_event = data["entry"][0]["messaging"][0]
        sender_id = messaging_event["sender"]["id"]
        message_text = messaging_event.get("message", {}).get("text")
        if not message_text:
            return {"status": "ok", "detail": "No text message"}
    except (KeyError, IndexError):
        return {"status": "ok", "detail": "Non-message event ignored"}


    user_name = get_user_profile(sender_id)
    print(f"⬅️ Message from {user_name} (ID: {sender_id}): {message_text}")

    # chat_summary = user_histories.get(sender_id, "")


    try:
        ai_reply = code_runner(user_name, message_text)

    except Exception as e:
        ai_reply = "Sorry, I'm having trouble. Please try again."
        print(f"LangGraph Error: {e}")
        # new_chat_summary = chat_summary 
    
    
    # user_histories[sender_id] = new_chat_summary

    send_to_meta_api(sender_id, ai_reply)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("messenger_bot:app", host="0.0.0.0", port=8001, reload=True)