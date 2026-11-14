# Reflection Agent — Prompts

---

## System Prompts
> Runtime instructions from `agent.py`. The SAME LLM plays three roles via three prompts.

### Writer (`WRITER_PROMPT`)
```
You are a skilled writer. Write a short, clear piece (max 100 words)
for the user's request. Return ONLY the text itself — no title, no intro like "Here is...".
```

### Critic (`CRITIC_PROMPT`)
```
You are a strict but fair editor. Review the draft against the request.
Check: clarity, tone, grammar, and whether it fully answers the request.
HARD RULE: the draft must be 100 words or fewer. If it is longer, it is NOT approved —
tell the writer to cut it.
- If it is good enough AND within the limit, reply with exactly: APPROVED
- Otherwise reply with 2-3 short, specific suggestions (one line each).
```
The critic's message also includes `Word count: <n> (limit 100)` so it can check the rule.

### Reviser (`REVISER_PROMPT`)
```
You are a writer revising your draft.
Rewrite it applying the editor's feedback, but keep it to 100 words or fewer
(cut words if needed — never make it longer).
Return ONLY the improved text. Do NOT start with "Here is the revised text" or any intro.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a REFLECTION agent CLI in Python using LangChain and LangGraph:
write a draft, critique it, revise it, and repeat until approved.

STACK
  LLM       : Ollama llama3.2, temperature=0.5 (via langchain-ollama)
  Framework : LangGraph StateGraph with a loop (revise -> critique)

STATE (TypedDict)
  request: str, draft: str, feedback: str, rounds: int

TOOL (1)
  count_words(text: str) -> str   # "81 words (medium)" — used to print draft length

NODES
  write    : LLM + WRITER_PROMPT   -> state["draft"], rounds = 0
  critique : LLM + CRITIC_PROMPT   -> state["feedback"]  ("APPROVED" or suggestions)
  revise   : LLM + REVISER_PROMPT  -> new draft, rounds += 1

GRAPH
  START -> write -> critique
  critique -> (conditional)
      feedback STARTS with "APPROVED" -> END   # not just contains the word
                                                # (code also overrides APPROVED if draft > 100 words)
      rounds >= MAX_ROUNDS(3) -> END      # safety limit so the loop always stops
      otherwise               -> revise -> critique   # THE LOOP

ENTRY POINT (agent.py)
  build_agent(), ask(), interactive while-loop CLI
  Print each step (writer / critic / reviser) and the FULL critic feedback
  Reject inputs shorter than 4 words ("good", "pls proceed" are not writing requests)
  Strip "Here is the revised text:" intro lines from model output (clean())
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          <- count_words
  agent.py          <- state, nodes, should_continue(), build_agent(), ask(), main()
  requirements.txt  <- langchain, langchain-ollama, langgraph, requests
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def count_words(text: str) -> str:
    """Count the words in a piece of text and report whether it is short, medium or long."""
```

---

## Example Interaction

```
You: Write a short email asking my boss for Friday off

  ✍️  [writer] first draft (81 words (medium))
  🧐 [critic] APPROVED ...

Final: Dear [Boss's Name],

I am writing to request this Friday off. I have a personal appointment ...
```
> A strong first draft is approved immediately. A weaker one shows extra lines:
> `🧐 [critic] <suggestions>` then `🔁 [reviser] revision #1`.

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| One LLM, three prompts | Roles come from prompts, not from different models |
| Critic replies `APPROVED` | A single keyword is an easy, reliable stop signal |
| `MAX_ROUNDS = 3` | Prevents an endless critique loop and runaway cost |
| `temperature=0.5` | Some creativity for writing; still stable enough to critique |
| Loop edge `revise -> critique` | The core of the Reflection pattern: improve, then re-check |
