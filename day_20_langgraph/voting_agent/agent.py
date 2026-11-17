"""
VOTING PANEL multi-agent  (ensemble / majority vote)
----------------------------------------------------
Ask three jurors with DIFFERENT personalities the SAME question, at the same time.
Count the votes in plain Python. Only if the panel cannot agree, a judge breaks the tie.
One AI can be wrong; a panel is wrong less often.

                ┌─► strict   ─┐
    START ──────┼─► friendly ─┼──► tally ──┬─ clear majority ─► END
                └─► evidence ─┘            └─ no majority ────► judge ─► END
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import spam_signals, parse_vote, parse_reply, tally

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

# Reason FIRST, vote second: small models vote more consistently after they have said why.
VOTE_FORMAT = "\nReply in exactly two lines:\nReason: <under 12 words>\nVote: SPAM or NOT_SPAM or UNSURE"

STRICT_PROMPT = ("You are a STRICT security guard. You distrust everything: if a message pushes you to click, pay, "
                 "reply with details or hurry, vote SPAM. Decide if the message is spam." + VOTE_FORMAT)
FRIENDLY_PROMPT = ("You are a FRIENDLY, trusting person. You give people the benefit of the doubt: normal chat, "
                   "reminders, receipts and newsletters from known senders are NOT_SPAM. But obvious scams "
                   "(prizes, free gift cards, 'claim now', strange links) are still SPAM. Decide if the message is spam." + VOTE_FORMAT)
EVIDENCE_PROMPT = ("You are a DATA ANALYST. You get a message AND counted warning signs. Follow this rule strictly: "
                   "score 4 or more -> SPAM; score 0 or 1 -> NOT_SPAM; score 2 or 3 -> UNSURE. "
                   "Quote the score in your reason." + VOTE_FORMAT)
JUDGE_PROMPT = """You are the TIE-BREAKER JUDGE. The panel disagreed. Read the message and their reasons and give
the final call. Reply in exactly two lines:
Reason: <one short sentence>
Vote: SPAM or NOT_SPAM"""


# ---------- State: each juror writes to its OWN key (they run in parallel) ----------
class State(TypedDict):
    message: str
    strict: str
    friendly: str
    evidence: str
    counts: str
    verdict: str
    decided_by: str


def juror(system: str, user: str) -> str:
    reply = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content
    return parse_reply(reply)          # -> "SPAM - short reason"


# ---------- Jurors (run at the same time) ----------
def strict_node(state: State):
    return {"strict": juror(STRICT_PROMPT, f"Message: {state['message']}")}


def friendly_node(state: State):
    return {"friendly": juror(FRIENDLY_PROMPT, f"Message: {state['message']}")}


def evidence_node(state: State):
    signals = spam_signals(state["message"])           # a TOOL gives this juror hard facts
    return {"evidence": juror(EVIDENCE_PROMPT, f"Message: {state['message']}\n\nWarning signs: {signals}")}


# ---------- Counting (plain Python) ----------
def tally_node(state: State):
    votes = [parse_vote(state[k]) for k in ("strict", "friendly", "evidence")]
    winner, counts = tally(votes)
    print(f"  🗳️  [strict]   {state['strict']}")
    print(f"  🗳️  [friendly] {state['friendly']}")
    print(f"  🗳️  [evidence] {state['evidence']}")
    print(f"  🧮 [tally]    votes = {dict(counts)}  ->  {winner or 'NO MAJORITY'}")
    if winner:
        return {"counts": str(dict(counts)), "verdict": winner, "decided_by": "majority vote"}
    return {"counts": str(dict(counts)), "verdict": "", "decided_by": ""}


def judge_node(state: State):
    print("  ⚖️  [judge]    panel is split — breaking the tie")
    reasons = f"strict: {state['strict']}\nfriendly: {state['friendly']}\nevidence: {state['evidence']}"
    reply = juror(JUDGE_PROMPT, f"Message: {state['message']}\n\nPanel:\n{reasons}")
    return {"verdict": parse_vote(reply) if parse_vote(reply) != "UNSURE" else "SPAM", "decided_by": "judge (tie-break)"}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("strict", strict_node)
    g.add_node("friendly", friendly_node)
    g.add_node("evidence", evidence_node)
    g.add_node("tally", tally_node)
    g.add_node("judge", judge_node)

    for juror_name in ("strict", "friendly", "evidence"):      # fan-out
        g.add_edge(START, juror_name)
    g.add_edge(["strict", "friendly", "evidence"], "tally")    # fan-in
    g.add_conditional_edges("tally", lambda s: "done" if s["verdict"] else "judge", {"done": END, "judge": "judge"})
    g.add_edge("judge", END)
    return g.compile()


def ask(agent, message):
    r = agent.invoke({"message": message, "strict": "", "friendly": "", "evidence": "",
                      "counts": "", "verdict": "", "decided_by": ""})
    icon = "🚫" if r["verdict"] == "SPAM" else "✅"
    return f"{icon} FINAL: {r['verdict']}   (decided by {r['decided_by']})"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🗳️  Voting Panel Agent  (3 jurors → majority → judge if tied)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}")
    print("  Try: 'URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1'")
    print("  Try: 'Hi Sam, are we still meeting for lunch at 1pm tomorrow?'\n")
    agent = build_agent()
    while True:
        try:
            message = input("Message to check: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not message: continue
        if message.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\n" + ask(agent, message) + "\n")


if __name__ == "__main__":
    main()
