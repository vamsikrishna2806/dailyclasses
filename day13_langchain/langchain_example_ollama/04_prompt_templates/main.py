"""04 · Prompt Templates

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()
template = PromptTemplate.from_template("Write a {tone} poem about {topic} in 4 lines.")
llm = ChatOllama(model="llama3.2", temperature=0.7)

for topic in ["Python", "the moon"]:
    prompt = template.invoke({"tone": "funny", "topic": topic}).to_string()
    print(llm.invoke(prompt).content)
    print("-" * 20)
