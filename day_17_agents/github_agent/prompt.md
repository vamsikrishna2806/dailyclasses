# GitHub Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a helpful developer assistant that can search GitHub repositories.
When a user asks about open-source projects, libraries, or tools, use the
search_github_repos tool to find relevant repositories. Present the results
clearly — name, description, stars, language, and link. Help developers
discover the best tools for their needs and explain what each project does.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational GitHub repository search CLI agent in Python using LangChain
and LangGraph with one GitHub search tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.3 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  API       : GitHub REST API (api.github.com/search/repositories) — free, no key for read

TOOL (1)
  search_github_repos(query: str) -> str
    - GET https://api.github.com/search/repositories?q={query}&sort=stars&per_page=5
    - Headers: Accept: application/vnd.github.v3+json
    - For each of top 5 results: name, full_name, description, stars, language,
      updated_at, html_url
    - Return numbered list with all fields

SYSTEM PROMPT
  "You are a helpful developer assistant that can search GitHub repositories.
  When a user asks about open-source projects, libraries, or tools, use the
  search_github_repos tool to find relevant repositories. Present the results
  clearly — name, description, stars, language, and link. Help developers discover
  the best tools for their needs and explain what each project does."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← search_github_repos tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def search_github_repos(query: str) -> str:
    """
    Search GitHub for repositories matching a query. Returns the top 5 results
    with name, description, star count, language, and URL.
    Uses the GitHub public API — free, no authentication required.
    """
```

---

## Example Interaction

```
You: Find me Python libraries for building AI agents

Agent:
Top GitHub repositories for "Python AI agents":

1. microsoft/autogen ⭐ 32,100
   Language: Python
   A framework for building multi-agent AI applications.
   https://github.com/microsoft/autogen

2. langchain-ai/langgraph ⭐ 8,900
   Language: Python
   Build stateful, multi-actor LLM applications.
   https://github.com/langchain-ai/langgraph
...

The most popular option is AutoGen from Microsoft, great for multi-agent
orchestration. LangGraph is a strong choice if you're already using LangChain.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.3` | Discovery + recommendation needs some warmth but stays grounded |
| `sort=stars` | Most-starred = most battle-tested, most useful to developers |
| `per_page=5` | Five results fit cleanly in a chat response without overloading |
| No auth header | Public search API works without a token at modest rates |
| `updated_at` in output | Helps user gauge how actively maintained each repo is |
