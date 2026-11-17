# How to Use — Planner-Executor Agent 🗺️

**What you will see:** you type a **word problem** with numbers. A planner writes a short numbered plan, an executor runs each step with a **calculator tool**, and an answerer writes the final sentence.

> 🧩 **Architecture you are learning:** **Plan-and-Execute** — think first and write a plan, then do the plan one step at a time with tools.
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

Open a terminal **inside this folder** (`planner_executor_agent`), then:

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

The agent asks `Task:` — type a **short maths word problem** and press **Enter**. Type `q` to quit.

Good things to try:
- `I buy 3 pens at $2 and 4 notebooks at $5, then get a 10% discount on the total. How much do I pay?`
- `Tickets cost $8 each. I buy 5 tickets and one $3 snack. What is the total?`
- `I have $50 and spend $12 on a book and $9 on lunch. How much is left?`
- `A bike costs $200 and a helmet $30, then 10% off the total. What do I pay?`

### Example session
```text
Task: I buy 3 pens at $2 and 4 notebooks at $5, then get a 10% discount on the total. How much do I pay?

  🧠 [planner] plan:
       1. Multiply 3 pens by $2
       2. Multiply 4 notebooks by $5
       3. Add the two results
       4. Multiply the total by 0.9
  🔧 [executor] step 1: CALC: 3 * 2   =>  6
  🔧 [executor] step 2: CALC: 4 * 5   =>  20
  🔧 [executor] step 3: CALC: 6 + 20   =>  26
  🔧 [executor] step 4: CALC: 26 * 0.9   =>  23.4

Answer: You pay $23.40 for the pens and notebooks after applying a 10% discount to the total cost of $26.
```

👀 **What to watch for:** Read the plan lines first (`🧠 [planner] plan:`), then watch the executor lines `🔧 [executor] step N: CALC: …  =>  result`. The **LLM only writes the expression**; the calculator tool does the arithmetic — that is why the numbers are exact.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `PLANNER_PROMPT` (numbered steps), `EXECUTOR_PROMPT` (one `CALC:` line), `ANSWERER_PROMPT`. |
| `class State` | `plan` = list of steps, `results` = list of results. The executor works on `plan[len(results)]`. |
| `planner_node`, `executor_node`, `answerer_node` | `run_tool()` reads the executor's `CALC: ...` line and calls the real `calculator` tool from `tools.py`. |
| `build_agent()` | `more_steps()` is the conditional edge: executor loops to itself until every step has a result, then goes to the answerer. |
| `tools.py` | `calculator` evaluates maths **safely** (no `eval()` of arbitrary code), `parse_plan` turns text into a list. `unit_convert` is there for an experiment. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Give the executor a second tool. In `tools.py` there is a ready `unit_convert`. Teach the executor prompt a `CONVERT: 10 km miles` line and handle it in `run_tool()`.
2. Print the plan only and stop (remove the executor). Is the plan alone useful? When would you show a plan to the user for approval first?
3. Ask a task with 5+ steps. `parse_plan(..., max_steps=4)` cuts the plan. Change the limit — what are the trade-offs?
4. Add a **replanner**: if a step's result is an error, ask the planner for a new plan.

## Troubleshooting

| Problem | Fix |
|---|---|
| The final number is wrong but every `CALC` line looks right | Then the **plan** was wrong, not the calculator. This is the key lesson: exact tools cannot fix a bad plan. Small models plan percentages and rates badly — try the suggested inputs, or a bigger model. |
| `Calculator error: ...` in a step | The executor wrote an expression the calculator cannot read. Run again; the safe calculator only accepts numbers and `+ - * / ** %`. |
| The final number is wrong | Check the `=>` results of each step. If a step is wrong, the plan or the expression was wrong — the answerer just repeats the results. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Why plan first instead of solving everything in one go?
- Who does the arithmetic — the LLM or the tool? Why does that matter?
- How does the graph know when to stop looping? (`len(results) == len(plan)`)
