"""05 · Chat Prompts & Placeholders

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

load_dotenv()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly tutor."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

history = [
    HumanMessage(content="I am learning Python."),
    AIMessage(content="Great! Ask me anything."),
]
msgs = prompt.invoke({"history": history, "question": "What is a loop?"})
print(llm.invoke(msgs).content)
