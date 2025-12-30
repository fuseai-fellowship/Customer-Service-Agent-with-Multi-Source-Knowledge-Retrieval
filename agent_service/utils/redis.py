import redis, json
from agent_service.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME, CHAT_TTL_SECONDS, CHAT_MAX_MESSAGES
r = redis.Redis(
    host= REDIS_HOST,
    port= REDIS_PORT,
    decode_responses=True,
    username= REDIS_USERNAME,
    password= REDIS_PASSWORD,
)

def get_user_key(user_id: str):
    return f"chat_history:{user_id}"

def save_message(user_id: str, role: str, content: str):
    user_key = get_user_key(user_id)  # <- use here
    msg = json.dumps({"role": role, "content": content})
    r.rpush(user_key, msg)
    r.ltrim(user_key, -CHAT_MAX_MESSAGES, -1)
    r.expire(user_key, CHAT_TTL_SECONDS)

def load_history(user_id: str):
    user_key = get_user_key(user_id)  # <- and here
    history = []
    for msg_json in r.lrange(user_key, 0, -1):
        history.append(json.loads(msg_json))
    return history