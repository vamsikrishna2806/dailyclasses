"""20 · LangGraph Basics

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    count: int

def clean(state: State):
    return {"text": state["text"].strip()}

def count_words(state: State):
    return {"count": len(state["text"].split())}

def route(state: State) -> str:
    return "long" if state["count"] > 5 else "short"

builder = StateGraph(State)
builder.add_node("clean", clean)
builder.add_node("count", count_words)
builder.add_edge(START, "clean")
builder.add_edge("clean", "count")
builder.add_conditional_edges("count", route, {"long": END, "short": END})

graph = builder.compile()
print(graph.invoke({"text": "  hello big world  ", "count": 0}))
