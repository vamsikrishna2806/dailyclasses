# How to Use — Hierarchical Agent 🏢

**What you will see:** you type a **product idea**. A manager first sends the **product team** (researcher → spec writer → lead) and then the **marketing team** (copywriter → social planner → lead). You get a product spec and a campaign.

> 🧩 **Architecture you are learning:** **Hierarchical teams (graphs inside a graph)** — a manager delegates to teams, and each team is its own small graph with workers and a lead.
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

Open a terminal **inside this folder** (`hierarchical_agent`), then:

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

The agent asks `Product idea:` — type a **product idea** in a few words and press **Enter**. Type `q` to quit.

Good things to try:
- `a note-taking app`
- `a language learning app`
- `a fitness app for busy parents`
- `a budget tracker for students`

### Example session
```text
Product idea: a note-taking app

  🏢 [manager] -> product
      🔎 [researcher]     asking the audience tool...
      📝 [spec_writer]    drafting features...
      👩‍💼 [product_lead]  merging into the product spec...
  🏢 [manager] -> marketing
      ✍️  [copywriter]     writing tagline + pitch...
      📣 [social_planner] writing social posts...
      👨‍💼 [marketing_lead] assembling the campaign...
  🏢 [manager] -> FINISH

Product Spec:
Fast search, Offline mode, Sync, and Tagging/Categorization.

CAMPAIGN
Tagline: "Organize Your Thoughts, Anywhere"
Pitch: Stay productive on-the-go with our note-taking app, featuring fast search and offline mode ...
Social posts:
1. "Stay organized and on top of your tasks with our note-taking app! 📝"
2. "Take your productivity to the next level with fast search, offline mode and syncing! 💻"
3. "Color-code your notes and categorize your thoughts with our intuitive tagging system! 🎨"
```

👀 **What to watch for:** Notice the **indentation**: `🏢 [manager] -> product` is the top level; the indented lines are the workers *inside* that team. The manager never sees individual workers — it only sees the team's final report. That is a **graph inside a graph**.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | Manager, plus prompts for 3 workers per team (researcher, spec writer, product lead, copywriter, social planner, marketing lead). |
| `TeamState` + `_linear_team()` | **Level 2:** a small graph `worker1 → worker2 → lead` with its own state. `build_product_team()` and `build_marketing_team()` plug in different workers. |
| `class State` | **Level 1:** the manager's state: `idea`, `product`, `marketing`, `next`, `steps`. |
| `manager_node` | Asks the LLM which team is next, then **guard rails** fix wrong choices (never repeat a team, product before marketing). |
| `build_agent()` | The manager's graph treats each team as ONE node: `product_node` calls `product_team.invoke(...)`; teams report back to the manager. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Add a third team, **`legal`**, with two workers (`risk_checker`, `lead`). Add a node and extend the manager prompt and routes.
2. Make the marketing team run *before* the product team. What breaks? (marketing needs the product spec as input!)
3. Print `product_team.get_graph().draw_ascii()` (needs `pip install grandalf`) to see a team's graph on its own.
4. Change `MAX_STEPS` to `2`. The manager is forced to FINISH early — see what is missing in the result.

## Troubleshooting

| Problem | Fix |
|---|---|
| The result has a strange extra heading | The lead agents reformat text; small models like to add markdown. It is cosmetic. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- What is a *sub-graph* and why is it useful?
- Why does the manager have guard rails instead of fully trusting the LLM?
- How do the teams report back to the manager? (an edge from each team node to `manager`)
