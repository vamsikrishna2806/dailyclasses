import re


def clean_text(text: str) -> str:
    """Small models love to start with 'Here is...:' — drop that intro line."""
    lines = text.strip().splitlines()
    if lines and lines[0].lower().startswith("here") and lines[0].rstrip().endswith(":"):
        lines = lines[1:]
    return "\n".join(lines).strip()


def count_words(text: str) -> int:
    """Count the words in a text."""
    return len(re.findall(r"\b\w[\w'-]*\b", text))


def reading_time(text: str, wpm: int = 200) -> str:
    """Estimate reading time (average adult reads ~200 words per minute)."""
    seconds = round(count_words(text) / wpm * 60)
    return f"{seconds} sec" if seconds < 90 else f"{seconds / 60:.1f} min"
