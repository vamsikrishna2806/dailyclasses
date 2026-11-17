"""
CODER <-> TESTER multi-agent  (generate -> test -> debug loop)
--------------------------------------------------------------
The CODER writes a function. The TESTER writes asserts. A REAL Python process
runs them (no AI there!). If they fail, the DEBUGGER fixes the code and we test again.

    START -> coder -> tester -> run_tests -> passed? --yes--> END
                                    ^           |
                                    |           no (and rounds left)
                                    └─ debugger ┘
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import strip_code_fences, code_blocks, build_test_program, run_python

OLLAMA_MODEL = "llama3.2"
MAX_FIXES = 3        # safety limit so the loop always stops
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

CODER_PROMPT = """You are a PYTHON CODER. Write ONE Python function that solves the task.
Rules: no input(), no print(), no example usage, no explanation.
Return ONLY the code inside one ```python block."""

TESTER_PROMPT = """You are a TESTER. Write 4 simple `assert` lines that test the function (call it by its name).
Rules: only assert lines, no imports, no explanation, no function definition.
Return ONLY the asserts inside one ```python block."""

DEBUGGER_PROMPT = """You are a DEBUGGER. The code failed its tests. You get the code, the tests and the error.
Either the code OR a test may be wrong (for example a wrong expected value) — decide which and fix it.
Return TWO ```python blocks and nothing else:
1) the full corrected function
2) the full list of assert lines (fix any assert that is itself wrong)"""


# ---------- State ----------
class State(TypedDict):
    task: str
    code: str
    tests: str
    passed: bool
    output: str
    fixes: int


def ask_llm(system: str, user: str) -> str:
    return strip_code_fences(llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content)


# ---------- Agents ----------
def coder_node(state: State):
    print("  👩‍💻 [coder]     writing the function...")
    return {"code": ask_llm(CODER_PROMPT, f"Task: {state['task']}")}


def tester_node(state: State):
    print("  🧪 [tester]    writing asserts...")
    return {"tests": ask_llm(TESTER_PROMPT, f"Task: {state['task']}\n\nCode:\n{state['code']}")}


def run_tests_node(state: State):
    """NOT an LLM: a real Python process runs code + tests. Facts beat opinions."""
    result = run_python(build_test_program(state["code"], state["tests"]))
    passed = result["ok"] and "ALL TESTS PASSED" in result["output"]
    lines = result["output"].splitlines()
    first_problem = lines[1] if lines and lines[0] == "FAILED:" and len(lines) > 1 else (lines[-1] if lines else "no output")
    print(f"  ▶️  [runner]    {'✅ all tests passed' if passed else '❌ ' + first_problem[:150]}")
    return {"passed": passed, "output": result["output"]}


def debugger_node(state: State):
    print(f"  🐞 [debugger]  fixing the code (fix #{state['fixes'] + 1})...")
    msg = f"Code:\n{state['code']}\n\nTests:\n{state['tests']}\n\nError:\n{state['output']}"
    reply = llm.invoke([SystemMessage(content=DEBUGGER_PROMPT), HumanMessage(content=msg)]).content
    blocks = code_blocks(reply)
    code = blocks[0] if blocks else state["code"]
    tests = blocks[1] if len(blocks) > 1 else state["tests"]      # the debugger may fix a wrong test too!
    return {"code": code, "tests": tests, "fixes": state["fixes"] + 1}


def after_tests(state: State) -> str:
    """Conditional edge: done, or loop back to the debugger?"""
    if state["passed"] or state["fixes"] >= MAX_FIXES:
        return "end"
    return "debugger"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("coder", coder_node)
    g.add_node("tester", tester_node)
    g.add_node("run_tests", run_tests_node)
    g.add_node("debugger", debugger_node)

    g.add_edge(START, "coder")
    g.add_edge("coder", "tester")
    g.add_edge("tester", "run_tests")
    g.add_conditional_edges("run_tests", after_tests, {"end": END, "debugger": "debugger"})
    g.add_edge("debugger", "run_tests")      # the loop: fix -> test again
    return g.compile()


def ask(agent, task):
    r = agent.invoke({"task": task, "code": "", "tests": "", "passed": False, "output": "", "fixes": 0})
    status = "✅ PASSED all tests" if r["passed"] else f"⚠️ still failing after {r['fixes']} fixes"
    return f"{status}\n\n--- code ---\n{r['code']}\n\n--- tests ---\n{r['tests']}"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  👩‍💻  Coder-Tester Agent  (write → test → debug loop)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Max fixes: {MAX_FIXES}")
    print("  Try: 'is_palindrome(s) that ignores case' or 'fizzbuzz(n) returning a list'\n")
    agent = build_agent()
    while True:
        try:
            task = input("Coding task: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not task: continue
        if task.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\n" + ask(agent, task) + "\n")


if __name__ == "__main__":
    main()
