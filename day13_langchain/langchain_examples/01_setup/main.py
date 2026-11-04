"""01 · Setup & Environment

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from importlib.metadata import version, PackageNotFoundError
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into environment variables

for pkg in ["langchain", "langchain-core", "langchain-openai"]:
    try:
        print(f"{pkg:<20} {version(pkg)}")
    except PackageNotFoundError:
        print(f"{pkg:<20} NOT INSTALLED -> pip install {pkg}")

print("OPENAI_API_KEY set:", bool(os.getenv("OPENAI_API_KEY")))
