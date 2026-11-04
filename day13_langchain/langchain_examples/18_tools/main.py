"""18 · Tools & Function Calling

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Add two whole numbers and return the sum."""
    return a + b

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([add])

messages = [HumanMessage(content="What is 12 plus 30?")]
ai_msg = llm.invoke(messages)
messages.append(ai_msg)

for call in ai_msg.tool_calls:          # the model asked for these
    result = add.invoke(call["args"])   # YOUR code runs them
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

print(llm.invoke(messages).content)     # final answer
