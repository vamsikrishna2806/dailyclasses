# Wikipedia Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a knowledgeable research assistant with access to Wikipedia.
When a user asks about a topic, person, place, or event, use the search_wikipedia tool
to find accurate information. Summarise the key facts clearly, explain any complex
concepts in simple terms, and highlight what makes the topic interesting or significant.
Always be informative but concise.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational Wikipedia research CLI agent in Python using LangChain
and LangGraph with one Wikipedia search tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.3 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  Library   : wikipedia Python package — free, no API key

TOOL (1)
  search_wikipedia(query: str) -> str
    - wikipedia.search(query) for suggestions
    - wikipedia.summary(suggestions[0], sentences=5) for content
    - wikipedia.page(suggestions[0]) for URL
    - Return: title, URL, 5-sentence summary
    - Handle DisambiguationError → list options
    - Handle PageError → "No page found"

SYSTEM PROMPT
  "You are a knowledgeable research assistant with access to Wikipedia. When a
  user asks about a topic, person, place, or event, use the search_wikipedia tool
  to find accurate information. Summarise the key facts clearly, explain any
  complex concepts in simple terms, and highlight what makes the topic interesting
  or significant. Always be informative but concise."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← search_wikipedia tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, wikipedia
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for a topic and return a concise summary with the article URL.
    Handles disambiguation by listing options. Uses the wikipedia Python package — free.
    """
```

---

## Example Interaction

```
You: Tell me about the Turing Test

Agent:
Topic : Turing Test
URL   : https://en.wikipedia.org/wiki/Turing_test

The Turing test, originally called the imitation game, is a test of a machine's
ability to exhibit intelligent behaviour indistinguishable from that of a human.
Proposed by Alan Turing in 1950 in the paper "Computing Machinery and Intelligence",
it became a foundational concept in AI philosophy. A human evaluator judges text
conversations between a human and a machine — if the evaluator cannot reliably tell
which is which, the machine passes.

The test remains influential but controversial: passing it does not necessarily
mean the machine is "thinking", just that its output looks human-like.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.3` | Factual retrieval + light synthesis = moderate temperature |
| `sentences=5` | Enough context without overwhelming small local models |
| DisambiguationError handler | "Congo" and "Mercury" would otherwise crash silently |
| `wikipedia` package | Abstracts MediaWiki API, handles redirects, completely free |
