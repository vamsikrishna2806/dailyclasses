"""
HIERARCHICAL multi-agent  (a company: manager -> team leads -> workers)
-----------------------------------------------------------------------
The top MANAGER only talks to TEAMS. Each team is its OWN small graph with its own workers
(a graph inside a graph). Teams report back to the manager.

                       ┌──────── product team ─────────┐
    START -> manager ──┤  researcher -> spec_writer -> lead │──┐
                ^      └────────────────────────────────┘    │
                │      ┌──────── marketing team ───────┐     │
                ├──────┤  copywriter -> social_planner -> lead │
                │      └────────────────────────────────┘    │
                └───────────────────(report back)────────────┘
                manager says FINISH -> END
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import audience_insights

OLLAMA_MODEL = "llama3.2"
MAX_STEPS = 5
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)

MANAGER_PROMPT = """You are the MANAGER of a company with two teams:
  product   -> researches the audience and writes a product spec
  marketing -> writes the tagline, pitch and social posts
Decide which team works NEXT. Product comes first, then marketing, then FINISH.
Answer with EXACTLY ONE word: product, marketing, or FINISH."""

RESEARCHER_PROMPT = "You are a RESEARCHER. Call audience_insights with the product idea, then report the audience in 2 short bullets."
SPEC_WRITER_PROMPT = "You are a SPEC WRITER. From the idea and audience facts, write 3 short bullet points: the key features. Return only the bullets."
PRODUCT_LEAD_PROMPT = "You are the PRODUCT LEAD. Merge the research and features into a 'PRODUCT SPEC' of 4 short lines. Return only the spec."
COPYWRITER_PROMPT = "You are a COPYWRITER. Using the product spec, write a tagline (max 6 words) and a 2-sentence pitch. Return only those."
SOCIAL_PLANNER_PROMPT = "You are a SOCIAL PLANNER. Write 3 short social media posts (one line each, with an emoji) for this product."
MARKETING_LEAD_PROMPT = "You are the MARKETING LEAD. Combine the copy and posts into a tidy 'CAMPAIGN' section. Return only the campaign."

researcher_agent = create_react_agent(llm, [audience_insights])


def say(system: str, user: str) -> str:
    return llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content.strip()


# =====================================================================
# LEVEL 2 — each TEAM is its own graph with its own small state
# =====================================================================
class TeamState(TypedDict):
    brief: str     # what the team was asked to do (+ context from other teams)
    step1: str     # first worker's output
    step2: str     # second worker's output
    report: str    # the lead's final report


def build_product_team():
    def researcher(s: TeamState):
        print("      🔎 [researcher]     asking the audience tool...")
        out = researcher_agent.invoke({"messages": [SystemMessage(content=RESEARCHER_PROMPT), HumanMessage(content=s["brief"])]})
        return {"step1": out["messages"][-1].content}

    def spec_writer(s: TeamState):
        print("      📝 [spec_writer]    drafting features...")
        return {"step2": say(SPEC_WRITER_PROMPT, f"Idea: {s['brief']}\n\nAudience:\n{s['step1']}")}

    def lead(s: TeamState):
        print("      👩‍💼 [product_lead]  merging into the product spec...")
        return {"report": say(PRODUCT_LEAD_PROMPT, f"Audience:\n{s['step1']}\n\nFeatures:\n{s['step2']}")}

    return _linear_team(researcher, spec_writer, lead)


def build_marketing_team():
    def copywriter(s: TeamState):
        print("      ✍️  [copywriter]     writing tagline + pitch...")
        return {"step1": say(COPYWRITER_PROMPT, s["brief"])}

    def social_planner(s: TeamState):
        print("      📣 [social_planner] writing social posts...")
        return {"step2": say(SOCIAL_PLANNER_PROMPT, s["brief"])}

    def lead(s: TeamState):
        print("      👨‍💼 [marketing_lead] assembling the campaign...")
        return {"report": say(MARKETING_LEAD_PROMPT, f"Copy:\n{s['step1']}\n\nPosts:\n{s['step2']}")}

    return _linear_team(copywriter, social_planner, lead)


def _linear_team(worker1, worker2, lead):
    g = StateGraph(TeamState)
    g.add_node("worker1", worker1)
    g.add_node("worker2", worker2)
    g.add_node("lead", lead)
    g.add_edge(START, "worker1")
    g.add_edge("worker1", "worker2")
    g.add_edge("worker2", "lead")
    g.add_edge("lead", END)
    return g.compile()           # <- a finished graph that we will use as ONE node below


product_team = build_product_team()
marketing_team = build_marketing_team()


# =====================================================================
# LEVEL 1 — the manager's graph only sees two big nodes: the teams
# =====================================================================
class State(TypedDict):
    idea: str
    product: str       # product team's report
    marketing: str     # marketing team's report
    next: str
    steps: int


def manager_node(state: State):
    progress = (f"Idea: {state['idea']}\nProduct team done: {'yes' if state['product'] else 'no'}\n"
                f"Marketing team done: {'yes' if state['marketing'] else 'no'}")
    word = say(MANAGER_PROMPT, progress).lower()
    choice = next((t for t in ("product", "marketing") if t in word), "FINISH")
    # Guard rails: never repeat a team that is already done.
    if choice == "product" and state["product"]:
        choice = "marketing"
    if choice == "marketing" and state["marketing"]:
        choice = "FINISH"
    if not state["product"]:
        choice = "product"                   # marketing needs the spec first
    if state["product"] and state["marketing"] or state["steps"] >= MAX_STEPS:
        choice = "FINISH"
    print(f"  🏢 [manager] -> {choice}")
    return {"next": choice, "steps": state["steps"] + 1}


def product_node(state: State):
    r = product_team.invoke({"brief": state["idea"], "step1": "", "step2": "", "report": ""})
    return {"product": r["report"]}


def marketing_node(state: State):
    brief = f"Product idea: {state['idea']}\n\n{state['product']}"
    r = marketing_team.invoke({"brief": brief, "step1": "", "step2": "", "report": ""})
    return {"marketing": r["report"]}


def build_agent():
    g = StateGraph(State)
    g.add_node("manager", manager_node)
    g.add_node("product", product_node)
    g.add_node("marketing", marketing_node)
    g.add_edge(START, "manager")
    g.add_conditional_edges("manager", lambda s: s["next"],
                            {"product": "product", "marketing": "marketing", "FINISH": END})
    g.add_edge("product", "manager")      # teams report back to the manager
    g.add_edge("marketing", "manager")
    return g.compile()


def ask(agent, idea):
    r = agent.invoke({"idea": idea, "product": "", "marketing": "", "next": "", "steps": 0})
    return f"{r['product']}\n\n{r['marketing']}"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  🏢  Hierarchical Agent  (manager → teams → workers)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Teams: product (3 agents), marketing (3 agents)")
    print("  Try: 'a note-taking app' or 'a language learning app'\n")
    agent = build_agent()
    while True:
        try:
            idea = input("Product idea: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not idea: continue
        if idea.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\n" + ask(agent, idea) + "\n")


if __name__ == "__main__":
    main()
