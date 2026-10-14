"""Hello World with the Google Gemini API."""
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Read the .env file that sits next to this script
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key or api_key == "your-gemini-key-here":
    raise SystemExit("Add your GEMINI_API_KEY to the .env file first.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=model,
    contents="Say hello world in one friendly sentence.",
)

print("Model :", model)
print("Reply :", response.text)
