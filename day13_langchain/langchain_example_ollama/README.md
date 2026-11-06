# LangChain sample programs (Ollama, local)

The same LangChain lessons as `langchain_examples`, but every model runs **locally
through Ollama**. No OpenAI or Anthropic key is needed, and nothing is sent to the cloud.

## 1. Install Ollama and download the models (once)

1. Install Ollama from https://ollama.com and start it.
2. Download the models used by the lessons:

```bat
ollama pull llama3.2
ollama pull nomic-embed-text
ollama pull qwen2.5
```

- `llama3.2` is the chat model (lessons 02–23).
- `nomic-embed-text` is the embedding model (lessons 14–17 and 23).
- `qwen2.5` is only the backup model in lesson 22.

If your computer is small, you can swap `llama3.2` for `llama3.2:1b` in the code.

## 2. Set up the virtual environment (once)

```bat
cd D:\getwork\day13_langchain\langchain_example_ollama
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

No `.env` file is required. Only copy `.env.example` to `.env` if you want to change
`OLLAMA_HOST` or turn on LangSmith tracing.

## 3. Run a lesson

Activate the venv, go into the lesson folder, and run the file:

```bat
.venv\Scripts\activate
cd 02_first_llm_call
python main.py
```

Each `main.py` runs on its own and prints its results. Press `Ctrl+C` to stop any
lesson that keeps running.

## Lessons

| Folder | Concept | Model used |
|---|---|---|
| 01_setup | Setup & Environment (also checks Ollama is running) | none |
| 02_first_llm_call | Your First LLM Call | llama3.2 |
| 03_messages | Messages & Roles | llama3.2 |
| 04_prompt_templates | Prompt Templates | llama3.2 |
| 05_chat_prompt_placeholders | Chat Prompts & Placeholders | llama3.2 |
| 06_output_parsers | Output Parsers | llama3.2 |
| 07_structured_output | Structured Output (Pydantic) | llama3.2 |
| 08_lcel_runnables | LCEL & the Pipe Operator | llama3.2 |
| 09_runnable_primitives | Runnable Building Blocks | llama3.2 |
| 10_streaming | Streaming & Batching | llama3.2 |
| 11_chat_memory | Chat Memory | llama3.2 |
| 12_document_loaders | Document Loaders | none |
| 13_text_splitters | Text Splitters | none |
| 14_embeddings | Embeddings | nomic-embed-text |
| 15_vector_stores | Vector Stores | nomic-embed-text |
| 16_retrievers | Retrievers | nomic-embed-text |
| 17_rag_pipeline | RAG End to End | llama3.2 + nomic-embed-text |
| 18_tools | Tools & Function Calling | llama3.2 |
| 19_agents | Agents | llama3.2 |
| 20_langgraph_intro | LangGraph Basics | none |
| 21_callbacks_tracing | Callbacks & Tracing | llama3.2 |
| 22_errors_fallbacks | Errors, Retries & Fallbacks | llama3.2 + qwen2.5 |
| 23_capstone | Capstone: Study Buddy Agent | llama3.2 + nomic-embed-text |

## Notes

- Local models are smaller than cloud models, so answers can be less accurate. Tool calling
  and structured output work with `llama3.2`, but check the printed results.
- The first run of a model is slow while Ollama loads it into memory.
- Lesson 22 uses a second local model as the backup, so there is no cloud fallback.
- Lesson 21 can send traces to LangSmith only if you set `LANGSMITH_TRACING=true` and a key.
