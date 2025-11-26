from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Chat settings
CHAT_TTL_SECONDS = int(os.getenv("CHAT_TTL_SECONDS", 3600))
CHAT_MAX_MESSAGES = int(os.getenv("CHAT_MAX_MESSAGES", 10))