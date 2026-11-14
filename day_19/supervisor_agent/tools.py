import requests
from langchain_core.tools import tool


@tool
def wiki_summary(topic: str) -> str:
    """
    Get a short factual summary of a topic from Wikipedia.
    Uses the free Wikipedia REST API — no API key.
    """
    title = topic.strip().replace(" ", "_")
    r = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
        headers={"User-Agent": "student-agent-demo/1.0"},
        timeout=10,
    )
    if r.status_code != 200:
        return f"No Wikipedia page found for '{topic}'. Try a simpler or more general title."
    return r.json().get("extract", "No summary available.")
