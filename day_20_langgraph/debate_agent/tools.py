def trim_words(text: str, limit: int = 60) -> str:
    """Keep a debater's speech short: cut after `limit` words."""
    words = text.strip().split()
    return " ".join(words[:limit]) + ("…" if len(words) > limit else "")


def format_transcript(speeches: list) -> str:
    """Turn the list of speeches into a readable transcript for the next speaker / judge."""
    return "\n".join(speeches) if speeches else "(no speeches yet)"


def parse_winner(verdict: str) -> str:
    """Find PRO or CON in the judge's reply. Returns 'PRO', 'CON' or 'TIE'."""
    text = verdict.upper()
    pro, con = text.find("WINNER: PRO"), text.find("WINNER: CON")
    if pro == -1 and con == -1:
        return "TIE"
    if pro == -1: return "CON"
    if con == -1: return "PRO"
    return "PRO" if pro < con else "CON"
