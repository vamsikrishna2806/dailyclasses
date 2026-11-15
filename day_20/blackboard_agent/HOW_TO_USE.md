# How to Use — Blackboard Agent 📋

**What you will see:** you describe **meals and a budget**. Four specialists (nutritionist, chef, shopper, auditor) write to one shared *board*. If the shopping list is too expensive, the auditor **erases the menu** and the chef must redo it.

> 🧩 **Architecture you are learning:** **Blackboard (shared workspace)** — specialists never talk to each other — they watch a shared board and add their part when they can.
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

Open a terminal **inside this folder** (`blackboard_agent`), then:

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

The agent asks `Meal request:` — describe the **meals and add a budget like `under $20`** and press **Enter**. Type `q` to quit.

Good things to try:
- `Vegetarian dinners for 3 days under $20`
- `Cheap high-protein dinners for 3 days under $25`
- `Kid-friendly dinners for 3 days under $18`

### Example session
```text
Meal request: Vegetarian dinners for 3 days under $17

  📋 [board] -> nutritionist
       🥗 nutritionist wrote dietary rules on the board
  📋 [board] -> chef
       👨‍🍳 chef wrote a menu on the board
  📋 [board] -> shopper
       🛒 shopper listed 11 items, total $22.00
  📋 [board] -> auditor
       🧾 auditor: $22.00 is over $17 -> erasing menu, chef must redo it
  📋 [board] -> chef
       👨‍🍳 chef wrote a menu on the board (cheaper version)
  📋 [board] -> shopper
       🛒 shopper listed 6 items, total $10.50
  📋 [board] -> auditor
       🧾 auditor: APPROVED ✅ within budget
  📋 [board] -> DONE

MENU:
Day 1: Bean and Rice Bowl      - beans - rice - onion - tomato
Day 2: Lentil Soup             - lentils - rice - onion - tomato
Day 3: Pasta with Tomato Sauce - pasta - tomato - onion - beans

SHOPPING LIST: beans, rice, onion, tomato, lentils, pasta
TOTAL: $10.50  (budget $17)
VERDICT: APPROVED ✅ within budget
```
🔎 **See the loop?** `auditor` → `chef` → `shopper` → `auditor`. No line of code says "go back to the chef" — erasing the menu made the chef's rule true again. With a very tight budget (e.g. `under $9`) the loop hits `MAX_REVISIONS` and ends with `OVER BUDGET ⚠️`.

👀 **What to watch for:** Watch the `📋 [board] -> …` lines. The **controller is plain Python, not an AI**: it just asks *"whose rule is true right now?"* If the auditor says *over budget*, the menu is erased, the chef's rule becomes true again — and the loop happens **without any code that says "go back to the chef"**.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `NUTRITIONIST_PROMPT`, `CHEF_PROMPT`, `SHOPPER_PROMPT`. `MAX_REVISIONS = 2` limits how often the chef may be sent back. |
| `class State` + `new_board()` | `board` is ONE dict everybody reads and writes: request, budget, constraints, menu, ingredients, cost, verdict, feedback. |
| `RULES` | The heart of the pattern: for each specialist a tiny function — *"I may act when X is on the board and my part is not"*. |
| `controller_node` | Walks through `RULES` and wakes the first specialist that can contribute. Nobody can? → `DONE`. |
| specialist nodes + `build_agent()` | Each specialist edits a copy of the board; every specialist has an edge back to the controller. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Ask with a very low budget (`under $8`). The auditor will loop; how many revisions happen? What is the final verdict?
2. Add a specialist **`dessert_chef`** who may act when the menu exists but `dessert` is empty. You only need a rule, a node, and edges — no manager changes!
3. Change `MAX_REVISIONS` to `0` to see the result without the cost loop.
4. Edit prices in `PRICES` (`tools.py`) — e.g. make beans $6 — and watch the chef adapt.

## Troubleshooting

| Problem | Fix |
|---|---|
| Still `OVER BUDGET` at the end | After `MAX_REVISIONS` loops the auditor accepts defeat. A small model may not respect a tight budget. Try a bigger budget. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Who tells the specialists when to work? (nobody — their rules do)
- What makes the chef run again after the auditor? (the menu was erased so the chef's rule is true again)
- Why is the controller not an LLM?
