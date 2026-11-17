# Blackboard Agent — Prompts

---

## System Prompts
> Runtime instructions copied from `agent.py` (3 prompts — one per LLM role).

### `NUTRITIONIST_PROMPT`
```
You are a NUTRITIONIST. From the request, write 3 short dietary rules for the meal plan
(one per line, starting with '- '). Return ONLY the 3 lines.
```

### `CHEF_PROMPT`
```
You are a CHEF. Plan a menu of 3 simple dishes (one per day) that follows the dietary rules.
Use ONLY ingredients from the PANTRY list and at most 4 ingredients per dish. Every ingredient has a price —
the WHOLE menu must stay inside the budget, so prefer cheap items.
Return ONLY this format, with no extra comments, no totals, no notes:
Day 1: <dish name>
- ingredient
- ingredient
Day 2: ...
If there is BUDGET FEEDBACK, the last menu was too expensive: use mostly items that cost $2.5 or less.
```

### `SHOPPER_PROMPT`
```
You are a SHOPPER. Read the menu and write ONE shopping list of every ingredient:
one simple ingredient per line starting with '- ', no quantities, no duplicates. Return ONLY the list.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a BLACKBOARD multi-agent CLI in Python using LangChain and LangGraph.
Specialists coordinate ONLY through a shared board; a rule-based controller wakes whoever can contribute.

STACK
  LLM       : Ollama llama3.2 (via langchain-ollama)
  Framework : LangGraph StateGraph
  Free, runs locally, no API key. requirements.txt: langchain, langchain-ollama, langgraph

TOOLS (tools.py): PRICES dict of cheap grocery items; price_of(item) (keyword match, default $3);
  parse_list(text) -> items from '- item' lines; parse_budget(text, default=30) from '$20' / '20 dollars'; pantry_text()

STATE (TypedDict): board (dict), next, steps
BOARD keys: request, budget, constraints, menu, ingredients (list), cost, verdict, feedback, revisions

RULES (dict name -> function(board) -> bool)
  nutritionist: not constraints | chef: constraints and not menu | shopper: menu and not ingredients | auditor: ingredients and not verdict

NODES
  controller   : NO LLM. first specialist whose rule is true, else DONE (also DONE when steps >= 10)
  nutritionist : LLM, 3 dietary rules from the request -> constraints
  chef         : LLM, 3-day menu using ONLY the priced pantry, at most 4 ingredients per dish, within budget;
                 if feedback exists, make it cheaper -> menu
  shopper      : LLM, merged ingredient list -> ingredients; code computes cost = sum(price_of)
  auditor      : NO LLM. if cost > budget and revisions < 2: ERASE menu/ingredients/verdict, set feedback, revisions += 1
                 else set verdict APPROVED or OVER BUDGET

GRAPH   START -> controller -> conditional(specialist | DONE: END) ; every specialist -> controller

CLI     loop: ask 'Meal request:', print '[board] -> who' lines, then menu, shopping list, total vs budget and verdict.
```
