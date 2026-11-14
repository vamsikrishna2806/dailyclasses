# Supervisor Agent — Prompts

---

## System Prompts
> Runtime instructions from `agent.py`: one for the supervisor, one per worker.

### Supervisor (`SUPERVISOR_PROMPT`)
```
You are a supervisor managing a team of workers:
  researcher -> finds facts (Wikipedia)
  writer     -> turns the facts into a short article
  proofreader-> fixes grammar and polishes the article
Look at the progress so far and decide who works NEXT.
Typical order: researcher, then writer, then proofreader, then FINISH.
Answer with EXACTLY ONE word: researcher, writer, proofreader, or FINISH.
```

### Workers
```
RESEARCHER_PROMPT  : You are a researcher. Use wiki_summary to get facts about the topic. Report the key facts as bullet points.
WRITER_PROMPT      : You are a writer. Using the research notes, write a clear 80-word article. Return only the article.
PROOFREADER_PROMPT : You are a proofreader. Fix grammar and polish this article without changing its meaning. Return only the final article.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a SUPERVISOR-with-workers agent CLI in Python using LangChain and LangGraph.
A boss LLM delegates to three workers and takes their results back until done.

STACK
  LLM       : Ollama llama3.2, temperature=0 (via langchain-ollama)
  Framework : LangGraph StateGraph (hub-and-spoke)
  API       : Wikipedia REST API (en.wikipedia.org/api/rest_v1/page/summary/) — free, no key

STATE (TypedDict)
  task: str, notes: str, article: str, next: str, steps: int

TOOL (1)
  wiki_summary(topic: str) -> str
    - GET https://en.wikipedia.org/api/rest_v1/page/summary/{title}  (set a User-Agent header)
    - Return the "extract" field; friendly message if status != 200

NODES
  supervisor  : LLM + SUPERVISOR_PROMPT -> one word -> state["next"]
                GUARD RAILS (small models slip): no notes -> researcher;
                no article -> writer; article not proofread -> proofreader;
                proofread -> FINISH; steps >= MAX_STEPS(6) -> FINISH
  researcher  : create_react_agent(llm, [wiki_summary]) -> state["notes"]
  writer      : LLM + WRITER_PROMPT      -> state["article"]
  proofreader : LLM + PROOFREADER_PROMPT -> state["article"] (+ "(proofread ✔)" marker)

GRAPH
  START -> supervisor
  supervisor -> (conditional on state["next"]) -> researcher | writer | proofreader | END
  researcher / writer / proofreader -> supervisor      # every worker REPORTS BACK

ENTRY POINT (agent.py)
  build_agent(), ask(), interactive while-loop CLI
  Print "[supervisor] -> <worker>" at each decision
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          <- wiki_summary
  agent.py          <- state, nodes, build_agent(), ask(), main()
  requirements.txt  <- langchain, langchain-ollama, langgraph, requests
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def wiki_summary(topic: str) -> str:
    """
    Get a short factual summary of a topic from Wikipedia.
    Uses the free Wikipedia REST API — no API key.
    """
```

---

## Example Interaction

```
Topic: Black holes
  [supervisor] -> researcher
  [supervisor] -> writer
  [supervisor] -> proofreader
  [supervisor] -> FINISH

Article: Black Holes: Cosmic Enigmas

A black hole is an astronomical body so dense that its gravity warps spacetime,
trapping everything, including light, inside. ...

(proofread ✔)
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Workers always return to the supervisor | The supervisor sees progress and decides what is next (hub-and-spoke) |
| One-word supervisor answer | Easy to parse and map to graph edges |
| Code guard rails around the LLM choice | llama3.2 sometimes picks the wrong worker; rules keep the order safe |
| `MAX_STEPS = 6` | Hard stop against infinite delegation |
| Only the researcher has a tool | Least privilege — writer and proofreader just transform text |
