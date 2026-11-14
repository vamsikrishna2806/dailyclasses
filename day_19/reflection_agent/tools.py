from langchain_core.tools import tool


@tool
def count_words(text: str) -> str:
    """Count the words in a piece of text and report whether it is short, medium or long."""
    n = len(text.split())
    size = "short" if n < 60 else "medium" if n < 150 else "long"
    return f"{n} words ({size})"
