"""15 · Vector Stores

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
    Document(page_content="You can return items within 30 days for a full refund."),
    Document(page_content="Delivery takes 3 to 5 working days."),
    Document(page_content="We accept cards, UPI and cash on delivery."),
])

for q in ["Can I send an item back?", "How long does shipping take?", "Can I pay with UPI?"]:
    best = store.similarity_search(q, k=1)[0]
    print(q, "->", best.page_content)
