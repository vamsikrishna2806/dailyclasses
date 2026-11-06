"""22 · Errors, Retries & Fallbacks

Run (with the venv active):  python main.py
Uses two free local models through Ollama. No API key needed:
  ollama pull llama3.2     (primary)
  ollama pull qwen2.5      (backup, used if the primary fails)
"""

import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

primary = ChatOllama(model="llama3.2", temperature=0)
backup = ChatOllama(model="qwen2.5", temperature=0)  # any other model you have pulled
robust = primary.with_fallbacks([backup])

def get_json(prompt: str, attempts: int = 3) -> dict:
    for _ in range(attempts):
        text = robust.invoke(prompt).content
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            prompt = f"Your last answer was not valid JSON ({e}). Return ONLY valid JSON."
    raise ValueError("Model never returned valid JSON")

try:
    print(get_json('Return JSON with keys "city" and "country" for Paris.'))
except Exception as e:
    print("Sorry, the assistant is busy. Please try again.", type(e).__name__)
