"""Hello World with the OpenAI API."""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Read the .env file that sits next to this script
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key or api_key == "your-openai-key-here":
    raise SystemExit("Add your OPENAI_API_KEY to the .env file first.")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model=model,
    input="Say hello world in one friendly sentence.",
)

print("Model :", model)
print("Reply :", response.output_text)
