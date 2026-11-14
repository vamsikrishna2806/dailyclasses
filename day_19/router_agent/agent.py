from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import lookup_invoice, search_kb

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

ROUTER_PROMPT = """You are a router for a customer-support team.
Read the customer message and answer with EXACTLY ONE word:
  billing  -> invoices, payments, refunds, charges
  tech     -> bugs, crashes, wifi, passwords, how-to problems
  general  -> anything else (hours, greetings, feedback)

Examples:
  "Is invoice 1002 paid?"          -> billing
  "I was charged twice"            -> billing
  "The app crashes on startup"     -> tech
  "I forgot my password"           -> tech
  "What time do you open?"         -> general
  "Hello!"                         -> general

Answer with just the one word."""

BILLING_PROMPT = "You are a friendly billing specialist. Use lookup_invoice when an invoice number is given."
TECH_PROMPT = "You are a patient tech-support engineer. Use search_kb to find fixes, then explain step by step."
GENERAL_PROMPT = "You are a polite front-desk assistant. Keep answers short and helpful."

# Each specialist is its own small agent with its own tools.
billing_agent = create_react_agent(llm, [lookup_invoice])
tech_agent = create_react_agent(llm, [search_kb])


# ---------- State: what flows through the graph ----------
class State(TypedDict):
    question: str
    route: str
    answer: str


# ---------- Nodes ----------
def router_node(state: State):
    reply = llm.invoke([SystemMessage(content=ROUTER_PROMPT), HumanMessage(content=state["question"])])
    word = reply.content.strip().lower()
    route = next((r for r in ("billing", "tech") if r in word), "general")  # safe fallback
    print(f"  [router] -> {route}")
    return {"route": route}


def billing_node(state: State):
    result = billing_agent.invoke({"messages": [SystemMessage(content=BILLING_PROMPT), HumanMessage(content=state["question"])]})
    return {"answer": result["messages"][-1].content}


def tech_node(state: State):
    result = tech_agent.invoke({"messages": [SystemMessage(content=TECH_PROMPT), HumanMessage(content=state["question"])]})
    return {"answer": result["messages"][-1].content}


def general_node(state: State):
    reply = llm.invoke([SystemMessage(content=GENERAL_PROMPT), HumanMessage(content=state["question"])])
    return {"answer": reply.content}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("router", router_node)
    g.add_node("billing", billing_node)
    g.add_node("tech", tech_node)
    g.add_node("general", general_node)

    g.add_edge(START, "router")
    # The "if/else" of agents: pick the next node from state["route"]
    g.add_conditional_edges("router", lambda s: s["route"],
                            {"billing": "billing", "tech": "tech", "general": "general"})
    for name in ("billing", "tech", "general"):
        g.add_edge(name, END)
    return g.compile()


def ask(agent, user_input):
    return agent.invoke({"question": user_input})["answer"]


def main():
    print("=" * 50)
    print("  🚦  Router Agent  (Ollama + LangGraph)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Routes: billing / tech / general")
    print("  Try: 'Is invoice 1002 paid?' or 'My wifi keeps dropping' or 'What are your hours?'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
