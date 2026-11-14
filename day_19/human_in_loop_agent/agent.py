from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.messages import HumanMessage, SystemMessage
from tools import send_email

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.4)

DRAFT_PROMPT = """You are an email assistant. Write a short, polite email (max 80 words)
for the user's request. Return ONLY the email body — no subject line, no extra comments."""


# ---------- State ----------
class State(TypedDict):
    request: str
    to: str
    draft: str
    feedback: str
    result: str


# ---------- Nodes ----------
def draft_node(state: State):
    msg = state["request"]
    if state.get("feedback"):  # second time around: include the human's notes
        msg += f"\n\nPrevious draft:\n{state['draft']}\n\nHuman feedback — please apply it:\n{state['feedback']}"
    reply = llm.invoke([SystemMessage(content=DRAFT_PROMPT), HumanMessage(content=msg)])
    return {"draft": reply.content.strip()}


def human_review_node(state: State):
    # interrupt() PAUSES the graph here and hands this payload to the human.
    # The graph resumes when we call invoke(Command(resume=...)) with their answer.
    decision = interrupt({"to": state["to"], "draft": state["draft"]})
    return {"feedback": decision}  # "approve" or the human's edit instructions


def route_after_review(state: State):
    return "send" if state["feedback"].strip().lower() in ("approve", "a", "yes", "y") else "draft"


def send_node(state: State):
    result = send_email.invoke({"to": state["to"], "subject": "Message from my assistant", "body": state["draft"]})
    return {"result": result}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("draft", draft_node)
    g.add_node("human_review", human_review_node)
    g.add_node("send", send_node)

    g.add_edge(START, "draft")
    g.add_edge("draft", "human_review")
    g.add_conditional_edges("human_review", route_after_review, {"send": "send", "draft": "draft"})
    g.add_edge("send", END)
    # A checkpointer is REQUIRED: it saves the paused state so we can resume later.
    return g.compile(checkpointer=MemorySaver())


def run_once(agent, request, to, thread_id="1"):
    """Drive one email from request to sent — asking the human whenever the graph pauses."""
    config = {"configurable": {"thread_id": thread_id}}
    out = agent.invoke({"request": request, "to": to, "draft": "", "feedback": "", "result": ""}, config)

    while "__interrupt__" in out:  # graph is paused, waiting for a human
        payload = out["__interrupt__"][0].value
        print(f"\n📧 DRAFT for {payload['to']}:\n{'-' * 40}\n{payload['draft']}\n{'-' * 40}")
        answer = input("Type 'approve' to send, or tell me what to change: ").strip() or "approve"
        out = agent.invoke(Command(resume=answer), config)  # resume from the pause

    return out["result"]


def main():
    print("=" * 50)
    print("  🙋  Human-in-the-Loop Agent  (Ollama + LangGraph)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Nothing is sent until YOU approve")
    print("  Try: 'Ask Priya to move tomorrow's meeting to 3pm'\n")
    agent = build_agent()
    n = 0
    while True:
        try:
            request = input("Request: ").strip()
            if not request: continue
            if request.lower() in ("quit", "exit", "q"):
                print("Bye!"); break
            to = input("Send to (email): ").strip() or "friend@example.com"
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        n += 1
        print("\nAgent:", run_once(agent, request, to, thread_id=str(n)), "\n")


if __name__ == "__main__":
    main()
