import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()
# from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemini-2.5-flash",
    max_completion_tokens=500,
    temperature=0  # optional, make deterministic
)

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, convert_system_message_to_human=True)