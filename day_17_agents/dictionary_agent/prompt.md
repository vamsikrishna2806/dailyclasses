# Dictionary Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a knowledgeable vocabulary and language assistant.
When a user asks about a word, use the define_word tool to look it up.
Explain the definition clearly, highlight interesting usage, provide examples
in context, and suggest when and how to use the word naturally in conversation.
Help users expand their vocabulary in an engaging way.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational vocabulary assistant CLI agent in Python using LangChain
and LangGraph with one word definition tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.3 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  API       : Free Dictionary API (dictionaryapi.dev/api/v2/entries/en/) — free, no key

TOOL (1)
  define_word(word: str) -> str
    - GET https://api.dictionaryapi.dev/api/v2/entries/en/{word}
    - From response[0]: extract phonetic, meanings (up to 3)
    - For each meaning: partOfSpeech, definitions (up to 2), examples, synonyms
    - Return formatted string: word + phonetic, then per-part-of-speech sections

SYSTEM PROMPT
  "You are a knowledgeable vocabulary and language assistant. When a user asks
  about a word, use the define_word tool to look it up. Explain the definition
  clearly, highlight interesting usage, provide examples in context, and suggest
  when and how to use the word naturally in conversation. Help users expand
  their vocabulary in an engaging way."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← define_word tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def define_word(word: str) -> str:
    """
    Look up the definition, pronunciation, part of speech, usage examples,
    and synonyms for any English word. Uses Free Dictionary API — no API key.
    """
```

---

## Example Interaction

```
You: What does ephemeral mean?

Agent:
Word: ephemeral  /ɪˈfem(ə)r(ə)l/

[adjective]
  Definition : Lasting for a very short time.
  Example    : Fashions are ephemeral: new ones regularly drive out the old.
  Synonyms   : transitory, transient, fleeting, momentary, brief

Usage tip: Use "ephemeral" when you want to emphasise that something beautiful
or significant disappears quickly — like morning dew, a trending topic, or
the feeling after a great concert.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.3` | Factual enough for definitions, slight warmth for context |
| Single tool | One API call covers definition, phonetics, examples, synonyms |
| Free Dictionary API | No key needed, clean JSON, broad English vocabulary |
| Up to 3 meanings | Covers all major parts of speech without overwhelming the LLM |
