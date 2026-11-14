# How to Use — Router Agent 🚦

**What you will see:** you ask a customer-support question, and the agent first prints *which department it chose* (`billing`, `tech` or `general`), then that specialist answers.

---

## Step 1 — One-time setup (do this once per computer)

1. **Install Python 3.10 or newer** → https://www.python.org/downloads/ (tick *"Add Python to PATH"* on Windows)
2. **Install Ollama** (runs the AI on your own computer, free) → https://ollama.com/download
3. **Download the AI model** (about 2 GB, one time). Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

## Step 2 — Set up this project (do this once per folder)

Open a terminal **inside this folder** (`router_agent`), then:

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

The agent shows `You:` — type a question and press **Enter**. Type `q` to quit.

| Type this | Router should pick | Because |
|---|---|---|
| `Is invoice 1002 paid?` | `billing` | it is about an invoice |
| `Can I get a refund for last month?` | `billing` | money question |
| `My wifi keeps dropping` | `tech` | technical problem |
| `I forgot my password` | `tech` | account / tech help |
| `What are your opening hours?` | `general` | everything else |

**Real invoices in the demo data:** `1001` (paid) and `1002` (overdue). Other numbers → "No invoice found".

### Example session
```
You: Is invoice 1002 paid?
  [router] -> billing

Agent: Invoice 1002 is for $120.00 and is overdue since 2026-10-20.
```
👀 **Watch the `[router] -> ...` line** — that is the whole point of this example.

## Step 5 — Experiments to try (learn by breaking it)

1. Ask something that fits **two** departments: `My payment page crashes`. Which one wins?
2. Open `agent.py` and delete the examples inside `ROUTER_PROMPT`. Ask `Is invoice 1002 paid?` again. Does the router still get it right? (Small models need examples!)
3. Add a 4th department: add a node, a prompt, and an entry in `add_conditional_edges`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` / `ConnectError` | Ollama is not running. Start the Ollama app or run `ollama serve`. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| First answer is slow | Normal — the model is loading into memory. Next answers are faster. |
| Yellow `LangGraphDeprecatedSinceV10` warning | Harmless. The code still works. |
| Router picks the wrong department | Small AI models make mistakes. Make the examples in `ROUTER_PROMPT` clearer. |
