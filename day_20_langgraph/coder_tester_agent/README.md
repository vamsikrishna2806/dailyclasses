# Coder-Tester Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A mini software team built with **LangChain + LangGraph + Ollama**: code → tests → real execution → debug loop.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `run_python` (subprocess runner with timeout), `strip_code_fences`
- **Architecture**: **Generate · Test · Debug loop** — one agent writes code, another writes tests, real Python runs them, and a debugger fixes failures.

```
START ─► coder ─► tester ─► run_tests ─► passed? ──yes──► END
                         ▲           │
                         │           no (rounds left)
                         └─ debugger ┘
```

**Key idea for students:** never *trust* generated code — **run it**. Putting a real tool (the Python runner) between the agents turns "I think it works" into "the tests pass".

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- is_palindrome(s) that ignores case and spaces
- fizzbuzz(n) returning a list of strings from 1 to n
- count_vowels(text) returning the number of vowels
- to_roman(n) converting 1-3999 to a Roman numeral
