"""18 · Tools & Function Calling

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Add two whole numbers and return the sum."""
    return a + b

llm = ChatOllama(model="llama3.2", temperature=0).bind_tools([add])

messages = [HumanMessage(content="What is 12 plus 30?")]
ai_msg = llm.invoke(messages)
messages.append(ai_msg)

for call in ai_msg.tool_calls:          # the model asked for these
    result = add.invoke(call["args"])   # YOUR code runs them
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

print(llm.invoke(messages).content)     # final answer
