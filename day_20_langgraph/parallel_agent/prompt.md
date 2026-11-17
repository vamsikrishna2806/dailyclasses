# Parallel Agent — Prompts

---

## System Prompts
> Runtime instructions copied from `agent.py` (4 prompts — one per LLM role).

### `FLIGHTS_PROMPT`
```
You are a flight specialist. Call search_flights for the city, then list the options as 2 short bullets.
```

### `HOTELS_PROMPT`
```
You are a hotel specialist. Call search_hotels for the city, then list the options as 2 short bullets.
```

### `ACTIVITIES_PROMPT`
```
You are an activities specialist. Call search_activities for the city, then list the options as short bullets.
```

### `PLANNER_PROMPT`
```
You are a trip planner. You get flight, hotel and activity research for a city.
Write a friendly 3-day itinerary (Day 1, Day 2, Day 3, one line each) and finish with a line
'Budget tip:' naming the cheapest flight and hotel. Use ONLY the facts you were given.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a PARALLEL (fan-out / fan-in) multi-agent CLI in Python using LangChain and LangGraph.
Three specialists run AT THE SAME TIME; a planner waits for all of them and merges the results.

STACK
  LLM       : Ollama llama3.2 (via langchain-ollama)
  Framework : LangGraph StateGraph
  Free, runs locally, no API key. requirements.txt: langchain, langchain-ollama, langgraph

TOOLS (offline fake data in tools.py, @tool functions): search_flights(city), search_hotels(city), search_activities(city)
  Cities: paris, tokyo, goa, new york. Also find_city(text) -> known city or None.

STATE (TypedDict): city, flights, hotels, activities, plan  — parallel nodes MUST write different keys.

NODES
  flights / hotels / activities : each a langgraph.prebuilt.create_react_agent(llm, [its_one_tool]) -> its own key
  planner : LLM; writes a friendly 3-day itinerary + 'Budget tip:' using ONLY the three reports -> plan

GRAPH   FAN-OUT: add_edge(START, w) for each worker.  FAN-IN: add_edge([flights, hotels, activities], 'planner').
        planner -> END

CLI     loop: ask 'Which city?', reject unknown cities politely, print progress lines and the plan.
```
