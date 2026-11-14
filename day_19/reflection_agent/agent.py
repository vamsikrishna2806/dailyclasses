from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import count_words

OLLAMA_MODEL = "llama3.2"
MAX_ROUNDS = 3  # safety limit so the loop always stops

llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.5)

WRITER_PROMPT = """You are a skilled writer. Write a short, clear piece (max 100 words)
for the user's request. Return ONLY the text itself."""

CRITIC_PROMPT = """You are a strict but fair editor. Review the draft against the request.
Check: clarity, tone, grammar, and whether it fully answers the request.
- If it is good enough, reply with exactly: APPROVED
- Otherwise reply with 2-3 short, specific suggestions for improvement."""

REVISER_PROMPT = """You are a writer revising your draft.
Rewrite it applying the editor's feedback. Return ONLY the improved text."""


# ---------- State ----------
class State(TypedDict):
    request: str
    draft: str
    feedback: str
    rounds: int


# ---------- Nodes ----------
def write_node(state: State):
    reply = llm.invoke([SystemMessage(content=WRITER_PROMPT), HumanMessage(content=state["request"])])
    print(f"\n  ✍️  [writer] first draft ({count_words.invoke(reply.content)})")
    return {"draft": reply.content, "rounds": 0}


def critique_node(state: State):
    msg = f"Request: {state['request']}\n\nDraft:\n{state['draft']}"
    reply = llm.invoke([SystemMessage(content=CRITIC_PROMPT), HumanMessage(content=msg)])
    print(f"  🧐 [critic] {reply.content.strip()[:200]}")
    return {"feedback": reply.content}


def revise_node(state: State):
    msg = f"Request: {state['request']}\n\nDraft:\n{state['draft']}\n\nEditor feedback:\n{state['feedback']}"
    reply = llm.invoke([SystemMessage(content=REVISER_PROMPT), HumanMessage(content=msg)])
    rounds = state["rounds"] + 1
    print(f"  🔁 [reviser] revision #{rounds} ({count_words.invoke(reply.content)})")
    return {"draft": reply.content, "rounds": rounds}


# ---------- Loop decision ----------
def should_continue(state: State):
    if "APPROVED" in state["feedback"].upper():
        return "done"
    if state["rounds"] >= MAX_ROUNDS:
        return "done"
    return "revise"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("write", write_node)
    g.add_node("critique", critique_node)
    g.add_node("revise", revise_node)

    g.add_edge(START, "write")
    g.add_edge("write", "critique")
    g.add_conditional_edges("critique", should_continue, {"revise": "revise", "done": END})
    g.add_edge("revise", "critique")  # <-- the loop: revise, then critique again
    return g.compile()


def ask(agent, user_input):
    return agent.invoke({"request": user_input})["draft"]


def main():
    print("=" * 50)
    print("  🪞  Reflection Agent  (Ollama + LangGraph)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Loop: write → critique → revise (max {MAX_ROUNDS})")
    print("  Try: 'Write a short email asking my boss for Friday off'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print("\nFinal:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
