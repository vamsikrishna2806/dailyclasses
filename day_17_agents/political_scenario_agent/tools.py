from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web for current political news, events, policies, elections,
    geopolitical developments, or any factual information about world affairs.
    Returns the top 5 search results with title, URL, and snippet.
    Uses DuckDuckGo — free, no API key required.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"No results found for: '{query}'"

        output_lines = [f"Web Search Results for: '{query}'\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            href = r.get("href", "")
            body = r.get("body", "No snippet available")
            output_lines.append(f"[{i}] {title}")
            output_lines.append(f"    URL : {href}")
            output_lines.append(f"    Info: {body}\n")

        return "\n".join(output_lines)

    except Exception as e:
        return f"Search failed: {str(e)}. Try rephrasing the query."
