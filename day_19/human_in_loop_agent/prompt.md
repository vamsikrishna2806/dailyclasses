# Human-in-the-Loop Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `DRAFT_PROMPT`

```
You are an email assistant. Write a short, polite email (max 80 words)
for the user's request. Start with "Dear <recipient name>," and end with
"Best regards," followed by the sender's name. Use the real names you are given and
NEVER leave placeholders like [Recipient] or [Your Name].
Return ONLY the email body — no subject line, no extra comments.
```

The draft node always sends the names along with the request:
```
Recipient name: <to_name>
Sender name: <sender>
Request: <original request>
```

When the human asks for changes, it also adds:
```

Previous draft:
<draft>

Human feedback — please apply it:
<what the human typed>
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a HUMAN-IN-THE-LOOP email assistant CLI in Python using LangChain and LangGraph.
The graph must PAUSE for human approval before the risky action (sending).

STACK
  LLM          : Ollama llama3.2, temperature=0.4 (via langchain-ollama)
  Framework    : LangGraph StateGraph
  Pause/resume : langgraph.types.interrupt and Command(resume=...)
  Checkpointer : MemorySaver  (REQUIRED — saves the paused state)

STATE (TypedDict)
  request: str, to: str, to_name: str, sender: str, draft: str, feedback: str, result: str

TOOL (1)
  send_email(to: str, subject: str, body: str) -> str
    - Demo version: append the email to outbox.txt (no real SMTP)

NODES
  draft        : LLM + DRAFT_PROMPT (include previous draft + feedback if present)
  human_review : decision = interrupt({"to":..., "draft":...}) -> state["feedback"]
  send         : calls send_email

GRAPH
  START -> draft -> human_review
  human_review -> (conditional)
      feedback is "approve"/"a"/"yes"/"y" -> send -> END
      anything else                       -> draft   # redraft with the human's notes

RUNNER (run_once)
  config = {"configurable": {"thread_id": ...}}
  out = agent.invoke(initial_state, config)
  while "__interrupt__" in out:
      show out["__interrupt__"][0].value to the user, read their answer
      out = agent.invoke(Command(resume=answer), config)

ENTRY POINT (agent.py)
  Interactive CLI with numbered, example-rich prompts: 1) sender name  2) request
  3) recipient email  4) recipient name, then run_once()
  Validate input with an ask_until_valid(prompt, is_ok, hint) helper:
    name not "approve"/"q"; request >= 3 words; email must look like name@domain.com
  An EMPTY answer at the review step must never count as approval
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          <- send_email
  agent.py          <- state, nodes, build_agent(), run_once(), main()
  requirements.txt  <- langchain, langchain-ollama, langgraph, requests
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    'Send' an email. For this demo it appends the email to outbox.txt
    (a real app would call SMTP / Gmail API here). This is the RISKY action
    that a human must approve first.
    """
```

---

## Example Interaction

```
Your name: Vamsi                      (asked once at start-up)
Request: Ask Priya to move tomorrow's meeting to 3pm
Send to (email): priya@example.com
Recipient's name: Priya

📧 DRAFT for priya@example.com:
----------------------------------------
Hi Priya,

I was wondering if you could move tomorrow's meeting to 3pm instead ...
----------------------------------------
Reply with ONLY 'approve' to send, or tell me what to change: make it shorter

📧 DRAFT for priya@example.com:
----------------------------------------
Hi Priya,

Could you please move tomorrow's meeting to 3pm? ...
----------------------------------------
Reply with ONLY 'approve' to send, or tell me what to change: approve

Agent: Email to priya@example.com saved in outbox.txt
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `interrupt()` before `send_email` | Irreversible actions need a human decision first |
| `MemorySaver` checkpointer | Without it the graph cannot remember where it paused |
| `thread_id` per email | Each request gets its own saved conversation |
| Any text other than "approve" = feedback | One input box handles both approving and editing |
| `send_email` writes to a file | Safe to demo; swap for a real API later |
