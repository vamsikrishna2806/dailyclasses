"""14 · Embeddings

Run (with the venv active):  python main.py
Uses a free local embedding model through Ollama (run: ollama pull nomic-embed-text).
No API key needed.
"""

import math
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings

load_dotenv()
emb = OllamaEmbeddings(model="nomic-embed-text")

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

sentences = [
    "The stock market fell today.",
    "Shares dropped sharply.",
    "I love baking cakes.",
    "Bread needs flour and yeast.",
]
vectors = emb.embed_documents(sentences)
query = emb.embed_query("Why are investors worried?")

for score, s in sorted(((cosine(query, v), s) for v, s in zip(vectors, sentences)), reverse=True):
    print(round(score, 3), s)
