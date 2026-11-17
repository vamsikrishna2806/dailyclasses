"""
PARALLEL (fan-out / fan-in) multi-agent
---------------------------------------
Three independent specialists work AT THE SAME TIME (fan-out).
When ALL of them finish, one planner merges their results (fan-in).

                 ┌─► flights    ─┐
    START ───────┼─► hotels     ─┼──► planner ─► END
                 └─► activities ─┘
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import search_flights, search_hotels, search_activities, find_city

OLLAMA_MODEL = "llama3.2"
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

FLIGHTS_PROMPT = "You are a flight specialist. Call search_flights for the city, then list the options as 2 short bullets."
HOTELS_PROMPT = "You are a hotel specialist. Call search_hotels for the city, then list the options as 2 short bullets."
ACTIVITIES_PROMPT = "You are an activities specialist. Call search_activities for the city, then list the options as short bullets."
PLANNER_PROMPT = """You are a trip planner. You get flight, hotel and activity research for a city.
Write a friendly 3-day itinerary (Day 1, Day 2, Day 3, one line each) and finish with a line
'Budget tip:' naming the cheapest flight and hotel. Use ONLY the facts you were given."""

# Each worker is a small ReAct agent with exactly ONE tool.
flights_agent = create_react_agent(llm, [search_flights])
hotels_agent = create_react_agent(llm, [search_hotels])
activities_agent = create_react_agent(llm, [search_activities])


# ---------- State ----------
# IMPORTANT: parallel nodes must write to DIFFERENT keys, otherwise they overwrite each other.
class State(TypedDict):
    city: str
    flights: str
    hotels: str
    activities: str
    plan: str


def run_worker(agent, prompt, city):
    out = agent.invoke({"messages": [SystemMessage(content=prompt), HumanMessage(content=f"City: {city}")]})
    return out["messages"][-1].content


# ---------- Workers (they run in parallel) ----------
def flights_node(state: State):
    print("  ✈️  [flights]     searching...")
    return {"flights": run_worker(flights_agent, FLIGHTS_PROMPT, state["city"])}


def hotels_node(state: State):
    print("  🏨 [hotels]      searching...")
    return {"hotels": run_worker(hotels_agent, HOTELS_PROMPT, state["city"])}


def activities_node(state: State):
    print("  🎡 [activities]  searching...")
    return {"activities": run_worker(activities_agent, ACTIVITIES_PROMPT, state["city"])}


# ---------- Fan-in: waits until all three are done ----------
def planner_node(state: State):
    print("  🧭 [planner]     all 3 reports arrived — merging into one plan")
    msg = (f"City: {state['city']}\n\nFLIGHTS:\n{state['flights']}\n\n"
           f"HOTELS:\n{state['hotels']}\n\nACTIVITIES:\n{state['activities']}")
    return {"plan": llm.invoke([SystemMessage(content=PLANNER_PROMPT), HumanMessage(content=msg)]).content}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("flights", flights_node)
    g.add_node("hotels", hotels_node)
    g.add_node("activities", activities_node)
    g.add_node("planner", planner_node)

    # FAN-OUT: three edges leave START → all three nodes start together
    for worker in ("flights", "hotels", "activities"):
        g.add_edge(START, worker)
    # FAN-IN: ONE edge with a LIST of sources → planner waits for ALL of them
    g.add_edge(["flights", "hotels", "activities"], "planner")
    g.add_edge("planner", END)
    return g.compile()


def ask(agent, text):
    city = find_city(text)
    if not city:
        return "I only know: Paris, Tokyo, Goa, New York. Try one of those!"
    return agent.invoke({"city": city, "flights": "", "hotels": "", "activities": "", "plan": ""})["plan"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  ⚡  Parallel Agent  (3 specialists at once → 1 planner)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Cities: Paris, Tokyo, Goa, New York\n")
    agent = build_agent()
    while True:
        try:
            text = input("Which city? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not text: continue
        if text.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\nTrip plan:\n" + ask(agent, text) + "\n")


if __name__ == "__main__":
    main()
