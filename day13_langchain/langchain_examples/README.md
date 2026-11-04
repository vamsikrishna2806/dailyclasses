# LangChain sample programs

Every code example from the LangChain visual guide, one folder per lesson.
The code matches the **Full code** section of each lesson page
(`../index.html` → open a lesson → "Full code with a virtual environment").

## 1. Set up the virtual environment (once)

```bat
cd D:\getwork\day13_langchain\langchain_examples
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Then create your key file. Copy `.env.example` to `.env` and paste your key:

```bat
copy .env.example .env
```

Lesson 01 shows how to use a free local model with Ollama if you have no key.

## 2. Run a lesson

Activate the venv, go into the lesson folder, and run the file:

```bat
.venv\Scripts\activate
cd 02_first_llm_call
python main.py
```

Each `main.py` runs on its own and prints its results. Press `Ctrl+C` to stop any
lesson that keeps running (for example the agents).

## Lessons

| Folder | Concept | How to run |
|---|---|---|
| 01_setup | Setup & Environment | `python main.py` |
| 02_first_llm_call | Your First LLM Call | `python main.py` |
| 03_messages | Messages & Roles | `python main.py` |
| 04_prompt_templates | Prompt Templates | `python main.py` |
| 05_chat_prompt_placeholders | Chat Prompts & Placeholders | `python main.py` |
| 06_output_parsers | Output Parsers | `python main.py` |
| 07_structured_output | Structured Output (Pydantic) | `python main.py` |
| 08_lcel_runnables | LCEL & the Pipe Operator | `python main.py` |
| 09_runnable_primitives | Runnable Building Blocks | `python main.py` |
| 10_streaming | Streaming & Batching | `python main.py` |
| 11_chat_memory | Chat Memory | `python main.py` |
| 12_document_loaders | Document Loaders | `python main.py` |
| 13_text_splitters | Text Splitters | `python main.py` |
| 14_embeddings | Embeddings | `python main.py` |
| 15_vector_stores | Vector Stores | `python main.py` |
| 16_retrievers | Retrievers | `python main.py` |
| 17_rag_pipeline | RAG End to End | `python main.py` |
| 18_tools | Tools & Function Calling | `python main.py` |
| 19_agents | Agents | `python main.py` |
| 20_langgraph_intro | LangGraph Basics | `python main.py` |
| 21_callbacks_tracing | Callbacks & Tracing | `python main.py` |
| 22_errors_fallbacks | Errors, Retries & Fallbacks | `python main.py` |
| 23_capstone | Capstone: Study Buddy Agent | `python main.py` |

## Notes

- Keep `.env` secret. It is in `.gitignore`, so Git will not upload it.
- Model names such as `gpt-4o-mini` may change. If a name is rejected, use a model your account has.
- Lesson 22 needs an Anthropic key for its backup model. Remove `with_fallbacks` if you only have an OpenAI key.
