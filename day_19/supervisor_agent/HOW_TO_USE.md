# How to Use — Supervisor Agent 🧑‍💼

**What you will see:** you type a **topic**. A "boss" agent sends a researcher (Wikipedia), then a writer, then a proofreader to work on it, and prints each decision. You get a short finished article.

> ⚠️ This example needs an **internet connection** (it reads Wikipedia).

---

## Step 1 — One-time setup (do this once per computer)

1. **Install Python 3.10 or newer** → https://www.python.org/downloads/ (tick *"Add Python to PATH"* on Windows)
2. **Install Ollama** (runs the AI on your own computer, free) → https://ollama.com/download
3. **Download the AI model** (about 2 GB, one time). Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

## Step 2 — Set up this project (do this once per folder)

Open a terminal **inside this folder** (`supervisor_agent`), then:

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

The agent asks `Topic:` — type a **subject** (not a question) and press **Enter**. Type `q` to quit.

Good topics (they have Wikipedia pages):
- `Black holes`
- `The Eiffel Tower`
- `Photosynthesis`
- `Albert Einstein`

### Example session
```
Topic: Black holes
  [supervisor] -> researcher      ← boss sends the researcher to Wikipedia
  [supervisor] -> writer          ← researcher is back; boss sends the writer
  [supervisor] -> proofreader     ← writer is back; boss sends the proofreader
  [supervisor] -> FINISH          ← everyone is done

Article: Black Holes: Cosmic Enigmas
A black hole is an astronomical body so dense that ...
(proofread ✔)
```
👀 **Watch the `[supervisor] -> ...` lines.** After *every* worker finishes, control returns to the supervisor. That "report back to the boss" shape is the whole lesson.

## Step 5 — Experiments to try (learn by breaking it)

1. Type a topic with no Wikipedia page, like `asdfghjk`. What does the researcher report?
2. In `agent.py`, change `MAX_STEPS = 6` to `2`. The supervisor will stop early. Why?
3. Add a 4th worker, e.g. a **translator** node that translates the article to Spanish. Add it to the supervisor prompt, the graph and the guard rails.
4. Read the "guard rails" comments in `supervisor_node`. Why does the code force the order instead of trusting the AI?

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve`. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `No Wikipedia page found` in the notes | Try a simpler / more general topic, e.g. `Moon` instead of `lunar surface geology`. |
| Wikipedia errors / timeouts | Check your internet connection and try again. |
| Takes a minute | Normal — 4 AI calls happen in a row (researcher, writer, proofreader + supervisor decisions). |
| Yellow `LangGraphDeprecatedSinceV10` warning | Harmless. The code still works. |
