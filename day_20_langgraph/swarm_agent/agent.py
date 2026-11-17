"""
SWARM (hand-off) multi-agent
----------------------------
There is NO boss. Every agent decides for itself who should take over next
by ending its reply with `HANDOFF: <agent>` (like passing a phone call on).

    START -> triage ──► orders ──► refunds
               │          │           │
               └──────────┴───────────┴──► DONE -> END
"""
import re
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_order_status, issue_refund, parse_handoff

OLLAMA_MODEL = "llama3.2"
MAX_HOPS = 5         # safety limit so agents cannot pass the call around forever
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

HANDOFF_RULE = """
Your reply has TWO parts: first your message to the customer, then ONE last line that is exactly one of:
HANDOFF: orders
HANDOFF: refunds
HANDOFF: DONE"""

TRIAGE_PROMPT = """You are the FRONT DESK of an online shop. Write ONE short friendly sentence to the customer.
If the message mentions an order, delivery, damage or a refund, do NOT ask questions — pass it on with HANDOFF: orders.
If it is only small talk, answer it and use HANDOFF: DONE.

Example reply:
Sorry about that, let me get our orders team.
HANDOFF: orders""" + HANDOFF_RULE

ORDERS_PROMPT = """You are the ORDERS agent. You get the customer's message and the TOOL RESULT for their order.
Tell the customer the status in 1-2 sentences.
If the customer asks for a refund / their money back AND the status is 'delivered' -> HANDOFF: refunds
(you cannot refund yourself — the refunds agent does it). Otherwise -> HANDOFF: DONE.""" + HANDOFF_RULE

REFUNDS_PROMPT = """You are the REFUNDS agent. You get the customer's message and the TOOL RESULT of the refund.
Tell the customer the outcome in 1-2 sentences, using the tool result. Then HANDOFF: DONE.""" + HANDOFF_RULE


# ---------- State ----------
class State(TypedDict):
    request: str
    active: str      # which agent speaks next
    log: list        # replies so far: ["[triage] ...", "[orders] ..."]
    hops: int


# Small models sometimes forget the HANDOFF line. Safety net: what to do when it is missing.
SAFETY_NET = {"triage": "orders"}          # triage's whole job is to pass the customer on
ICONS = {"triage": "🛎️ ", "orders": "📦", "refunds": "💸"}


def order_id_from(text: str) -> str:
    """Find a 4-digit order number such as 5001 in the customer's message."""
    m = re.search(r"\b(\d{4})\b", text)
    return m.group(1) if m else ""


def conversation(state: State) -> str:
    seen = "\n".join(state["log"]) or "(nobody has replied yet)"
    return f"Customer message: {state['request']}\n\nWhat the team already said:\n{seen}"


def finish_turn(state: State, name: str, raw: str):
    """Every agent ends the same way: record the reply and choose who is next."""
    message, target = parse_handoff(raw, default=SAFETY_NET.get(name, "done"))
    message = message or "(no message)"
    if target == name or state["hops"] + 1 >= MAX_HOPS:      # guard rails
        target = "done"
    print(f"  {ICONS[name]} [{name}] {message}")
    print(f"       ↪ hands off to: {target}")
    return {"log": state["log"] + [f"[{name}] {message}"], "active": target, "hops": state["hops"] + 1}


# ---------- Agents ----------
def triage_node(state: State):
    raw = llm.invoke([SystemMessage(content=TRIAGE_PROMPT), HumanMessage(content=conversation(state))]).content
    return finish_turn(state, "triage", raw)


def orders_node(state: State):
    # Tool-first: plain code finds the order number and runs the tool; the LLM explains the result.
    result = get_order_status.invoke({"order_id": order_id_from(state["request"])})
    print(f"       🔧 tool get_order_status -> {result}")
    msg = conversation(state) + f"\n\nTOOL RESULT: {result}"
    raw = llm.invoke([SystemMessage(content=ORDERS_PROMPT), HumanMessage(content=msg)]).content
    return finish_turn(state, "orders", raw)


def refunds_node(state: State):
    result = issue_refund.invoke({"order_id": order_id_from(state["request"])})
    print(f"       🔧 tool issue_refund -> {result}")
    msg = conversation(state) + f"\n\nTOOL RESULT: {result}"
    raw = llm.invoke([SystemMessage(content=REFUNDS_PROMPT), HumanMessage(content=msg)]).content
    return finish_turn(state, "refunds", raw)


def next_agent(state: State) -> str:
    """Conditional edge: read the agent's own HANDOFF decision."""
    return state["active"] if state["active"] in ("triage", "orders", "refunds") else "done"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("triage", triage_node)
    g.add_node("orders", orders_node)
    g.add_node("refunds", refunds_node)

    g.add_edge(START, "triage")
    routes = {"triage": "triage", "orders": "orders", "refunds": "refunds", "done": END}
    for name in ("triage", "orders", "refunds"):       # EVERY agent can hand off to any other
        g.add_conditional_edges(name, next_agent, routes)
    return g.compile()


def ask(agent, request):
    r = agent.invoke({"request": request, "active": "triage", "log": [], "hops": 0})
    return "\n".join(r["log"])


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🐝  Swarm Agent  (agents hand the customer to each other)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Agents: triage, orders, refunds")
    print("  Orders you can use: 5001 (delivered), 5002 (shipped), 5003 (already refunded)")
    print("  Try: 'Order 5001 arrived broken, I want my money back'\n")
    agent = build_agent()
    while True:
        try:
            request = input("Customer: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not request: continue
        if request.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        ask(agent, request)
        print()


if __name__ == "__main__":
    main()
