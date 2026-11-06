"""05 · Chat Prompts & Placeholders

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

load_dotenv()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly tutor."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
llm = ChatOllama(model="llama3.2", temperature=0)

history = [
    HumanMessage(content="I am learning Python."),
    AIMessage(content="Great! Ask me anything."),
]
msgs = prompt.invoke({"history": history, "question": "What is a loop?"})
print(llm.invoke(msgs).content)
