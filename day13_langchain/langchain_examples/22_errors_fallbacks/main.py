"""22 · Errors, Retries & Fallbacks

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY and ANTHROPIC_API_KEY (the backup model).
"""

import json
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

load_dotenv()

primary = ChatOpenAI(model="gpt-4o-mini", max_retries=2, timeout=20)
backup = ChatAnthropic(model="claude-haiku-5-5")  # check the current model name in the provider docs
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
