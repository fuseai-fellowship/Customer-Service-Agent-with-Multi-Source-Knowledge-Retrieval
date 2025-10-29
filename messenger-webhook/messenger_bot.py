from fastapi import FastAPI, Request, HTTPException
from starlette.responses import PlainTextResponse
from typing import Dict, List
import json
import os
import requests
from agent_service.runner import code_runner

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "MY_DEFAULT_VERIFY_TOKEN")

app = FastAPI(title="Messenger AI Chatbot")

user_histories: Dict[str, str] = {}

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

    print(f"⬅️ Message from {sender_id}: {message_text}")

    chat_summary = user_histories.get(sender_id, "")

    try:
        ai_reply, new_chat_summary = code_runner(message_text, chat_summary)

    except Exception as e:
        ai_reply = "Sorry, I'm having trouble. Please try again."
        print(f"LangGraph Error: {e}")
        new_chat_summary = chat_summary 
    user_histories[sender_id] = new_chat_summary

    send_to_meta_api(sender_id, ai_reply)
    return {"status": "ok"}
