# Political Scenario Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are an expert political analyst and geopolitical strategist.
Your role is to analyze political scenarios, current events, elections, policy
decisions, international relations, and world affairs with clarity and balance.

When analyzing a scenario:
1. Use the web_search tool to find current, factual information.
2. Present multiple perspectives without personal bias.
3. Explain the key players, their motivations, and likely outcomes.
4. Highlight risks, opportunities, and historical context where relevant.
5. Keep your analysis concise, structured, and evidence-based.

Always cite your sources by mentioning where you found the information.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational political analysis CLI agent in Python using LangChain
and LangGraph with real-time DuckDuckGo web search.

STACK
  LLM       : Ollama llama3.2, temperature=0.3 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  Search    : DuckDuckGo via duckduckgo-search Python package
              (free, no API key, no registration required)

TOOL (1)

  web_search(query: str) -> str
    - Open a DDGS() context manager
    - Call ddgs.text(query, max_results=5) → list of result dicts
    - Each dict has: title, href (URL), body (snippet)
    - Return numbered list:
        "Web Search Results for: '{query}'\n
        [1] Title
            URL : https://...
            Info: snippet text

        [2] ..."
    - If no results: return "No results found for: '{query}'"
    - On any exception: return friendly error message, suggest rephrasing

BEHAVIOUR
  The agent may call web_search multiple times per question to:
    - Search different angles of the same political scenario
    - Look up historical context after getting current news
    - Verify or cross-check a claim from an earlier search result

SYSTEM PROMPT
  "You are an expert political analyst and geopolitical strategist.
  Your role is to analyze political scenarios, current events, elections,
  policy decisions, international relations, and world affairs with clarity
  and balance.

  When analyzing a scenario:
  1. Use the web_search tool to find current, factual information.
  2. Present multiple perspectives without personal bias.
  3. Explain the key players, their motivations, and likely outcomes.
  4. Highlight risks, opportunities, and historical context where relevant.
  5. Keep your analysis concise, structured, and evidence-based.

  Always cite your sources by mentioning where you found the information."

ENTRY POINT (agent.py)
  build_agent() → ChatOllama + create_react_agent + tools=[web_search]
  ask(agent, user_input) →
    invoke with [SystemMessage(SYSTEM_PROMPT), HumanMessage(user_input)]
    return result["messages"][-1].content
  main():
    - Print header: model name + tool name
    - Print 3 example queries:
        "What is the current political situation in France?"
        "Analyze the impact of US-China trade tensions."
        "What are the key issues in the upcoming UK elections?"
    - Interactive while-loop, exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← web_search tool definition
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langchain-community,
                       langgraph, duckduckgo-search
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring the LLM reads from `tools.py`

```python
@tool
def web_search(query: str) -> str:
    """
    Search the web for current political news, events, policies, elections,
    geopolitical developments, or any factual information about world affairs.
    Returns the top 5 search results with title, URL, and snippet.
    Uses DuckDuckGo — free, no API key required.
    """
```

---

## Example Interaction

```
You: Analyze the current US-China trade tensions and what it means for Asia.

Agent:
[calls web_search("US China trade tensions 2026")]
[calls web_search("US China trade impact Southeast Asia 2026")]

Based on current reporting from Reuters and the Financial Times:

KEY PLAYERS
  United States : Pushing tariffs on Chinese goods to protect domestic
                  manufacturing and reduce strategic dependencies.
  China         : Retaliating with counter-tariffs and diversifying
                  trade relationships across ASEAN nations.
  ASEAN         : Caught between two major partners; some nations
                  (Vietnam, India) are benefiting from supply-chain shifts.

LIKELY OUTCOMES
  Short term : Continued tit-for-tat tariff cycles, elevated prices
               for consumers in both economies.
  Medium term : Accelerated decoupling in semiconductors and EVs.
  Long term   : A bifurcated global trade system with two competing
                technology standards.

RISKS
  Spillover effects on global supply chains, risk of miscalculation
  escalating beyond trade into broader geopolitical confrontation.

Sources: Reuters (reuters.com), FT (ft.com), CFR analysis (cfr.org)
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.3` | Slight creativity for nuanced analysis; not fully deterministic |
| DuckDuckGo over SerpAPI/Tavily | Completely free, no API key, no rate-limit signup |
| `max_results=5` | Enough for multi-perspective coverage without token overload |
| Multi-search loop allowed | Political topics often need several queries to cover all angles |
| Structured system prompt (numbered) | Forces the LLM to follow a consistent analytical framework |
| `create_react_agent` | Handles multi-step tool calling loop automatically |
