import requests
from langchain_core.tools import tool


@tool
def search_github_repos(query: str) -> str:
    """
    Search GitHub for public repositories matching a topic, technology, or keyword.
    Returns top 5 results with stars, description, and URL.
    Uses GitHub public API — free, no API key required.
    """
    r = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": 5},
        headers={"Accept": "application/vnd.github.v3+json"},
        timeout=10
    )
    data = r.json()

    if not data.get("items"):
        return f"No GitHub repositories found for '{query}'."

    total = data.get("total_count", 0)
    result = f"GitHub Search: '{query}' — {total:,} total repos found\nTop 5:\n\n"

    for i, repo in enumerate(data["items"], 1):
        result += (
            f"[{i}] {repo['full_name']}\n"
            f"     ⭐ {repo['stargazers_count']:,} stars  "
            f"🍴 {repo['forks_count']:,} forks  "
            f"[{repo.get('language', 'N/A')}]\n"
            f"     {repo.get('description', 'No description') or 'No description'}\n"
            f"     {repo['html_url']}\n\n"
        )
    return result.strip()
