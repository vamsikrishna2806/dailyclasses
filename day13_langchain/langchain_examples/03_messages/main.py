"""03 · Messages & Roles

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

messages = [
    SystemMessage(content="You are a friendly tutor. Answer in 2 short sentences."),
    HumanMessage(content="What is a variable?"),
]
first = llm.invoke(messages)
print(first.content)

# Keep the conversation: add the reply, then the follow-up question
messages.append(AIMessage(content=first.content))
messages.append(HumanMessage(content="Give me an example in Python."))
second = llm.invoke(messages)
print(second.content)
