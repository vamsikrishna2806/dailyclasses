"""12 · Document Loaders

Run (with the venv active):  python main.py
Creates notes.txt and students.csv in this folder when run.
"""

from pathlib import Path
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_core.documents import Document

# Create two small sample files so the lesson runs anywhere
Path("notes.txt").write_text("Python was created by Guido van Rossum.\nLists are ordered.", encoding="utf-8")
Path("students.csv").write_text("name,score\nAsha,91\nDev,78\nMeera,85\n", encoding="utf-8")

doc = Document(page_content="Hello world", metadata={"source": "manual"})
print(doc.page_content, doc.metadata)

text_docs = TextLoader("notes.txt", encoding="utf-8").load()
csv_docs = CSVLoader("students.csv").load()

print("text docs:", len(text_docs), text_docs[0].metadata)
print("csv rows:", len(csv_docs))
print(csv_docs[0].page_content)
