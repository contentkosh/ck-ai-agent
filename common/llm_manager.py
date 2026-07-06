import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from configuration.app_settings import LLM_MODEL

load_dotenv()

llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)