import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

# comment this for openroueter llm and uncomment for google gemini llm
from langchain_google_genai import ChatGoogleGenerativeAI


# for google gemini llm
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    # This is important for compatibility with LangGraph's SystemMessages
    convert_system_message_to_human=True 
)

# llm = ChatOpenAI(
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
#     model=os.getenv("MODEL"),
#     max_completion_tokens=500,
#     temperature=0  # optional, make deterministic
# )
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, convert_system_message_to_human=True)
