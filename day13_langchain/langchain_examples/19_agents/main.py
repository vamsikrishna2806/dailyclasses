"""19 · Agents

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

import datetime
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Add two whole numbers."""
    return a + b

@tool
def today() -> str:
    """Return today's date."""
    return datetime.date.today().isoformat()

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[add, today],
    system_prompt="You are a helpful assistant. Use tools when they help.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "What is today's date, and what is 15 + 27?"}]})

for msg in result["messages"]:   # watch every step
    print(msg.type, "|", msg.content)
