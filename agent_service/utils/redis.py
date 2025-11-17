import redis, json
from agent_service.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME, CHAT_TTL_SECONDS, CHAT_MAX_MESSAGES
r = redis.Redis(
    host= REDIS_HOST,
    port= REDIS_PORT,
    decode_responses=True,
    username= REDIS_USERNAME,
    password= REDIS_PASSWORD,
)
USER_KEY = "chat_history:runner"

def save_message(role, content):
    # Append message to Redis list
    msg = json.dumps({"role": role, "content": content})
    r.rpush(USER_KEY, msg)
    # Optionally, trim list to last N messages to save memory
    r.ltrim(USER_KEY, -CHAT_MAX_MESSAGES, -1) 
    r.expire(USER_KEY, CHAT_TTL_SECONDS)

def load_history():
    history = []
    for msg_json in r.lrange(USER_KEY, 0, -1):
        history.append(json.loads(msg_json))
    return history