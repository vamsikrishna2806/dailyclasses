"""
BLACKBOARD multi-agent  (shared workspace)
------------------------------------------
Imagine a whiteboard in a meeting room. Specialists do NOT talk to each other and
nobody tells them what to do. Each specialist only watches the board:
"Is there something here I can add to?"  If yes, it writes its part on the board.

    The controller (plain Python rules, NO AI) simply asks:
    "Who can contribute right now?" and wakes that specialist.

        nutritionist  needs: request           adds: constraints
        chef          needs: constraints       adds: menu
        shopper       needs: menu              adds: shopping list + cost
        auditor       needs: shopping list     adds: verdict  (too expensive? ERASES the menu -> chef redoes it)
"""
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from tools import price_of, parse_list, parse_budget, pantry_text

OLLAMA_MODEL = "llama3.2"
MAX_STEPS = 10          # safety limit on controller loops
MAX_REVISIONS = 2       # how many times the auditor may send the chef back
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)

NUTRITIONIST_PROMPT = """You are a NUTRITIONIST. From the request, write 3 short dietary rules for the meal plan
(one per line, starting with '- '). Return ONLY the 3 lines."""

CHEF_PROMPT = """You are a CHEF. Plan a menu of 3 simple dishes (one per day) that follows the dietary rules.
Use ONLY ingredients from the PANTRY list and at most 4 ingredients per dish. Every ingredient has a price —
the WHOLE menu must stay inside the budget, so prefer cheap items.
Return ONLY this format, with no extra comments, no totals, no notes:
Day 1: <dish name>
- ingredient
- ingredient
Day 2: ...
If there is BUDGET FEEDBACK, the last menu was too expensive: use mostly items that cost $2.5 or less."""

SHOPPER_PROMPT = """You are a SHOPPER. Read the menu and write ONE shopping list of every ingredient:
one simple ingredient per line starting with '- ', no quantities, no duplicates. Return ONLY the list."""


def say(system: str, user: str) -> str:
    return llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content.strip()


# ---------- State: the BOARD ----------
class State(TypedDict):
    board: dict      # the shared workspace everyone reads and writes
    next: str        # who the controller woke up
    steps: int


def new_board(request: str) -> dict:
    return {"request": request, "budget": parse_budget(request), "constraints": "", "menu": "",
            "ingredients": [], "cost": 0.0, "verdict": "", "feedback": "", "revisions": 0}


# ---------- The rules: "when may each specialist contribute?" ----------
RULES = {
    "nutritionist": lambda b: not b["constraints"],
    "chef":         lambda b: b["constraints"] and not b["menu"],
    "shopper":      lambda b: b["menu"] and not b["ingredients"],
    "auditor":      lambda b: b["ingredients"] and not b["verdict"],
}


def controller_node(state: State):
    """No AI here. First specialist whose rule is true wakes up. Nobody can? We are done."""
    choice = next((name for name, can in RULES.items() if can(state["board"])), "DONE")
    if state["steps"] >= MAX_STEPS:
        choice = "DONE"
    print(f"  📋 [board] -> {choice}")
    return {"next": choice, "steps": state["steps"] + 1}


# ---------- Specialists ----------
def nutritionist_node(state: State):
    b = dict(state["board"])
    b["constraints"] = say(NUTRITIONIST_PROMPT, b["request"])
    print("       🥗 nutritionist wrote dietary rules on the board")
    return {"board": b}


def chef_node(state: State):
    b = dict(state["board"])
    msg = (f"Request: {b['request']}\nBUDGET FOR THE WHOLE MENU: ${b['budget']:.0f}\n\n"
           f"Dietary rules:\n{b['constraints']}\n\nPANTRY (item $price): {pantry_text()}")
    if b["feedback"]:
        msg += f"\n\nBUDGET FEEDBACK: {b['feedback']} Make it cheaper!"
    b["menu"] = say(CHEF_PROMPT, msg)
    print("       👨‍🍳 chef wrote a menu on the board" + (" (cheaper version)" if b["feedback"] else ""))
    return {"board": b}


def shopper_node(state: State):
    b = dict(state["board"])
    items = parse_list(say(SHOPPER_PROMPT, b["menu"]))
    b["ingredients"] = items
    b["cost"] = round(sum(price_of(i) for i in items), 2)
    print(f"       🛒 shopper listed {len(items)} items, total ${b['cost']:.2f}")
    return {"board": b}


def auditor_node(state: State):
    """Plain Python judge: compares cost with budget. Too expensive? ERASE the menu so the chef is re-triggered."""
    b = dict(state["board"])
    if b["cost"] > b["budget"] and b["revisions"] < MAX_REVISIONS:
        print(f"       🧾 auditor: ${b['cost']:.2f} is over ${b['budget']:.0f} -> erasing menu, chef must redo it")
        priciest = sorted(b["ingredients"], key=price_of, reverse=True)[:3]       # be SPECIFIC so the chef can act
        pricey_text = ", ".join(f"{i} (${price_of(i):g})" for i in priciest)
        b.update(menu="", ingredients=[], verdict="", revisions=b["revisions"] + 1,
                 feedback=f"Last menu cost ${b['cost']:.2f} but the budget is ${b['budget']:.0f}. "
                          f"The most expensive items were: {pricey_text}. Do NOT use them again.")
    else:
        ok = b["cost"] <= b["budget"]
        b["verdict"] = "APPROVED ✅ within budget" if ok else "OVER BUDGET ⚠️ (revision limit reached)"
        print(f"       🧾 auditor: {b['verdict']}")
    return {"board": b}


# ---------- Graph ----------
def build_agent():
    g = StateGraph(State)
    g.add_node("controller", controller_node)
    g.add_node("nutritionist", nutritionist_node)
    g.add_node("chef", chef_node)
    g.add_node("shopper", shopper_node)
    g.add_node("auditor", auditor_node)

    g.add_edge(START, "controller")
    g.add_conditional_edges("controller", lambda s: s["next"],
                            {"nutritionist": "nutritionist", "chef": "chef", "shopper": "shopper",
                             "auditor": "auditor", "DONE": END})
    for name in ("nutritionist", "chef", "shopper", "auditor"):
        g.add_edge(name, "controller")             # everyone writes to the board, then control returns
    return g.compile()


def ask(agent, request):
    b = agent.invoke({"board": new_board(request), "next": "", "steps": 0})["board"]
    return (f"MENU:\n{b['menu']}\n\nSHOPPING LIST: {', '.join(b['ingredients'])}\n"
            f"TOTAL: ${b['cost']:.2f}  (budget ${b['budget']:.0f})\nVERDICT: {b['verdict']}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 52)
    print("  📋  Blackboard Agent  (specialists share one board)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Specialists: nutritionist, chef, shopper, auditor")
    print("  Try: 'Vegetarian dinners for 3 days under $20'\n")
    agent = build_agent()
    while True:
        try:
            request = input("Meal request: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!"); break
        if not request: continue
        if request.lower() in ("quit", "exit", "q"):
            print("Bye!"); break
        print()
        print("\n" + ask(agent, request) + "\n")


if __name__ == "__main__":
    main()
