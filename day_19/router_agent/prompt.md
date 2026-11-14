# Router Agent — Prompts

---

## System Prompts
> Runtime instructions from `agent.py`. There are 4 prompts: one for the router, one per specialist.

### Router (`ROUTER_PROMPT`)
```
You are a router for a customer-support team.
Read the customer message and answer with EXACTLY ONE word:
  billing  -> invoices, payments, refunds, charges
  tech     -> bugs, crashes, wifi, passwords, how-to problems
  general  -> anything else (hours, greetings, feedback)

Examples:
  "Is invoice 1002 paid?"          -> billing
  "I was charged twice"            -> billing
  "The app crashes on startup"     -> tech
  "I forgot my password"           -> tech
  "What time do you open?"         -> general
  "Hello!"                         -> general

Answer with just the one word.
```

### Specialists
```
BILLING_PROMPT : You are a friendly billing specialist. Use lookup_invoice when an invoice number is given.
TECH_PROMPT    : You are a patient tech-support engineer. Use search_kb to find fixes, then explain step by step.
GENERAL_PROMPT : You are a polite front-desk assistant. Keep answers short and helpful.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a customer-support ROUTER agent CLI in Python using LangChain and LangGraph
with two tools.

STACK
  LLM       : Ollama llama3.2, temperature=0 (via langchain-ollama)
  Framework : LangGraph StateGraph with add_conditional_edges
  Data      : in-memory dicts (no API, no key)

STATE (TypedDict)
  question: str, route: str, answer: str

TOOLS (2)
  lookup_invoice(invoice_id: str) -> str   # reads INVOICES dict
  search_kb(keyword: str) -> str           # reads KNOWLEDGE_BASE dict (wifi/password/crash)

NODES
  router   : LLM call with ROUTER_PROMPT -> one word -> state["route"]
             fallback to "general" if the word is not billing/tech
  billing  : create_react_agent(llm, [lookup_invoice]) + BILLING_PROMPT
  tech     : create_react_agent(llm, [search_kb])      + TECH_PROMPT
  general  : plain LLM call with GENERAL_PROMPT (no tools)

GRAPH
  START -> router
  router -> (conditional on state["route"]) -> billing | tech | general
  billing / tech / general -> END

ROUTER PROMPT MUST INCLUDE few-shot examples (small models misroute without them)

ENTRY POINT (agent.py)
  build_agent(), ask(), interactive while-loop CLI
  Print "[router] -> <route>" so students can SEE the decision
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          <- lookup_invoice, search_kb
  agent.py          <- state, nodes, build_agent(), ask(), main()
  requirements.txt  <- langchain, langchain-ollama, langgraph, requests
```

---

## Tool Contracts
> Exact `@tool` docstrings from `tools.py`

```python
@tool
def lookup_invoice(invoice_id: str) -> str:
    """Look up an invoice by its number (e.g. 1001) and return amount and payment status."""

@tool
def search_kb(keyword: str) -> str:
    """Search the tech-support knowledge base for a keyword like wifi, password or crash."""
```

---

## Example Interaction

```
You: Is invoice 1002 paid?
  [router] -> billing

Agent: Invoice 1002 is for $120.00 and is overdue since 2026-10-20.

You: What are your hours?
  [router] -> general

Agent: (short, friendly reply from the general assistant)
```
> Exact wording varies with the model; the `[router]` line is the part to watch.

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0` | Routing must be consistent — same question, same route |
| One-word answer | Easy to parse and to map to a graph edge |
| Few-shot examples in router prompt | Without them llama3.2 sent an invoice question to `general` |
| Fallback to `general` | Never crash on an unexpected router reply |
| Specialists have separate tools | Each agent sees only the tools it needs → fewer wrong tool calls |
