"""10 · Streaming & Batching

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

import asyncio, time
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()
chain = ChatPromptTemplate.from_template("Write a 4-line poem about {thing}.") | ChatOllama(model="llama3.2") | StrOutputParser()

# 1. Streaming: print as tokens arrive
start = time.perf_counter()
for i, chunk in enumerate(chain.stream({"thing": "the sea"})):
    if i == 0:
        print(f"[first chunk after {time.perf_counter() - start:.2f}s]")
    print(chunk, end="", flush=True)
print()

# 2. Async streaming (for web apps)
async def main():
    async for chunk in chain.astream({"thing": "the sky"}):
        print(chunk, end="", flush=True)
    print()

asyncio.run(main())

# 3. Batch: many inputs, results in the same order
print(chain.batch([{"thing": "rain"}, {"thing": "fire"}]))
