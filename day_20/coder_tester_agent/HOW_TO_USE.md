# How to Use — Coder-Tester Agent 👩‍💻

**What you will see:** you describe a **small Python function**. A coder writes it, a tester writes `assert` lines, a *real Python process* runs them, and — if something fails — a debugger fixes the code and it is tested again (max 3 fixes).

> 🧩 **Architecture you are learning:** **Generate · Test · Debug loop** — one agent writes code, another writes tests, real Python runs them, and a debugger fixes failures.
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

Open a terminal **inside this folder** (`coder_tester_agent`), then:

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

The agent asks `Coding task:` — describe **one small function** with its name and press **Enter**. Type `q` to quit.

Good things to try:
- `is_palindrome(s) that ignores case and spaces`
- `fizzbuzz(n) returning a list of strings from 1 to n`
- `count_vowels(text) returning the number of vowels`
- `to_roman(n) converting 1-3999 to a Roman numeral`

### Example session
```text
Coding task: word_frequency(text) returning a dict of lowercase word counts that ignores punctuation

  👩‍💻 [coder]     writing the function...
  🧪 [tester]    writing asserts...
  ▶️  [runner]    ❌ assert word_frequency("This is a test. This test is only a test.") == {'this': 2, ... 'test': 2, ...}
                     -> but it returned {'a': 2, 'is': 2, 'test': 3, 'this': 2, 'only': 1}
  🐞 [debugger]  fixing the code (fix #1)...
  ▶️  [runner]    ✅ all tests passed

✅ PASSED all tests

--- code ---
import re
def word_frequency(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return {word: words.count(word) for word in set(words)}
```
🔎 **Look closely:** the code was right all along — the *test* expected `'test': 2` but the word appears 3 times. The runner reported what the function **really returned**, and the debugger fixed the **test**. (When you run it, a simple task like `is_prime(n)` often passes first time with no debugger at all.)

👀 **What to watch for:** Look for the `▶️ [runner]` line: it says ✅ or ❌ with the real error. If ❌, a `🐞 [debugger]` line follows and the runner runs again — that is the loop. The runner is **plain Python, not an AI**: facts beat opinions.

## Step 5 — Read the code (10 minutes)

Open `agent.py`. Every agent file in this course has the **same 5 parts, top to bottom**:

| Part in `agent.py` | What it is |
|---|---|
| `PROMPTS` at the top | `CODER_PROMPT`, `TESTER_PROMPT`, `DEBUGGER_PROMPT`. `MAX_FIXES = 3` limits the loop. |
| `class State` | `code`, `tests`, `passed`, `output` (the error text), `fixes` (how many repairs so far). |
| `coder_node`, `tester_node`, `debugger_node` | All use `strip_code_fences()` to pull code out of the model's ```python block. |
| `run_tests_node` | **No LLM.** Joins code + asserts, runs them via `run_python()` in a separate process with a 5-second timeout. |
| `build_agent()` | `after_tests()` decides: pass or limit reached → END, else → debugger. Then `debugger → run_tests` closes the loop. |

`tools.py` holds the helper functions / tools. `prompt.md` shows every prompt and a *build prompt* you can give any AI to recreate this agent.

## Step 6 — Experiments (learn by breaking it)

1. Ask for something hard (`to_roman`) and count how many fixes it needs. Try 2-3 different tasks.
2. Set `MAX_FIXES = 0`. What happens when the first attempt fails?
3. In `TESTER_PROMPT`, ask for 8 asserts instead of 4. Are there more failures? Are the tests themselves ever wrong?
4. Break a test on purpose (edit `tests` in the state) and see whether the debugger fixes the *code* or the *test*.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Timed out after 5s (infinite loop?)` | The generated code never ended. The runner killed it — the debugger will try to fix it. |
| Tests fail because the **test** is wrong | Normal! LLM-written tests can be wrong too. The debugger prompt says either side may be wrong. |
| `Connection refused` / `ConnectError` to localhost | Ollama is not running. Start the Ollama app or run `ollama serve` in another terminal. |
| `model "llama3.2" not found` | Run `ollama pull llama3.2` |
| `ModuleNotFoundError: langgraph` (or `langchain_ollama`) | The virtual environment is not active. Run the *activate* command from Step 2 again. |
| PowerShell says *"running scripts is disabled"* | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt instead). |
| `ImportError: DLL load failed ... Application Control policy has blocked this file` | Your PC's security policy blocks one of the Python packages (`ormsgpack`). Ask your teacher/IT to allow it, or run on another computer. |
| Yellow `LangGraphDeprecatedSinceV10` / `LangChainDeprecationWarning` | Harmless warnings. The code still works. |
| The answer is a bit different every time | Normal — language models are not deterministic. The *shape* of the run (which agents ran, in what order) should stay the same. |
| A small model sometimes gives a silly answer | `llama3.2` is a small 3B model. That is why the code has *guard rails* (checks in plain Python). Try again, or switch `OLLAMA_MODEL` to a bigger model. |

## Check yourself ✅

- Why is `run_tests_node` not an LLM node?
- What stops the loop from running forever?
- ⚠️ Why should you only run code you trust? (the runner executes whatever the model wrote)
