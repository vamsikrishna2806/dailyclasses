# How to Use — Voting Panel Agent 🗳️

**What you will see:** you paste a **message**. Three jurors (strict, friendly, data analyst) vote SPAM / NOT_SPAM / UNSURE at the same time. Plain code counts the votes; only if there is no majority does a judge break the tie.

> 🧩 **Architecture you are learning:** **Voting / ensemble** — several agents with different personalities judge the same input and the majority wins.
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

Open a terminal **inside this folder** (`voting_agent`), then:

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

The agent asks `Message to check:` — paste or type any **short message** and press **Enter**. Type `q` to quit.

Good things to try:
- `URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1`
- `Hi Sam, are we still meeting for lunch at 1pm tomorrow?`
- `Your package delivery is delayed. Confirm your address to reschedule: www.parcel-help.net`
- `Congratulations! Your invoice 4521 is attached. Please review at www.docs-share.co`

### Example session
```text
Message to check: URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1

  🗳️  [strict]   UNSURE - Unsolicited link to claim a free gift card.
  🗳️  [friendly] SPAM - Contains suspicious link and urgent tone.
  🗳️  [evidence] SPAM - High score with multiple warning signs, likely SPAM.
  🧮 [tally]    votes = {'SPAM': 2}  ->  SPAM

🚫 FINAL: SPAM   (decided by majority vote)
```

A trickier message — the panel splits and the **judge** is called:
```text
Message to check: Free pizza Friday in the office kitchen at noon!!

  🗳️  [strict]   UNSURE - Unlikely to be a legitimate work event.
  🗳️  [friendly] NOT_SPAM - Unverified sender, but sounds like a legitimate office event.
  🗳️  [evidence] SPAM - High score with multiple exclamation marks and money-related word.
  🧮 [tally]    votes = {'NOT_SPAM': 1, 'SPAM': 1}  ->  NO MAJORITY
  ⚖️  [judge]    panel is split — breaking the tie

✅ FINAL: NOT_SPAM   (decided by judge (tie-break))
```

👀 **What to watch for:** Read the three `🗳️` lines — each juror gives a vote **and a reason**. Then `🧮 [tally]` shows the count. Try the 3rd and 4th examples: tricky messages make jurors disagree, and you may see `⚖️ [judge]` break a tie.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | Three personalities share one `VOTE_FORMAT`. The *Data Analyst* gets numbers from a tool. |
| `class State` | `strict`, `friendly`, `evidence` — one key per juror (they run in parallel), plus `counts`, `verdict`, `decided_by`. |
| `*_node` jurors | `evidence_node` first calls `spam_signals()` (plain code) and shows the facts to the model. |
| `tally_node` | **No LLM.** `parse_vote()` reads each reply, `tally()` needs at least 2 equal votes for a winner. |
| `build_agent()` | Fan-out from START to the jurors, fan-in to `tally`, then a conditional edge: majority → END, otherwise → `judge`. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Send an ambiguous message (e.g. `Your account needs verification`). Do the jurors agree?
2. Make the Strict juror even stricter, or turn the Friendly juror into a **gullible** one. How do results change?
3. Add two more jurors (5 in total) and require **3** votes for a majority in `tally()`.
4. Replace `spam_signals` with your own detector (e.g. count misspelled words).

## Troubleshooting

| Problem | Fix |
|---|---|
| The panel is wrong about a message | That is real life: panels reduce errors, they do not remove them. Look at the reasons to see which juror was misled. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Why do the jurors have DIFFERENT personalities instead of three identical copies?
- Who counts the votes — an LLM or code? Why?
- When does the judge run?
