# How to Use — Human-in-the-Loop Agent 🙋

**What you will see:** the agent writes an email, then **stops and waits for you**. Nothing is "sent" until you type `approve`. You can ask for rewrites as many times as you like.

> This demo does **not** really send email. "Sending" saves the email into a file called `outbox.txt` in this folder.

---

## Step 1 — One-time setup (do this once per computer)

1. **Install Python 3.10 or newer** → https://www.python.org/downloads/ (tick *"Add Python to PATH"* on Windows)
2. **Install Ollama** (runs the AI on your own computer, free) → https://ollama.com/download
3. **Download the AI model** (about 2 GB, one time). Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

## Step 2 — Set up this project (do this once per folder)

Open a terminal **inside this folder** (`human_in_loop_agent`), then:

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

## Step 4 — Answer the 4 questions

The agent asks **numbered questions**. Answer each one and press **Enter**:

| # | Question | Type something like | ❌ Not this |
|---|---|---|---|
| 1 | Your name (used to sign the email) — asked **once** | `Vamsi` | `approve` |
| 2 | What should the email say? | `Ask Priya to move tomorrow's meeting to 3pm` | `ok` (too short) |
| 3 | Recipient's email address | `priya@example.com` | `priya` (needs `@` and `.com`) |
| 4 | Recipient's name | `Priya` | *(empty)* |

If an answer looks wrong the agent says `⚠️` and **asks again** — you can't break it.

## Step 5 — Review the draft (the human-in-the-loop moment!)

The agent prints the draft and **pauses**:

```
📧 DRAFT  (to: Priya <priya@example.com>)
----------------------------------------
Dear Priya,
Could you please move tomorrow's meeting to 3pm? ...
Best regards,
Vamsi
----------------------------------------
👉 Type  approve  to SEND, or type what to change (e.g. 'make it shorter'):
```

You have two choices:

| You type | What happens |
|---|---|
| `approve` | ✅ Email is "sent" (saved to `outbox.txt`) |
| `make it shorter` / `more formal` / `mention it is urgent` | 🔁 The AI rewrites the draft and shows it again |
| *(just Enter)* | Nothing — it asks again. Empty never sends. |

⚠️ **Type just the single word `approve` to send.** Something like `change the name and approve` counts as a *change request*, so you will see a new draft first, then type `approve`.

## Step 6 — Check the result

After `approve` you will see:
```
✅ Email to priya@example.com saved in outbox.txt
```
Open `outbox.txt` in this folder to see every email you approved. The agent then asks for a **new email** — type `q` at question 2 to quit.

## Step 7 — Experiments to try (learn by breaking it)

1. Reject the first draft **three times** with different feedback. Does the AI follow each instruction?
2. Open `agent.py` and find `interrupt(...)`. Comment it out — now the email is sent with **no** human check. That is exactly why this pattern exists!
3. In `tools.py`, change `send_email` to print to the screen instead of writing a file.
4. Try a request with an urgent tone: `Tell Priya the server is down and we need help now`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` / `ConnectError` | Ollama is not running. Start the Ollama app or run `ollama serve`. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| Draft contains `[Name]`-style placeholders | Small models sometimes do this. Reply `remove the placeholders` and it will rewrite. |
| Typo in the email address (e.g. `gmial.com`) | The agent only checks the *shape* (`name@domain.com`), not that the address exists. Check the `to:` line before you approve. |
| Can't find `outbox.txt` | It appears in this folder after your first `approve`. |
| Yellow `LangGraphDeprecatedSinceV10` warning | Harmless. The code still works. |
