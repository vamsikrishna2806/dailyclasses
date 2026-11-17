# How to Use — RAG Team Agent 📚

**What you will see:** you ask a **question about a tiny company handbook**. A rewriter makes search keywords, plain code retrieves passages, an answerer replies with source ids like `[HR-1]`, and a fact-checker verifies every claim. Questions not covered get *"I could not find that"* instead of a guess.

> 🧩 **Architecture you are learning:** **Multi-agent RAG (retrieve · answer · verify)** — one agent finds sources, one answers only from them, and a checker sends unsupported answers back.
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

Open a terminal **inside this folder** (`rag_team_agent`), then:

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

The agent asks `Question:` — ask **a question a new employee might have** and press **Enter**. Type `q` to quit.

Good things to try:
- `How many vacation days do I get?`
- `Can I work from home?`
- `What is the password policy?`
- `How much can I claim for meals while travelling?`
- `What is the CEO's salary?   ← NOT in the handbook on purpose!`

### Example session
```text
Question: Can I work from home?

  🔍 [rewriter]   search keywords: work from home job
  📚 [retriever]  found: ['HR-3']
  💬 [answerer]   You can work from home up to 3 days per week, but you must have director approval for fully remote work. Tuesday and Thursday are office days for team meetings. [HR-3]
  🕵️  [checker]    UNSUPPORTED: You must have director approval for fully remote work.
  💬 [answerer]   Yes, you can work from home up to 3 days per week, but you need director approval for fully remote work. [HR-3]
  🕵️  [checker]    GROUNDED

Answer: Yes, you can work from home up to 3 days per week, but you need director approval for fully remote work. [HR-3]
   (✅ checked against the handbook)
```

A question the handbook cannot answer — the agent admits it instead of guessing:
```text
Question: What is the CEO's salary?

  🔍 [rewriter]   search keywords: CEO salary
  📚 [retriever]  found: nothing

Answer: I could not find that in the handbook.
   (⚠️ NO SOURCES)
```

👀 **What to watch for:** Check the `📚 [retriever] found: [...]` line, then the `🕵️ [checker]` line. If the checker says `UNSUPPORTED`, the answer goes back to the answerer. For the CEO question the retriever finds *nothing* and the agent honestly says it does not know — **no hallucination**.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `REWRITER_PROMPT`, `ANSWERER_PROMPT` ("ONLY from the context"), `CHECKER_PROMPT`. `MAX_ROUNDS = 2` limits retries. |
| `tools.py` | `DOCS` is the handbook (8 passages). `search_docs()` scores passages by keyword overlap — a stand-in for the embeddings/vector store you learned on day 12. |
| `class State` | `question`, `search_query`, `docs` (retrieved passages), `answer`, `verdict`, `rounds`. |
| nodes | `retriever_node` has **no LLM**. `checker_node` also *verifies the verifier* with plain Python: a flagged claim that appears word-for-word in the passages is accepted. |
| `build_agent()` | Two conditional edges: `after_retrieval` (nothing found → `no_answer`) and `after_check` (grounded → END, else → `answerer` again). |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Add a new passage to `DOCS` (e.g. *parking policy*) and ask about it.
2. Ask the CEO question again, then add a passage about it and ask once more. Watch the behaviour change with the knowledge, not the code.
3. Set `MAX_ROUNDS = 0`. What happens when the checker complains?
4. Replace the keyword search with a real vector search (use your day-12 code) — only `search_docs()` has to change.

## Troubleshooting

| Problem | Fix |
|---|---|
| `I could not find that in the handbook.` for a question that should be answerable | The keyword search found nothing. Rephrase with words that appear in the handbook (see `tools.py`). |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- What is *grounding* and why does the checker matter?
- Why does the retriever not use an LLM?
- What does the agent do when the retriever finds nothing? Why is that better than guessing?
