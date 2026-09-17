import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from configuration.config import (LLM_MODEL, OPENROUTER_BASE_URL)
load_dotenv()

llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=OPENROUTER_BASE_URL,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)