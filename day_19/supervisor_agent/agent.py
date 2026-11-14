from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import wiki_summary

OLLAMA_MODEL = "llama3.2"
MAX_STEPS = 6  # safety limit on supervisor decisions

llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

SUPERVISOR_PROMPT = """You are a supervisor managing a team of workers:
  researcher -> finds facts (Wikipedia)
  writer     -> turns the facts into a short article
  proofreader-> fixes grammar and polishes the article
Look at the progress so far and decide who works NEXT.
Typical order: researcher, then writer, then proofreader, then FINISH.
Answer with EXACTLY ONE word: researcher, writer, proofreader, or FINISH."""

RESEARCHER_PROMPT = "You are a researcher. Use wiki_summary to get facts about the topic. Report the key facts as bullet points."
WRITER_PROMPT = "You are a writer. Using the research notes, write a clear 80-word article. Return only the article."
PROOFREADER_PROMPT = "You are a proofreader. Fix grammar and polish this article without changing its meaning. Return only the final article."

researcher_agent = create_react_agent(llm, [wiki_summary])  # a worker WITH a tool


# ---------- State ----------
class State(TypedDict):
    task: str
    notes: str       # researcher output
    article: str     # writer / proofreader output
    next: str        # supervisor's decision
    steps: int


def progress(state: State) -> str:
    return (f"Task: {state['task']}\n"
            f"Research notes done: {'yes' if state['notes'] else 'no'}\n"
            f"Article written: {'yes' if state['article'] else 'no'}")


# ---------- Supervisor ----------
def supervisor_node(state: State):
    reply = llm.invoke([SystemMessage(content=SUPERVISOR_PROMPT), HumanMessage(content=progress(state))])
    word = reply.content.strip().lower()
    choice = next((w for w in ("researcher", "writer", "proofreader") if w in word), "FINISH")
    # Guard rails: small models sometimes pick a wrong step, so enforce the order.
    if not state["notes"]:
        choice = "researcher"
    elif not state["article"]:
        choice = "writer"
    elif "proofread ✔" in state["article"]:
        choice = "FINISH"
    else:
        choice = "proofreader"
    if state["steps"] >= MAX_STEPS:
        choice = "FINISH"
    print(f"  🧑‍💼 [supervisor] -> {choice}")
    return {"next": choice, "steps": state["steps"] + 1}


# ---------- Workers ----------
def researcher_node(state: State):
    result = researcher_agent.invoke({"messages": [SystemMessage(content=RESEARCHER_PROMPT), HumanMessage(content=state["task"])]})
    return {"notes": result["messages"][-1].content}


def writer_node(state: State):
    msg = f"Topic: {state['task']}\n\nResearch notes:\n{state['notes']}"
    reply = llm.invoke([SystemMessage(content=WRITER_PROMPT), HumanMessage(content=msg)])
    return {"article": reply.content}


def proofreader_node(state: State):
    reply = llm.invoke([SystemMessage(content=PROOFREADER_PROMPT), HumanMessage(content=state["article"])])
    return {"article": reply.content + "\n\n(proofread ✔)"}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("supervisor", supervisor_node)
    g.add_node("researcher", researcher_node)
    g.add_node("writer", writer_node)
    g.add_node("proofreader", proofreader_node)

    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", lambda s: s["next"],
                            {"researcher": "researcher", "writer": "writer",
                             "proofreader": "proofreader", "FINISH": END})
    # Every worker reports BACK to the supervisor (that's the hub-and-spoke shape).
    for worker in ("researcher", "writer", "proofreader"):
        g.add_edge(worker, "supervisor")
    return g.compile()


def ask(agent, user_input):
    result = agent.invoke({"task": user_input, "notes": "", "article": "", "next": "", "steps": 0})
    return result["article"]


def main():
    print("=" * 50)
    print("  🧑‍💼  Supervisor Agent  (Ollama + Wikipedia)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Workers: researcher, writer, proofreader")
    print("  Try: 'Black holes' or 'The Eiffel Tower'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("Topic: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print("\nArticle:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
