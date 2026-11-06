"""23 · Capstone: Study Buddy Agent

Run (with the venv active):  python main.py
Put your .txt study notes in a notes/ folder next to main.py before running.
Uses free local models through Ollama:
  ollama pull llama3.2
  ollama pull nomic-embed-text
"""

from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.document_loaders import TextLoader
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 1. Ingest: put your .txt study notes in a folder called notes/ first
def build_store(folder="notes"):
    docs = []
    for path in Path(folder).glob("*.txt"):
        docs += TextLoader(str(path), encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
    store = InMemoryVectorStore(OllamaEmbeddings(model="nomic-embed-text"))
    store.add_documents(chunks)
    return store

store = build_store()

# 2. Tools
@tool
def search_notes(query: str) -> str:
    """Search the student's study notes. Use this for any course question."""
    hits = store.similarity_search(query, k=3)
    return "\n\n".join(f"[{d.metadata.get('source')}] {d.page_content}" for d in hits)

@tool
def calculate(expression: str) -> str:
    """Evaluate simple arithmetic like '12 * (3 + 4)'."""
    if not set(expression) <= set("0123456789+-*/(). "):
        return "Only numbers and + - * / ( ) are allowed."
    return str(eval(expression))  # safe only because the input is filtered above

# 3. Agent
SYSTEM = ("You are a Study Buddy. Call search_notes before answering course questions. "
          "Cite the source file. If the notes do not contain the answer, say so. "
          "Use calculate for arithmetic.")
agent = create_agent(
    model=ChatOllama(model="llama3.2", temperature=0),
    tools=[search_notes, calculate],
    system_prompt=SYSTEM,
)

# 4. Memory: keep the last 10 messages
history = []

def ask(question: str) -> str:
    history.append({"role": "user", "content": question})
    result = agent.invoke({"messages": history[-10:]}, config={"recursion_limit": 8})
    answer = result["messages"][-1].content
    history.append({"role": "assistant", "content": answer})
    return answer

print(ask("What is photosynthesis?"))
print(ask("Explain that more simply."))
