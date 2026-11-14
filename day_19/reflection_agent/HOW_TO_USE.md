# How to Use — Reflection Agent 🪞

**What you will see:** you ask for a short piece of writing. The agent writes a draft, an "editor" critiques it, and the agent rewrites it — repeating until the editor approves (or 3 rounds pass). You can watch every step.

---

## Step 1 — One-time setup (do this once per computer)

1. **Install Python 3.10 or newer** → https://www.python.org/downloads/ (tick *"Add Python to PATH"* on Windows)
2. **Install Ollama** (runs the AI on your own computer, free) → https://ollama.com/download
3. **Download the AI model** (about 2 GB, one time). Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

## Step 2 — Set up this project (do this once per folder)

Open a terminal **inside this folder** (`reflection_agent`), then:

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

The agent asks `What should I write? (q to quit):`

👉 **Tell it WHAT to write, in a full sentence.** Answers like `good` or `ok` are rejected — they are not writing requests.

Good requests:
- `Write a short email asking my boss for Friday off`
- `Write a product description for a reusable water bottle`
- `Explain what an API is to a 10-year-old`
- `Write a poem about rain`

Type `q` to quit.

### How to read the output
```
  ✍️  [writer] first draft (83 words (medium))     ← step 1: first draft
  🧐 [critic]                                      ← step 2: editor's feedback
       Suggestion 1: ...
       Suggestion 2: ...
  🔁 [reviser] revision #1 (70 words (medium))     ← step 3: rewrite using feedback
  🧐 [critic]
       APPROVED                                    ← editor is happy → loop stops

Final: <the improved text>
```
- The loop stops when the critic's reply **starts with `APPROVED`**, or after **3 revisions** (safety limit).
- Drafts must stay **100 words or fewer**.
- Sometimes the first draft is approved at once — then you will see no revision. Try a harder request to see the loop work.

## Step 5 — Experiments to try (learn by breaking it)

1. Open `agent.py` and change `MAX_ROUNDS = 3` to `1`. How does the result change?
2. Make the critic **stricter**: in `CRITIC_PROMPT` add *"Be very picky about tone."*
3. Change `MAX_WORDS = 100` to `40`. Does the writer obey?
4. Give a vague request like `Write something nice about my teacher` and compare it with a detailed one.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` / `ConnectError` | Ollama is not running. Start the Ollama app or run `ollama serve`. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `⚠️ Describe what to write...` | Your input was too short. Type a full request (4+ words). |
| Final text contains `[Your Name]` | Normal for generic writing — the agent does not know your name. Add it to your request: *"...sign it as Vamsi"*. |
| The critic contradicts itself | Small AI models are imperfect critics. This is a great discussion point: that is why the loop has a 3-round limit. |
| First answer is slow | Normal — the model is loading into memory. |
