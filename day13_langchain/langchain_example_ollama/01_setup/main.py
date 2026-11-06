"""01 · Setup & Environment

Run (with the venv active):  python main.py
Uses a free local model through Ollama. No API key needed.
Install Ollama from https://ollama.com, then run:  ollama pull llama3.2
"""

from importlib.metadata import version, PackageNotFoundError
from urllib.request import urlopen
from urllib.error import URLError
from dotenv import load_dotenv
import os

load_dotenv()  # optional: reads .env (for example OLLAMA_HOST)

for pkg in ["langchain", "langchain-core", "langchain-ollama"]:
    try:
        print(f"{pkg:<20} {version(pkg)}")
    except PackageNotFoundError:
        print(f"{pkg:<20} NOT INSTALLED -> pip install {pkg}")

host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
print("Ollama host:", host)

try:
    with urlopen(f"{host}/api/tags", timeout=3) as resp:
        print("Ollama server is running, status:", resp.status)
except URLError:
    print("Ollama server NOT reachable -> start Ollama, then run: ollama pull llama3.2")
