"""02 · Your First LLM Call

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

question = "Explain Python in one sentence."
response = llm.invoke(question)

print("Answer:", response.content)
print("Type:", type(response).__name__)
print("Tokens:", response.usage_metadata)
