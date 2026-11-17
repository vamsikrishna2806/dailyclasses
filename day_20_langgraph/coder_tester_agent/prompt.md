# Coder-Tester Agent — Prompts

---

## System Prompts
> Runtime instructions copied from `agent.py` (3 prompts — one per LLM role).

### `CODER_PROMPT`
```
You are a PYTHON CODER. Write ONE Python function that solves the task.
Rules: no input(), no print(), no example usage, no explanation.
Return ONLY the code inside one ```python block.
```

### `TESTER_PROMPT`
```
You are a TESTER. Write 4 simple `assert` lines that test the function (call it by its name).
Rules: only assert lines, no imports, no explanation, no function definition.
Return ONLY the asserts inside one ```python block.
```

### `DEBUGGER_PROMPT`
```
You are a DEBUGGER. The code failed its tests. You get the code, the tests and the error.
Either the code OR a test may be wrong (for example a wrong expected value) — decide which and fix it.
Return TWO ```python blocks and nothing else:
1) the full corrected function
2) the full list of assert lines (fix any assert that is itself wrong)
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a CODER <-> TESTER multi-agent CLI in Python using LangChain and LangGraph.
Generate code, generate tests, run them for real, and loop through a debugger until they pass.

STACK
  LLM       : Ollama llama3.2 (via langchain-ollama)
  Framework : LangGraph StateGraph
  Free, runs locally, no API key. requirements.txt: langchain, langchain-ollama, langgraph
  temperature 0

TOOLS (tools.py)
  strip_code_fences(text) : return the code inside ```python ... ```
  run_python(code, timeout=5) : write code to a temp file, run with subprocess in the same interpreter,
                                return {ok: bool, output: last 6 lines of stdout+stderr}; handle TimeoutExpired

STATE (TypedDict): task, code, tests, passed (bool), output, fixes (int)

NODES
  coder     : ONE python function, no input()/print()/examples          -> code
  tester    : 4 simple assert lines that call the function              -> tests
  run_tests : NO LLM. run code + tests + print('ALL TESTS PASSED') ; passed = ok and marker found
  debugger  : gets code, tests, error; returns the corrected FULL function; fixes += 1

GRAPH   START -> coder -> tester -> run_tests -> conditional(passed or fixes >= MAX_FIXES ? END : debugger)
        debugger -> run_tests          MAX_FIXES = 3

CLI     loop: ask 'Coding task:', print progress lines, then PASSED/FAILED status, the code and the tests.
        Warn the student that running generated code is only safe for classroom demos.
```
