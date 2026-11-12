# GitHub Agent

An open-source code discovery assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `search_github_repos` — repo search via [GitHub Public API](https://api.github.com/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Find the best Python web frameworks on GitHub
- Search for LangChain repos
- What are the most popular machine learning libraries?
