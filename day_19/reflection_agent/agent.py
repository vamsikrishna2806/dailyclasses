from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import count_words

OLLAMA_MODEL = "llama3.2"
MAX_ROUNDS = 3      # safety limit so the loop always stops
MAX_WORDS = 100     # the writer, critic AND reviser all enforce this

llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.5)

WRITER_PROMPT = f"""You are a skilled writer. Write a short, clear piece (max {MAX_WORDS} words)
for the user's request. Return ONLY the text itself — no title, no intro like "Here is...". """

CRITIC_PROMPT = f"""You are a strict but fair editor. Review the draft against the request.
Check: clarity, tone, grammar, and whether it fully answers the request.
HARD RULE: the draft must be {MAX_WORDS} words or fewer. If it is longer, it is NOT approved —
tell the writer to cut it.
- If it is good enough AND within the limit, reply with exactly: APPROVED
- Otherwise reply with 2-3 short, specific suggestions (one line each)."""

REVISER_PROMPT = f"""You are a writer revising your draft.
Rewrite it applying the editor's feedback, but keep it to {MAX_WORDS} words or fewer
(cut words if needed — never make it longer).
Return ONLY the improved text. Do NOT start with "Here is the revised text" or any intro."""


# ---------- State ----------
class State(TypedDict):
    request: str
    draft: str
    feedback: str
    rounds: int


def clean(text: str) -> str:
    """Small models love to add 'Here is the revised text:' — drop that intro line."""
    lines = text.strip().splitlines()
    if lines and lines[0].lower().startswith("here") and lines[0].rstrip().endswith(":"):
        lines = lines[1:]
    return "\n".join(lines).strip()


def is_approved(feedback: str) -> bool:
    """Approved only if the reply STARTS with APPROVED (not suggestions that end with the word)."""
    return feedback.strip().upper().startswith("APPROVED")


# ---------- Nodes ----------
def write_node(state: State):
    reply = llm.invoke([SystemMessage(content=WRITER_PROMPT), HumanMessage(content=state["request"])])
    draft = clean(reply.content)
    print(f"\n  ✍️  [writer] first draft ({count_words.invoke(draft)})")
    return {"draft": draft, "rounds": 0}


def critique_node(state: State):
    n = len(state["draft"].split())
    msg = f"Request: {state['request']}\n\nWord count: {n} (limit {MAX_WORDS})\n\nDraft:\n{state['draft']}"
    reply = llm.invoke([SystemMessage(content=CRITIC_PROMPT), HumanMessage(content=msg)])
    feedback = reply.content.strip()
    if n > MAX_WORDS and is_approved(feedback):
        # Guard rail: a small model may approve anyway, but code enforces the rule.
        feedback = f"Too long ({n} words). Cut it to {MAX_WORDS} words or fewer."
    print("  🧐 [critic]")
    for line in feedback.splitlines():
        if line.strip():
            print(f"       {line.strip()}")
    return {"feedback": feedback}


def revise_node(state: State):
    msg = f"Request: {state['request']}\n\nDraft:\n{state['draft']}\n\nEditor feedback:\n{state['feedback']}"
    reply = llm.invoke([SystemMessage(content=REVISER_PROMPT), HumanMessage(content=msg)])
    draft = clean(reply.content)
    rounds = state["rounds"] + 1
    print(f"  🔁 [reviser] revision #{rounds} ({count_words.invoke(draft)})")
    return {"draft": draft, "rounds": rounds}


# ---------- Loop decision ----------
def should_continue(state: State):
    if is_approved(state["feedback"]):
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
    print(f"  Model: {OLLAMA_MODEL}  |  Loop: write → critique → revise (max {MAX_ROUNDS}, {MAX_WORDS} words)")
    print("  Tell me WHAT to write, e.g. 'Write a short email asking my boss for Friday off'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("What should I write? (q to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        if len(user_input.split()) < 4:  # 'good', 'pls proceed' are not writing requests
            print("   ⚠️  Describe what to write in a few words, e.g. 'Write a poem about rain'.\n")
            continue
        print("\nFinal:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
