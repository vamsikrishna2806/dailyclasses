"""13 · Text Splitters

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

text = (
    "LangChain helps you split long documents into small pieces. "
    "Good chunks keep whole ideas together. "
    "A little overlap protects sentences that fall on a boundary. "
) * 5

for size in [100, 200, 400]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=size // 10)
    chunks = splitter.split_text(text)
    print(f"size={size:<4} chunks={len(chunks)}  first: {chunks[0][:40]}...")
