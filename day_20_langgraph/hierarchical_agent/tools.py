from langchain_core.tools import tool

# Fake market-research "database" so the demo works offline — no API key needed.
INSIGHTS = {
    "note": "Students and professionals (18-35). Top pain: notes scattered across apps. Wants: fast search, offline mode, sync.",
    "fitness": "Busy adults (25-45). Top pain: no motivation. Wants: short workouts, streaks, progress charts.",
    "budget": "Young earners (20-35). Top pain: not knowing where money goes. Wants: auto-categories, simple charts, alerts.",
    "language": "Learners of all ages. Top pain: forgetting words. Wants: daily practice, spaced repetition, speaking games.",
}
DEFAULT = "General audience (18-45). Wants: simple, fast, free to try, works on phone."


@tool
def audience_insights(product_idea: str) -> str:
    """Get facts about the target audience for a product idea (e.g. a note app, fitness app, budget app, language app)."""
    idea = product_idea.lower()
    for key, facts in INSIGHTS.items():
        if key in idea:
            return facts
    return DEFAULT
