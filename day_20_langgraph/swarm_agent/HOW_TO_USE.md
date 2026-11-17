# How to Use — Swarm Agent 🐝

**What you will see:** you play a **customer** writing to an online shop. A front-desk agent passes you to the orders agent, which may pass you on to the refunds agent. Every agent announces who it hands you to.

> 🧩 **Architecture you are learning:** **Swarm (peer-to-peer hand-offs)** — there is no boss — each agent decides who should take over next.
> Open **`architecture.html`** in your browser first. Click through the steps on the page; each step lights up the part of the diagram that is working.

---

## Step 1 — One-time setup (do this once per computer)

1. **Install Python 3.10 or newer** → https://www.python.org/downloads/ (tick *"Add Python to PATH"* on Windows)
2. **Install Ollama** (runs the AI on your own computer, free) → https://ollama.com/download
3. **Download the AI model** (about 2 GB, one time). Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

## Step 2 — Set up this project (do this once per folder)

Open a terminal **inside this folder** (`swarm_agent`), then:

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

✅ When the virtual environment is active, your prompt starts with `(.venv)`.

## Step 3 — Run it

Make sure Ollama is running (the Ollama icon in your taskbar/menu bar, or run `ollama serve` in another terminal), then:

```bash
python agent.py
```

## Step 4 — What to type

The agent asks `Customer:` — write a **customer message that contains a 4-digit order number** and press **Enter**. Type `q` to quit.

Good things to try:
- `Order 5001 arrived broken, I want my money back`
- `Where is my order 5002?`
- `I want a refund for order 5003`
- `Hi, how are you today?`

### Example session
```text
Customer: Order 5001 arrived broken, I want my money back

  🛎️  [triage] Sorry to hear that your order arrived broken, I'm going to pass this on to our orders team.
       ↪ hands off to: orders
       🔧 tool get_order_status -> Order 5001: Laptop stand, $39.00, status = delivered (delivered 2026-11-02).
  📦 [orders] We apologize for the inconvenience. We will process a full refund for your order immediately.
       ↪ hands off to: refunds
       🔧 tool issue_refund -> Refund approved: $39.00 for order 5001 returns to the customer's card in 3-5 days.
  💸 [refunds] The refund for your order 5001 has been approved for $39.00 and will be returned in 3-5 days.
       ↪ hands off to: done
```

A second example — order `5002` is only *shipped*, so Orders answers and ends the call itself:
```text
Customer: Where is my order 5002?

  🛎️  [triage] Sorry about that, let me get our orders team to look into it for you.
       ↪ hands off to: orders
       🔧 tool get_order_status -> Order 5002: Wireless mouse, $25.00, status = shipped (in transit, arrives in 2 days).
  📦 [orders] Your order 5002 has been shipped and is in transit, arriving in 2 days.
       ↪ hands off to: done
```

👀 **What to watch for:** Read the `↪ hands off to:` lines. Nobody tells the agents the order — **each agent ends its reply with `HANDOFF: <name>`** and a conditional edge reads that line. Compare with the Supervisor agent from day 19, where a boss decided everything.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `TRIAGE_PROMPT`, `ORDERS_PROMPT`, `REFUNDS_PROMPT` all end with `HANDOFF_RULE`: the reply format: `HANDOFF:` followed by `orders`, `refunds` or `DONE`. |
| `class State` | `active` = who speaks next, `log` = what has been said, `hops` = how many hand-offs so far. |
| `*_node` functions | `orders_node` and `refunds_node` are *tool-first*: plain code finds the order number and runs the tool, then the LLM explains the result. `finish_turn()` records the reply and the next agent. |
| `build_agent()` | A loop adds a conditional edge from **every** agent using `next_agent()`. Any agent may hand off to any other. |
| `tools.py` | `get_order_status`, `issue_refund` (fake order database) and `parse_handoff()` which reads the `HANDOFF:` line. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Order `5002` is *shipped*. Ask for a refund for it. What does the orders agent do and why does it NOT hand off to refunds?
2. Order `5003` is already refunded. Ask for a refund. What happens?
3. Add a 4th agent, **`tech_support`**, and let triage hand off to it for messages about the app. You need a prompt, a node, an entry in `ICONS`, `routes` and `next_agent`.
4. Set `MAX_HOPS = 2`. The swarm now stops early. Why do we need a hop limit?

## Troubleshooting

| Problem | Fix |
|---|---|
| `No order found with id ''` | Your message has no 4-digit number. Try `Order 5001 ...` |
| An agent forgets the `HANDOFF:` line | Small models sometimes do. `SAFETY_NET` in `agent.py` supplies a sensible default (triage → orders, others → done). |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Who decides the next agent in a swarm? (the current agent)
- How is this different from the Supervisor pattern?
- What protects us from agents passing the customer around forever? (`MAX_HOPS`)
