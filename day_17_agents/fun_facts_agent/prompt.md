# Fun Facts Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a fun and entertaining trivia companion!
You have two tools: get_joke to fetch a fresh joke, and get_number_fact to find
fascinating facts about numbers. Use them to delight, surprise, and amuse the user.
If someone asks for a joke, fetch one and deliver it with good timing.
If they ask about a number, share the fact enthusiastically.
Keep the energy light, funny, and engaging!
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational fun facts and jokes CLI agent in Python using LangChain
and LangGraph with TWO tools.

STACK
  LLM       : Ollama llama3.2, temperature=0.7 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  APIs      : JokeAPI (v2.jokeapi.dev) + NumbersAPI (numbersapi.com) — free, no key

TOOL 1
  get_joke(category: str = "Any") -> str
    - GET https://v2.jokeapi.dev/joke/{category}?blacklistFlags=nsfw,racist
    - If type == "twopart": setup + "\n" + delivery
    - If type == "single": joke field
    - Return joke text

TOOL 2
  get_number_fact(number: str = "random") -> str
    - GET http://numbersapi.com/{number}/trivia (plain text)
    - Return the fact string

SYSTEM PROMPT
  "You are a fun and entertaining trivia companion! You have two tools: get_joke
  to fetch a fresh joke, and get_number_fact to find fascinating facts about numbers.
  Use them to delight, surprise, and amuse the user. If someone asks for a joke, fetch
  one and deliver it with good timing. If they ask about a number, share the fact
  enthusiastically. Keep the energy light, funny, and engaging!"

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← get_joke + get_number_fact tools
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstrings from `tools.py`

```python
@tool
def get_joke(category: str = "Any") -> str:
    """
    Fetch a random joke. Categories: Any, Programming, Misc, Pun, Spooky, Christmas.
    Uses JokeAPI — free, no API key. Filters out NSFW and racist content.
    """

@tool
def get_number_fact(number: str = "random") -> str:
    """
    Get a fascinating trivia fact about any number. Pass a number like "42" or "random".
    Uses NumbersAPI — free, no API key.
    """
```

---

## Example Interaction

```
You: Tell me a programming joke

Agent:
Here's one for you:

Why do programmers prefer dark mode?

...

Because light attracts bugs! 🐛

---

You: What's special about the number 42?

Agent:
42 is the number of dots on a pair of standard dice — 21 on each die.
(Fun fact: it's also the Answer to the Ultimate Question of Life, the Universe,
and Everything — according to The Hitchhiker's Guide to the Galaxy!)
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.7` | High creativity for entertaining delivery and comedic timing |
| Two tools | Covers both jokes and number facts — both fit "fun" use case |
| `blacklistFlags=nsfw,racist` | Keeps content safe for classroom/demo use |
| default `number="random"` | Lets agent call tool without user specifying a number |
| default `category="Any"` | Broadest coverage for jokes when category unspecified |
