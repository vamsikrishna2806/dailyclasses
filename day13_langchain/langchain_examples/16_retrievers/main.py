"""16 · Retrievers

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()
store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))
store.add_documents([
    Document(page_content="Pay by card, UPI or cash on delivery."),
    Document(page_content="Online payments are processed securely."),
    Document(page_content="Refunds go back to the original payment method."),
    Document(page_content="Delivery takes 3 to 5 working days."),
])

similar = store.as_retriever(search_kwargs={"k": 3})
varied = store.as_retriever(search_type="mmr", search_kwargs={"k": 3})

for name, r in [("similarity", similar), ("mmr", varied)]:
    print("--", name)
    for d in r.invoke("How can I pay?"):
        print("  ", d.page_content)
