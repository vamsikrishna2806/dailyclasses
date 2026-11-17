"""
RAG TEAM multi-agent  (retrieve -> answer -> fact-check)
--------------------------------------------------------
Four roles make an answer you can TRUST:
  rewriter   turns a chatty question into search keywords
  retriever  finds handbook passages (plain code, no AI)
  answerer   answers ONLY from those passages and cites them like [HR-1]
  checker    is every claim really in the passages? if not, send it back

    START -> rewriter -> retriever -> found anything? --no--> no_answer -> END
                                          |yes
                                          v
                            answerer -> checker -> grounded? --yes--> END
                                ^                      |
                                └──── (feedback) ──────┘ no, and rounds left
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import search_docs, format_context, keywords

OLLAMA_MODEL = "llama3.2"
MAX_ROUNDS = 2        # how many times the checker may send the answer back
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

REWRITER_PROMPT = """You are a SEARCH QUERY WRITER. Turn the user's question into 3-5 keywords for a document search.
Return ONLY the keywords separated by spaces."""

ANSWERER_PROMPT = """You are a HANDBOOK ASSISTANT. Answer the question using ONLY the CONTEXT passages.
Be short (max 2 sentences) and end with the source ids in brackets, like [HR-1].
If the context does not contain the answer, reply exactly: I could not find that in the handbook."""

CHECKER_PROMPT = """You are a FACT CHECKER. Check ONLY the statements made in the ANSWER (ignore other passages).
Look for every fact and number of the ANSWER in the CONTEXT.
- If every fact in the answer appears in the CONTEXT, reply with the single word: GROUNDED
- If the answer says something the CONTEXT does not say, reply: UNSUPPORTED: <the exact claim that is missing>"""


# ---------- State ----------
class State(TypedDict):
    question: str
    search_query: str
    docs: list
    answer: str
    verdict: str
    rounds: int


def say(system: str, user: str) -> str:
    return llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content.strip()


# ---------- Agents ----------
def rewriter_node(state: State):
    query = say(REWRITER_PROMPT, state["question"])
    print(f"  🔍 [rewriter]   search keywords: {query}")
    return {"search_query": query}


def retriever_node(state: State):
    """Plain code (NO LLM). Search with the rewritten query AND the original words."""
    docs = search_docs(state["search_query"] + " " + " ".join(keywords(state["question"])))
    print(f"  📚 [retriever]  found: {[d['id'] for d in docs] or 'nothing'}")
    return {"docs": docs}


def no_answer_node(state: State):
    return {"answer": "I could not find that in the handbook.", "verdict": "NO SOURCES"}


def answerer_node(state: State):
    msg = f"CONTEXT:\n{format_context(state['docs'])}\n\nQUESTION: {state['question']}"
    if state["verdict"].startswith("UNSUPPORTED"):
        msg += f"\n\nYour previous answer was rejected: {state['verdict']}\nFix it using only the context."
    answer = say(ANSWERER_PROMPT, msg)
    print(f"  💬 [answerer]   {answer}")
    return {"answer": answer}


def checker_node(state: State):
    if state["answer"].lower().startswith("i could not find"):
        # An honest "I don't know" makes no claims, so there is nothing to fact-check.
        print("  🕵️  [checker]    nothing to check (the answerer admitted it does not know)")
        return {"verdict": "GROUNDED", "rounds": state["rounds"] + 1}
    msg = f"CONTEXT:\n{format_context(state['docs'])}\n\nANSWER: {state['answer']}"
    verdict = say(CHECKER_PROMPT, msg).splitlines()[0]
    if not verdict.upper().startswith("UNSUPPORTED"):
        verdict = "GROUNDED"
    else:
        # Verify the verifier! A small model sometimes flags a "missing" claim that is literally in the passages.
        # Plain Python can settle that: if the flagged text appears in the context, the checker was wrong.
        claim = verdict.split(":", 1)[1].strip(" \"'.") if ":" in verdict else ""
        if len(claim) < 4 or claim.lower() in format_context(state["docs"]).lower():
            verdict = "GROUNDED"
    print(f"  🕵️  [checker]    {verdict}")
    return {"verdict": verdict, "rounds": state["rounds"] + 1}


def after_retrieval(state: State) -> str:
    return "answerer" if state["docs"] else "no_answer"


def after_check(state: State) -> str:
    if state["verdict"] == "GROUNDED" or state["rounds"] > MAX_ROUNDS:
        return "end"
    return "answerer"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("rewriter", rewriter_node)
    g.add_node("retriever", retriever_node)
    g.add_node("no_answer", no_answer_node)
    g.add_node("answerer", answerer_node)
    g.add_node("checker", checker_node)

    g.add_edge(START, "rewriter")
    g.add_edge("rewriter", "retriever")
    g.add_conditional_edges("retriever", after_retrieval, {"answerer": "answerer", "no_answer": "no_answer"})
    g.add_edge("no_answer", END)
    g.add_edge("answerer", "checker")
    g.add_conditional_edges("checker", after_check, {"end": END, "answerer": "answerer"})   # the loop
    return g.compile()


def ask(agent, question):
    r = agent.invoke({"question": question, "search_query": "", "docs": [], "answer": "", "verdict": "", "rounds": 0})
    badge = {"GROUNDED": "✅ checked against the handbook"}.get(r["verdict"], f"⚠️ {r['verdict']}")
    return f"{r['answer']}\n   ({badge})"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  📚  RAG Team Agent  (retrieve → answer → fact-check)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Knowledge: a tiny company handbook (see tools.py)")
    print("  Try: 'How many vacation days do I get?' or 'Can I work from home?'")
    print("  Try something NOT in the handbook: 'What is the CEO's salary?'\n")
    agent = build_agent()
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not question: continue
        if question.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\nAnswer:", ask(agent, question), "\n")


if __name__ == "__main__":
    main()
