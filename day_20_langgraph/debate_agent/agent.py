"""
DEBATE multi-agent
------------------
Two agents with OPPOSITE jobs argue in turns. A neutral judge reads the
whole transcript and picks a winner. Arguing makes both sides stronger.

    START -> pro -> con -> (more rounds?) --yes--> pro ...
                              |
                              no
                              v
                            judge -> END
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import trim_words, format_transcript, parse_winner

OLLAMA_MODEL = "llama3.2"
ROUNDS = 2          # how many times each side speaks
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.7)

PRO_PROMPT = """You are the PRO debater. You ARGUE FOR the motion — never switch sides.
Speak in max 50 words. If the opponent already spoke, answer their last point first.
Return ONLY your speech."""

CON_PROMPT = """You are the CON debater. You ARGUE AGAINST the motion — never switch sides.
Speak in max 50 words. Answer the opponent's last point first.
Return ONLY your speech."""

JUDGE_PROMPT = """You are a neutral JUDGE. Read the debate. Decide who argued better
(clear reasons, answered the opponent). Reply in EXACTLY this format:
Winner: PRO   (or)   Winner: CON
Reason: <one short sentence>"""


# ---------- State ----------
class State(TypedDict):
    motion: str
    speeches: list    # every speech so far, e.g. "PRO: ..."
    round: int
    verdict: str
    winner: str


def speak(system: str, state: State, label: str) -> str:
    # Small models forget which side they are on, so we REMIND them every turn.
    stance = "AGREE with" if label == "PRO" else "DISAGREE with"
    msg = (f"Motion: \"{state['motion']}\"\nYour side: {label}. You must {stance} this motion.\n\n"
           f"Debate so far:\n{format_transcript(state['speeches'])}\n\n"
           f"Your turn. Say 'my opponent' instead of PRO/CON. Max 50 words:")
    speech = llm.invoke([SystemMessage(content=system), HumanMessage(content=msg)]).content.strip().strip('"')
    return f"{label}: " + trim_words(speech, 60)


# ---------- Agents ----------
def pro_node(state: State):
    speech = speak(PRO_PROMPT, state, "PRO")
    print(f"\n  🟢 {speech}")
    return {"speeches": state["speeches"] + [speech]}


def con_node(state: State):
    speech = speak(CON_PROMPT, state, "CON")
    print(f"\n  🔴 {speech}")
    return {"speeches": state["speeches"] + [speech], "round": state["round"] + 1}


def judge_node(state: State):
    print("\n  ⚖️  [judge] reading the whole debate...")
    msg = f"Motion: {state['motion']}\n\nDebate:\n{format_transcript(state['speeches'])}"
    verdict = llm.invoke([SystemMessage(content=JUDGE_PROMPT), HumanMessage(content=msg)]).content
    return {"verdict": verdict.strip(), "winner": parse_winner(verdict)}


def more_rounds(state: State) -> str:
    """Conditional edge: keep debating, or call the judge?"""
    return "pro" if state["round"] < ROUNDS else "judge"


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("pro", pro_node)
    g.add_node("con", con_node)
    g.add_node("judge", judge_node)

    g.add_edge(START, "pro")
    g.add_edge("pro", "con")
    g.add_conditional_edges("con", more_rounds, {"pro": "pro", "judge": "judge"})  # the loop
    g.add_edge("judge", END)
    return g.compile()


def ask(agent, motion):
    r = agent.invoke({"motion": motion, "speeches": [], "round": 0, "verdict": "", "winner": ""})
    return r["verdict"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🥊  Debate Agent  (PRO vs CON, then a judge)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Rounds: {ROUNDS}")
    print("  Try: 'Homework should be banned' or 'Cats are better than dogs'\n")
    agent = build_agent()
    while True:
        try:
            motion = input("Motion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not motion: continue
        if motion.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print("\n  --- the debate begins ---")
        print("\n⚖️  Verdict:\n" + ask(agent, motion) + "\n")


if __name__ == "__main__":
    main()
