import requests
from langchain_core.tools import tool


@tool
def get_joke(category: str = "Any") -> str:
    """
    Get a random joke. Categories: Any, Programming, Misc, Dark, Pun, Spooky, Christmas.
    Uses JokeAPI — free, no API key required.
    """
    valid = ["Any", "Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas"]
    cat = category.strip().title()
    if cat not in valid:
        cat = "Any"

    r = requests.get(
        f"https://v2.jokeapi.dev/joke/{cat}",
        params={"blacklistFlags": "nsfw,explicit,racist,sexist"},
        timeout=10
    )
    data = r.json()

    if data.get("type") == "single":
        return f"😄 {data['joke']}"
    elif data.get("type") == "twopart":
        return f"😄 {data['setup']}\n\n...{data['delivery']} 🥁"
    return "Could not fetch a joke right now. Try again!"


@tool
def get_number_fact(number: str) -> str:
    """
    Get an interesting trivia fact about a number, year, or date.
    Examples: '42', '1969', 'random'. Uses NumbersAPI — free, no API key.
    """
    n = number.strip().lower()
    if n == "random":
        url = "http://numbersapi.com/random/trivia"
    else:
        url = f"http://numbersapi.com/{n}/trivia"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return f"🔢 {r.text}"
        return f"No fact found for '{number}'."
    except Exception as e:
        return f"Could not fetch fact: {str(e)}"
