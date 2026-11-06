"""02 · Your First LLM Call

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()
llm = ChatOllama(model="llama3.2", temperature=0)

question = "Explain Python in one sentence."
response = llm.invoke(question)

print("Answer:", response.content)
print("Type:", type(response).__name__)
print("Tokens:", response.usage_metadata)
