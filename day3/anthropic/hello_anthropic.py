"""Hello World with the Anthropic (Claude) API."""
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

# Read the .env file that sits next to this script
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("ANTHROPIC_API_KEY")
model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")

if not api_key or api_key == "your-anthropic-key-here":
    raise SystemExit("Add your ANTHROPIC_API_KEY to the .env file first.")

client = Anthropic(api_key=api_key)

response = client.messages.create(
    model=model,
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello world in one friendly sentence."}
    ],
)

print("Model :", model)
print("Reply :", response.content[0].text)
