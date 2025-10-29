# agent-service/messenger_bot.py
import os
import requests
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from starlette.responses import PlainTextResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, List
from typing_extensions import TypedDict
from dotenv import load_dotenv

# --- 1. INITIAL SETUP & CONFIGURATION ---
load_dotenv()
# IMPORTANT: These keys MUST be set in your .env file
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "MY_DEFAULT_VERIFY_TOKEN")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- 2. LLM & GRAPH SETUP (Minimal) ---

# Initialize LLM for OpenRouter
llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL"),
    temperature=0.7,
    max_completion_tokens=500
)

# Define State for LangGraph
class State(TypedDict):
    messages: Annotated[List[HumanMessage], add_messages]

# Define the single chat node
def simple_llm_chat_node(state: State):
    """Passes the chat history to the LLM and gets a response."""
    print("--- Running LLM for response ---")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the simple LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", simple_llm_chat_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
compiled_graph = graph_builder.compile()

# --- 3. META API UTILITY ---

def send_to_meta_api(recipient_id: str, text: str):
    """Sends a text message back to the Messenger user."""
    if not FB_PAGE_ACCESS_TOKEN:
        print("ERROR: FB_PAGE_ACCESS_TOKEN is missing. Cannot send reply.")
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
        response.raise_for_status() # Raises an HTTPError if the status is 4xx or 5xx
        print(f"✅ Reply sent to {recipient_id}: {text[:30]}...")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message to Meta: {e}")

# --- 4. FASTAPI WEBHOOK ENDPOINTS ---

app = FastAPI(title="Basic Meta Echo Bot")

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Handles the Meta webhook verification (GET request)."""
    
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    token = request.query_params.get("hub.verify_token")

    # Log for debugging before validation
    print(f"DEBUG: Received verification request with token: {token}")

    if mode == "subscribe" and token and challenge:
        # Check if the received token matches the one in your environment
        if token == FB_VERIFY_TOKEN:
            print("✅ Webhook verified successfully.")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            # Token mismatch is a 403 Forbidden error
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    
    # Missing parameters is a 400 Bad Request error
    raise HTTPException(status_code=400, detail="Missing or invalid verification parameters")


@app.post("/webhook")
async def handle_messages(request: Request):
    """Receives incoming messages (POST request), runs LLM, and replies."""
    
    # --- 1. SAFELY READ BODY (CRITICAL FIX) ---
    try:
        # Read the raw body first
        body = await request.body()
        if not body:
            # Handle cases where Meta sends a POST request with an empty body
            print("INFO: Received empty body in POST request. Acknowledging.")
            return {"status": "ok", "detail": "Empty body acknowledged"}

        # Attempt to decode the JSON
        data = json.loads(body)
        
    except json.JSONDecodeError:
        # If the body is present but not JSON (shouldn't happen often, but useful for retries)
        print("ERROR: Could not decode JSON body.")
        # Return OK status code, otherwise Meta will retry the failed webhook
        return {"status": "ok", "detail": "Invalid body format"} 
    
    # --- 2. EXTRACT MESSAGE DETAILS ---
    try:
        # The rest of your extraction logic remains the same, using 'data'
        messaging_event = data['entry'][0]['messaging'][0]
        sender_id = messaging_event['sender']['id']
        # Check for message text, handle case where it's a delivery receipt (no 'text' key)
        message_text = messaging_event.get('message', {}).get('text')
        
        if not message_text:
             # Ignore events without text content (like delivery receipts)
            return {"status": "ok", "detail": "Event without text content ignored"}

    except (KeyError, IndexError, TypeError):
        # Ignore non-message events (like delivery receipts or postbacks)
        return {"status": "ok", "detail": "Non-message event ignored"}

    # ... (Rest of the LLM/LangGraph processing logic) ...
    # ...

    print(f"⬅️ Received message from {sender_id}: {message_text}")
    
    # --- 3. RUN LANGGRAPH (Synchronous for now) ---
    try:
        inputs = {"messages": [HumanMessage(content=message_text)]}
        final_state = compiled_graph.invoke(inputs) 
        final_reply_text = final_state["messages"][-1].content
    
    except Exception as e:
        final_reply_text = "I'm sorry, but my AI core is currently having issues. Please try again in a moment."
        print(f"❌ LangGraph / LLM Execution Error: {e}")
        
    # --- 4. SEND REPLY AND RETURN SUCCESS ---
    send_to_meta_api(sender_id, final_reply_text)
    
    return {"status": "ok"}


if __name__ == '__main__':
    # You will need to import uvicorn and run the app as usual
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    pass


# --- RUN ENTRY POINT ---
if __name__ == "__main__":
    # We use port 8000 for local testing
    uvicorn.run(app, host="0.0.0.0", port=8000)