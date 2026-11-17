# How to Use — Debate Agent 🥊

**What you will see:** you type a **motion** (a statement to argue about). A PRO agent and a CON agent debate for 2 rounds, then a judge reads the whole transcript and names a winner.

> 🧩 **Architecture you are learning:** **Debate (adversarial loop)** — two agents with opposite jobs argue in turns and a neutral judge decides.
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

Open a terminal **inside this folder** (`debate_agent`), then:

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

The agent asks `Motion:` — type a **statement** that people can disagree about and press **Enter**. Type `q` to quit.

Good things to try:
- `Homework should be banned`
- `Cats are better than dogs`
- `School should start later in the morning`
- `Everyone should learn to code`

### Example session
```text
Motion: Homework should be banned

  --- the debate begins ---

  🟢 PRO: My opponent has not made a case for homework. Research suggests it can hinder creativity and
  increase stress. Banning homework would allow a more engaging, innovative learning environment ...

  🔴 CON: My opponent's point about research is misleading. Many studies show homework can improve
  academic performance, particularly in higher-level subjects ...

  🟢 PRO: That assertion is overstated. Research on this topic is inconsistent, and many studies fail to
  control for other factors ...

  🔴 CON: That claim relies on flawed assumptions. The relationship between homework and success is complex ...

  ⚖️  [judge] reading the whole debate...

⚖️  Verdict:
Winner: PRO
Reason: PRO provided more nuanced counterarguments and showed a deeper understanding of the research.
```
_(Speeches are shortened here. The judge's winner can change between runs — a good reason not to blindly trust an AI judge.)_

👀 **What to watch for:** Notice that every speech *answers the opponent's last point*. That only works because both debaters receive the **full transcript** each turn (see `State.speeches`). The loop `con → pro` repeats until `ROUNDS` is reached, then the edge goes to the judge.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `PRO_PROMPT`, `CON_PROMPT`, `JUDGE_PROMPT`. `ROUNDS = 2` controls the loop length. |
| `class State` | `speeches` is a growing list (the transcript), `round` counts finished rounds. |
| `pro_node`, `con_node`, `judge_node` | `speak()` reminds the model of its side EVERY turn (small models forget!). Only `con_node` increments `round`. |
| `build_agent()` | `add_conditional_edges("con", more_rounds, ...)` — after CON, either loop back to `pro` or go to `judge`. That one line makes the loop. |
| `ask()` / `main()` | `parse_winner()` in `tools.py` extracts PRO/CON from the judge's text. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Change `ROUNDS = 2` to `1`, then to `3`. How does the debate quality change? How long does it take?
2. Make the debaters speak in a funny style (e.g. *like a pirate*) by editing their prompts.
3. Add a third voice, **`moderator`**, who summarises after each round. (Add a node between `con` and the decision.)
4. Run the same motion twice. Does the judge always pick the same winner? What does that tell you about trusting an AI judge?

## Troubleshooting

| Problem | Fix |
|---|---|
| A debater argues for the wrong side | Small models sometimes lose track. The code reminds the side every turn, but it can still slip. Run again or use a bigger model. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Which function creates the loop? (the conditional edge `more_rounds`)
- Why does each debater get the whole transcript?
- Why is a debate more useful than asking one agent for both sides?
