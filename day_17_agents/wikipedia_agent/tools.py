import wikipedia
from langchain_core.tools import tool


@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for a summary about any topic, person, place, or concept.
    Returns a 5-sentence summary and the article URL. Free, no API key.
    """
    try:
        results = wikipedia.search(query, results=3)
        if not results:
            return f"No Wikipedia results found for '{query}'."

        try:
            page = wikipedia.page(results[0], auto_suggest=False)
            summary = wikipedia.summary(results[0], sentences=5, auto_suggest=False)
        except wikipedia.exceptions.DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            summary = wikipedia.summary(e.options[0], sentences=5, auto_suggest=False)

        return (
            f"Wikipedia: {page.title}\n"
            f"URL      : {page.url}\n\n"
            f"{summary}"
        )
    except Exception as e:
        return f"Could not fetch Wikipedia page: {str(e)}"
