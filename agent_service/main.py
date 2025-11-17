from agent_service.llm import llm
import redis, json
from agent_service.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME
r = redis.Redis(
    host= REDIS_HOST,
    port= REDIS_PORT,
    decode_responses=True,
    username= REDIS_USERNAME,
    password= REDIS_PASSWORD,
)

USER_KEY = "chat_history:runner"  # You can make this dynamic per user/session
TTL_SECONDS = 30

def save_message(role, content):
    # Append message to Redis list
    msg = json.dumps({"role": role, "content": content})
    r.rpush(USER_KEY, msg)
    # Optionally, trim list to last N messages to save memory
    r.ltrim(USER_KEY, -20, -1) 
    r.expire(USER_KEY, TTL_SECONDS)

def load_history():
    history = []
    for msg_json in r.lrange(USER_KEY, 0, -1):
        history.append(json.loads(msg_json))
    return history

chat_history = []

print("Start chatting with Gemini (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    
    save_message("user", user_input)
    chat_history = load_history()

    response = llm.invoke(chat_history)
    assistant_text = response.content  # safer than .last

    print(f"Gemini: {assistant_text}")

    save_message("assistant", assistant_text)
