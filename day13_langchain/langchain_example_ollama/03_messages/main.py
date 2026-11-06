"""03 · Messages & Roles

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama

load_dotenv()
llm = ChatOllama(model="llama3.2", temperature=0)

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
