"""11 · Chat Memory

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
chat = RunnableWithMessageHistory(
    chain, get_session_history,
    input_messages_key="question", history_messages_key="history",
)

alice = {"configurable": {"session_id": "alice"}}
bob = {"configurable": {"session_id": "bob"}}

chat.invoke({"question": "My name is Ravi."}, config=alice)
print(chat.invoke({"question": "What is my name?"}, config=alice))  # Ravi
print(chat.invoke({"question": "What is my name?"}, config=bob))    # does not know
