"""17 · RAG End to End

Run (with the venv active):  python main.py
Creates handbook.txt in this folder when run. Needs OPENAI_API_KEY in .env.
"""

from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 1. Index (once)
Path("handbook.txt").write_text(
    "Employees get 20 days of paid leave per year.\n"
    "Sick leave is 10 days and needs a doctor's note after 2 days.\n"
    "The office is open 9am to 6pm, Monday to Friday.\n", encoding="utf-8")
docs = TextLoader("handbook.txt", encoding="utf-8").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20).split_documents(docs)
store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))
store.add_documents(chunks)
retriever = store.as_retriever(search_kwargs={"k": 2})

# 2-4. Retrieve, augment, generate
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. If it is not there, say you do not know.\n\nContext:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

print(rag.invoke("How many leave days do I get?"))
print(rag.invoke("What is the capital of France?"))  # should say it does not know
