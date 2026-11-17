"""
PLAN-AND-EXECUTE multi-agent
----------------------------
1. PLANNER  thinks FIRST and writes a numbered plan (no tools).
2. EXECUTOR does the plan ONE STEP AT A TIME: the LLM picks the tool call,
   the TOOL (calculator) does the real arithmetic.
3. ANSWERER  turns the collected results into the final answer.

    START -> planner -> executor -> (more steps?) --yes--> executor ...
                                          |
                                          no
                                          v
                                       answerer -> END
"""
import re
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import calculator, parse_plan

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

PLANNER_PROMPT = """You are a PLANNER. Break the task into the FEWEST short numbered steps (1 to 4).
Each step is ONE calculation. The LAST step gives the final answer.
Rules: use ONLY the numbers in the task, never invent extra steps (no tax, tips or fees), never write results.
Return ONLY the numbered lines. Examples:

Task: 2 shirts at $15 and 1 hat at $10. Total?
1. Multiply 2 shirts by $15
2. Multiply 1 hat by $10
3. Add the two results

Task: A $40 coat is 25% off. What do I pay?
1. Multiply $40 by 0.75

Task: A bike costs $200 and a helmet $30, then 10% off the total. What do I pay?
1. Add $200 and $30
2. Multiply the result by 0.9"""

EXECUTOR_PROMPT = """You are an EXECUTOR. You get ONE step and the results of earlier steps.
Reply with exactly ONE line, the math expression for the calculator tool:
CALC: <expression with plain numbers>
Write earlier results into the expression as numbers. Never calculate yourself.
Example: step 'Add the two results', earlier results 30 and 10  ->  CALC: 30 + 10
Example: step 'Multiply 2 shirts by $15'  ->  CALC: 2 * 15"""

ANSWERER_PROMPT = """You are an ANSWERER. Using the original task and the step results, give the final answer
in ONE clear sentence. Use the numbers from the results — do not recalculate."""

# ---------- State ----------
class State(TypedDict):
    task: str
    plan: list       # ["Multiply...", "Add..."]
    results: list    # result line for each finished step
    answer: str


# ---------- Agents ----------
def planner_node(state: State):
    reply = llm.invoke([SystemMessage(content=PLANNER_PROMPT), HumanMessage(content=state["task"])]).content
    plan = parse_plan(reply)
    print("  🧠 [planner] plan:")
    for i, s in enumerate(plan, 1):
        print(f"       {i}. {s}")
    return {"plan": plan, "results": []}


def run_tool(reply: str) -> str:
    """Read the executor's one-line instruction and run the REAL calculator tool. The tool does the maths, not the LLM."""
    m = re.search(r"CALC:\s*(.+)", reply, re.I)
    return calculator.invoke({"expression": (m.group(1) if m else reply).strip()})


def executor_node(state: State):
    i = len(state["results"])                      # which step are we on?
    step = state["plan"][i]
    done = "\n".join(f"Step {n + 1} result: {r}" for n, r in enumerate(state["results"])) or "(none yet)"
    msg = f"Task: {state['task']}\n\nEarlier results:\n{done}\n\nYOUR STEP ({i + 1}/{len(state['plan'])}): {step}"
    instruction = llm.invoke([SystemMessage(content=EXECUTOR_PROMPT), HumanMessage(content=msg)]).content.strip().splitlines()[0]
    result = run_tool(instruction)
    print(f"  🔧 [executor] step {i + 1}: {instruction}   =>  {result}")
    return {"results": state["results"] + [result]}


def answerer_node(state: State):
    steps = "\n".join(f"{n + 1}. {s} -> {r}" for n, (s, r) in enumerate(zip(state["plan"], state["results"])))
    msg = f"Task: {state['task']}\n\nSteps and results:\n{steps}"
    return {"answer": llm.invoke([SystemMessage(content=ANSWERER_PROMPT), HumanMessage(content=msg)]).content.strip()}


def more_steps(state: State) -> str:
    """Conditional edge: is there still a plan step without a result?"""
    return "executor" if len(state["results"]) < len(state["plan"]) else "answerer"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("planner", planner_node)
    g.add_node("executor", executor_node)
    g.add_node("answerer", answerer_node)

    g.add_edge(START, "planner")
    g.add_edge("planner", "executor")
    g.add_conditional_edges("executor", more_steps, {"executor": "executor", "answerer": "answerer"})  # loop
    g.add_edge("answerer", END)
    return g.compile()


def ask(agent, task):
    return agent.invoke({"task": task, "plan": [], "results": [], "answer": ""})["answer"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🗺️  Planner-Executor Agent  (plan first, then do)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: calculator")
    print("  Try: 'I buy 3 pens at $2 and 4 notebooks at $5. How much in total?'\n")
    agent = build_agent()
    while True:
        try:
            task = input("Task: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not task: continue
        if task.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\nAnswer:", ask(agent, task), "\n")


if __name__ == "__main__":
    main()
