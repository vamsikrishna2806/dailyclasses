import requests
from langchain_core.tools import tool


@tool
def search_recipe(dish: str) -> str:
    """
    Search for a recipe by dish name. Returns ingredients, measurements,
    and step-by-step cooking instructions. Uses TheMealDB — free, no API key.
    """
    r = requests.get(
        "https://www.themealdb.com/api/json/v1/1/search.php",
        params={"s": dish}, timeout=10
    )
    data = r.json()
    if not data.get("meals"):
        return f"No recipe found for '{dish}'. Try a different dish name."

    meal = data["meals"][0]
    ingredients = []
    for i in range(1, 21):
        ing = (meal.get(f"strIngredient{i}") or "").strip()
        meas = (meal.get(f"strMeasure{i}") or "").strip()
        if ing:
            ingredients.append(f"{meas} {ing}".strip())

    instructions = (meal.get("strInstructions") or "")[:1000]

    return (
        f"Recipe: {meal['strMeal']}\n"
        f"Cuisine: {meal.get('strArea', 'N/A')} | Category: {meal.get('strCategory', 'N/A')}\n\n"
        f"Ingredients:\n" + "\n".join(f"  • {i}" for i in ingredients) +
        f"\n\nInstructions:\n{instructions}..."
    )
