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
for the user's request. Start with "Dear <recipient name>," and end with
"Best regards," followed by the sender's name. Use the real names you are given and
NEVER leave placeholders like [Recipient] or [Your Name].
Return ONLY the email body — no subject line, no extra comments."""


# ---------- State ----------
class State(TypedDict):
    request: str
    to: str
    to_name: str
    sender: str
    draft: str
    feedback: str
    result: str


# ---------- Nodes ----------
def draft_node(state: State):
    msg = f"Recipient name: {state['to_name']}\nSender name: {state['sender']}\nRequest: {state['request']}"
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


# ---------- Console helpers (keep input friendly for students) ----------
def ask_until_valid(prompt, is_ok, hint):
    """Keep asking until the answer passes is_ok, so bad input never derails the demo."""
    while True:
        value = input(prompt).strip()
        if is_ok(value):
            return value
        print(f"   ⚠️  {hint}")


def looks_like_email(text):
    local, _, domain = text.partition("@")
    return bool(local) and "." in domain and " " not in text


def run_once(agent, request, to, to_name, sender, thread_id="1"):
    """Drive one email from request to sent — asking the human whenever the graph pauses."""
    config = {"configurable": {"thread_id": thread_id}}
    out = agent.invoke({"request": request, "to": to, "to_name": to_name, "sender": sender,
                        "draft": "", "feedback": "", "result": ""}, config)

    while "__interrupt__" in out:  # graph is paused, waiting for a human
        payload = out["__interrupt__"][0].value
        print(f"\n📧 DRAFT  (to: {to_name} <{payload['to']}>)")
        print("-" * 40)
        print(payload["draft"])
        print("-" * 40)
        # An empty Enter must NOT send — only an explicit answer counts.
        answer = ask_until_valid(
            "👉 Type  approve  to SEND, or type what to change (e.g. 'make it shorter'): ",
            lambda v: v != "", "Please type 'approve' or a change request.")
        out = agent.invoke(Command(resume=answer), config)  # resume from the pause

    return out["result"]


def main():
    print("=" * 50)
    print("  🙋  Human-in-the-Loop Agent  (Ollama + LangGraph)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Nothing is sent until YOU approve\n")
    agent = build_agent()
    sender = ask_until_valid("1) Your name (used to sign the email), e.g. Vamsi: ",
                             lambda v: v != "" and v.lower() not in ("approve", "quit", "q"),
                             "Please type your real name.")
    n = 0
    while True:
        try:
            print("\n--- New email (type q to quit) ---")
            request = ask_until_valid("2) What should the email say? e.g. 'Ask Priya to move tomorrow's meeting to 3pm': ",
                                      lambda v: len(v.split()) >= 3 or v.lower() in ("q", "quit", "exit"),
                                      "Describe the email in a few words, or type q to quit.")
            if request.lower() in ("quit", "exit", "q"):
                print("Bye!"); break
            to = ask_until_valid("3) Recipient's email address: ", looks_like_email,
                                 "That doesn't look like an email (need name@domain.com). Try again.")
            to_name = ask_until_valid("4) Recipient's name, e.g. Priya: ", lambda v: v != "", "Please type a name.")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        n += 1
        print("\n✅", run_once(agent, request, to, to_name, sender, thread_id=str(n)))


if __name__ == "__main__":
    main()
