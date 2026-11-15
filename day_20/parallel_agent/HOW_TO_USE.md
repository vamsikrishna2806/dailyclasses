# How to Use — Parallel Agent ⚡

**What you will see:** you type a **city**. Three specialists — flights, hotels, activities — search at the same time (each with its own tool). When ALL are done, a planner merges them into a 3-day trip plan.

> 🧩 **Architecture you are learning:** **Parallel (fan-out / fan-in)** — independent jobs run at the same time, then one agent merges the results.
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

Open a terminal **inside this folder** (`parallel_agent`), then:

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

The agent asks `Which city?` — type one of the **4 known cities** (a sentence containing the name also works) and press **Enter**. Type `q` to quit.

Good things to try:
- `Paris`
- `Tokyo`
- `Goa`
- `I want to visit New York`

### Example session
```text
Which city? I want to visit Paris

  🎡 [activities]  searching...
  ✈️  [flights]     searching...
  🏨 [hotels]      searching...
  🧭 [planner]     all 3 reports arrived — merging into one plan

Trip plan:
Day 1: Arrive in Paris and check in to the Hostel Seine, then explore Montmartre.
Day 2: Visit the Louvre Museum, followed by an evening cruise along the Seine.
Day 3: Go up the Eiffel Tower for views of the city.

Budget tip: Budget Air ($310) with Hostel Seine ($45/night) is much cheaper than Air France + Hotel Lumière.
```
_(The order of the first three lines changes from run to run — they start together. The planner line is always last.)_

👀 **What to watch for:** Look at the order of the three `[flights] / [hotels] / [activities]` lines: it can be different every run, because they start together. The `[planner]` line always comes LAST — it waits for all three.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | One prompt per specialist plus `PLANNER_PROMPT`. Each specialist is a tiny ReAct agent with exactly one tool. |
| `class State` | Separate keys `flights`, `hotels`, `activities`. **Parallel nodes must write different keys**, otherwise they overwrite each other. |
| `*_node` functions | Each runs `run_worker(...)`, which lets the model call its tool. `planner_node` merges the three reports. |
| `build_agent()` | FAN-OUT: three `add_edge(START, worker)` lines. FAN-IN: `add_edge(["flights", "hotels", "activities"], "planner")` — a **list** of sources means *wait for all*. |
| `ask()` / `main()` | `find_city()` (in `tools.py`) spots the city name in your text. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Add a 4th parallel worker, **`weather`**, with its own tool and State key. Add one `add_edge(START, "weather")` and put it in the fan-in list.
2. Change the fan-in line to `g.add_edge("flights", "planner")` only. What happens to the other two reports? (The planner may run before they finish!)
3. Add a new city (e.g. `rome`) to `CITIES` in `tools.py` and plan a trip there.
4. Time a run with three workers, then imagine them running one after another. Why is parallel faster when work is independent? (With a single local Ollama the speed-up is small, but with real APIs it is large.)

## Troubleshooting

| Problem | Fix |
|---|---|
| `I only know: Paris, Tokyo, Goa, New York` | The demo uses a tiny offline database. Use one of those four cities, or add yours to `CITIES` in `tools.py`. |
| A specialist says it found no data | The model did not call the tool correctly. Run again — small models occasionally skip a tool call. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Why must each parallel node write a different State key?
- What does the *list* in `add_edge([...], "planner")` mean?
- When is parallel NOT a good idea? (when step B needs the result of step A)
