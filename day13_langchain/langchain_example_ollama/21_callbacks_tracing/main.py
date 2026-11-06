"""21 · Callbacks & Tracing

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
LangSmith tracing is optional (see the comments at the bottom).
"""

import time
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import ChatOllama

load_dotenv()

class Timer(BaseCallbackHandler):
    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.start = time.perf_counter()
        print("[start] model called")

    def on_llm_end(self, response, **kwargs):
        print(f"[end] took {time.perf_counter() - self.start:.2f}s")

    def on_llm_error(self, error, **kwargs):
        print("[error]", error)

llm = ChatOllama(model="llama3.2")
llm.invoke("Explain callbacks in one line.", config={"callbacks": [Timer()]})

# LangSmith tracing needs no code change. Put these in .env:
#   LANGSMITH_TRACING=true
#   LANGSMITH_API_KEY=your-key
#   LANGSMITH_PROJECT=langchain-zero-to-hero
