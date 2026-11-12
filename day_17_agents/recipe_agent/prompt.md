# Recipe Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a friendly and passionate chef assistant.
When a user asks for a recipe or cooking help, use the search_recipe tool to find it.
Present the ingredients clearly, explain the steps in simple language, and add
helpful cooking tips — substitutions, serving suggestions, or difficulty notes.
Make cooking feel approachable and fun for everyone.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational cooking assistant CLI agent in Python using LangChain
and LangGraph with one recipe search tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.4 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  API       : TheMealDB (themealdb.com/api/json/v1/1/search.php) — free, no key

TOOL (1)
  search_recipe(dish: str) -> str
    - GET https://www.themealdb.com/api/json/v1/1/search.php?s={dish}
    - Extract from meals[0]: strMeal, strArea, strCategory, strInstructions
    - Loop strIngredient1..20 + strMeasure1..20 to build ingredient list
    - Return: recipe name, cuisine, category, ingredients bullet list,
      first 1000 chars of instructions

SYSTEM PROMPT
  "You are a friendly and passionate chef assistant. When a user asks for a
  recipe or cooking help, use the search_recipe tool to find it. Present the
  ingredients clearly, explain the steps in simple language, and add helpful
  cooking tips — substitutions, serving suggestions, or difficulty notes.
  Make cooking feel approachable and fun for everyone."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← search_recipe tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def search_recipe(dish: str) -> str:
    """
    Search for a recipe by dish name. Returns ingredients, measurements,
    and step-by-step cooking instructions. Uses TheMealDB — free, no API key.
    """
```

---

## Example Interaction

```
You: How do I make biryani?

Agent:
Recipe: Chicken Biryani
Cuisine: Indian | Category: Chicken

Ingredients:
  • 1kg Chicken
  • 400g Basmati Rice
  • 2 large Onions
  • 2 tbsp Ghee
  • 1 tsp Cumin seeds
  ... (full list)

Instructions:
Wash the rice and soak for 30 minutes. Heat ghee in a heavy-bottomed pan,
fry the onions until golden brown...

Tip: If you don't have ghee, clarified butter works perfectly!
Serve with raita and a wedge of lemon.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.4` | Slight warmth for friendly, encouraging tone |
| Single tool | One well-scoped search is enough for recipe lookup |
| TheMealDB | Completely free, no API key, wide recipe coverage |
| Ingredients loop up to 20 | TheMealDB stores up to 20 ingredient/measure pairs |
| Truncate instructions to 1000 chars | Prevents token overload for small local models |
