"""
PIPELINE (assembly line) multi-agent
------------------------------------
Four specialist agents work in a FIXED order. Each one reads what the
previous one produced and adds its own piece:

    START -> outliner -> writer -> editor -> headline -> quality_gate -> END
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import clean_text, count_words, reading_time

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.5)

# ---------- Prompts: one per agent (each agent = one LLM + one job) ----------
OUTLINER_PROMPT = """You are an OUTLINER. Make a 3-point outline for a short blog post about the topic.
One short line per point. Return ONLY the 3 numbered lines."""

WRITER_PROMPT = """You are a BLOG WRITER. Write a short blog post (about 120 words) that follows the outline exactly.
Return ONLY the post text — no title, no intro."""

EDITOR_PROMPT = """You are an EDITOR. Improve the clarity and grammar of the post, remove repetition,
and keep about the same length. Return ONLY the edited post."""

HEADLINE_PROMPT = """You are a HEADLINE WRITER. Write ONE catchy headline (max 10 words) for this post.
Return ONLY the headline — no quotes, no intro."""


# ---------- State: the "baton" passed along the line ----------
class State(TypedDict):
    topic: str
    outline: str
    draft: str
    edited: str
    headline: str
    report: str


def ask_llm(system: str, user: str) -> str:
    return clean_text(llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content)


# ---------- Agents (nodes) ----------
def outliner_node(state: State):
    print("  1/5 🗂️  [outliner]  planning the structure...")
    return {"outline": ask_llm(OUTLINER_PROMPT, f"Topic: {state['topic']}")}


def writer_node(state: State):
    print("  2/5 ✍️  [writer]    writing the first draft...")
    msg = f"Topic: {state['topic']}\n\nOutline:\n{state['outline']}"
    return {"draft": ask_llm(WRITER_PROMPT, msg)}


def editor_node(state: State):
    print("  3/5 🧹 [editor]    polishing the draft...")
    return {"edited": ask_llm(EDITOR_PROMPT, state["draft"])}


def headline_node(state: State):
    print("  4/5 📰 [headline]  choosing a headline...")
    return {"headline": ask_llm(HEADLINE_PROMPT, state["edited"]).strip('"')}


def quality_gate_node(state: State):
    """Plain Python (NO LLM): not every node needs AI. This one just measures."""
    print("  5/5 📏 [quality]   measuring the result (plain code, no AI)")
    words = count_words(state["edited"])
    return {"report": f"{words} words · reading time {reading_time(state['edited'])}"}


# ---------- Graph: a straight line ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("outliner", outliner_node)
    g.add_node("writer", writer_node)
    g.add_node("editor", editor_node)
    g.add_node("headline", headline_node)
    g.add_node("quality_gate", quality_gate_node)

    g.add_edge(START, "outliner")
    g.add_edge("outliner", "writer")
    g.add_edge("writer", "editor")
    g.add_edge("editor", "headline")
    g.add_edge("headline", "quality_gate")
    g.add_edge("quality_gate", END)
    return g.compile()


def ask(agent, topic):
    r = agent.invoke({"topic": topic, "outline": "", "draft": "", "edited": "", "headline": "", "report": ""})
    return f"# {r['headline']}\n\n{r['edited']}\n\n({r['report']})"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🏭  Pipeline Agent  (outline → write → edit → headline)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}")
    print("  Try: 'Why sleep matters' or 'Learning to cook'\n")
    agent = build_agent()
    while True:
        try:
            topic = input("Blog topic: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not topic: continue
        if topic.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\n" + ask(agent, topic) + "\n")


if __name__ == "__main__":
    main()
