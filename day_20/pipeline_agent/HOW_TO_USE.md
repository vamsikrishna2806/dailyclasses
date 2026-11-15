# How to Use — Pipeline Agent 🏭

**What you will see:** you type a **blog topic**. Four agents — outliner, writer, editor, headline writer — work one after another and a plain-Python quality gate measures the result. You get a finished mini blog post.

> 🧩 **Architecture you are learning:** **Pipeline (assembly line)** — agents work in a fixed order and each one passes its result to the next.
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

Open a terminal **inside this folder** (`pipeline_agent`), then:

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

The agent asks `Blog topic:` — type a **topic** (a few words) and press **Enter**. Type `q` to quit.

Good things to try:
- `Why sleep matters`
- `Learning to cook`
- `Benefits of walking`
- `How volcanoes work`

### Example session
```text
Blog topic: Why sleep matters

  1/5 🗂️  [outliner]  planning the structure...
  2/5 ✍️  [writer]    writing the first draft...
  3/5 🧹 [editor]    polishing the draft...
  4/5 📰 [headline]  choosing a headline...
  5/5 📏 [quality]   measuring the result (plain code, no AI)

# Sleeping Well: The Key to a Healthier, Happier You

Sleep is essential for physical and mental restoration, allowing the body to repair and recharge. During sleep, the body
repairs and regenerates damaged cells, builds bone and muscle, and strengthens its immune system. Chronic sleep deprivation,
however, can have severe consequences ... (shortened here)

(106 words · reading time 32 sec)
```
_(Your text will be different — the AI writes something new each time. The five numbered lines will not.)_

👀 **What to watch for:** Watch the numbered lines `1/5 … 5/5`. They always appear in the same order — the order is fixed by the graph's edges, nobody "decides" it. That is the whole lesson of a pipeline.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `OUTLINER_PROMPT`, `WRITER_PROMPT`, `EDITOR_PROMPT`, `HEADLINE_PROMPT` — one job description per agent. |
| `class State` | The *baton*: `topic → outline → draft → edited → headline → report`. Each agent fills ONE field. |
| `*_node` functions | Each takes the state, calls the LLM once, returns the field it owns. `quality_gate_node` uses **no LLM** — just `tools.py` helpers. |
| `build_agent()` | Six `add_edge` lines in a straight line: `START → outliner → writer → editor → headline → quality_gate → END`. |
| `ask()` / `main()` | `ask()` runs the graph; `main()` is the input loop. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Add a 5th agent, **`translator`**, after the editor that translates the post into Spanish. You need: a prompt, a field in `State`, a node function, one new node and two changed edges.
2. Swap the order of `writer` and `editor` in `build_agent()` (edit before writing!). Run it. Why does the result get worse?
3. Change the writer prompt from *about 120 words* to *about 40 words*. Check the quality report: does the word count follow?
4. Remove the `quality_gate` node. Which edges must you change? This is the power of graphs — steps are easy to add and remove.

## Troubleshooting

| Problem | Fix |
|---|---|
| The post is much longer/shorter than 120 words | The model only *approximately* follows length. The quality gate shows the real number. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Who decides the order of the agents — an LLM or the graph? (the graph)
- Why does the quality gate not use an LLM? (counting is exact; use code when code is enough)
- What would break if two agents wrote to the same State field?
