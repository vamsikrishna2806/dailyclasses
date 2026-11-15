import re
from collections import Counter

URGENT = ("urgent", "act now", "limited time", "last chance", "immediately", "expires", "hurry")
MONEY = ("free", "winner", "prize", "cash", "$$$", "lottery", "gift card", "100% guaranteed", "claim")


def spam_signals(text: str) -> dict:
    """Count simple, objective spam warning signs. (Plain code — no AI.)"""
    t = text.lower()
    letters = [c for c in text if c.isalpha()]
    caps = round(sum(c.isupper() for c in letters) / len(letters), 2) if letters else 0
    signals = {
        "links": len(re.findall(r"https?://|www\.|bit\.ly", t)),
        "urgent_words": sum(w in t for w in URGENT),
        "money_words": sum(w in t for w in MONEY),
        "exclamations": text.count("!"),
        "caps_ratio": caps,
    }
    signals["score"] = (signals["links"] * 2 + signals["urgent_words"] * 2 + signals["money_words"] * 2
                        + min(signals["exclamations"], 3) + (2 if caps > 0.4 else 0))
    return signals


def parse_vote(text: str) -> str:
    """Read SPAM / NOT_SPAM / UNSURE from a juror's reply."""
    t = text.upper().replace("NOT SPAM", "NOT_SPAM").replace("NOT-SPAM", "NOT_SPAM")
    first = t.strip()[:30]
    if "NOT_SPAM" in first: return "NOT_SPAM"
    if "SPAM" in first: return "SPAM"
    if "UNSURE" in first: return "UNSURE"
    return "NOT_SPAM" if "NOT_SPAM" in t else "SPAM" if "SPAM" in t else "UNSURE"


def tally(votes: list):
    """Count votes. Returns (winner or None, Counter). A winner needs at least 2 votes."""
    counts = Counter(v for v in votes if v != "UNSURE")
    if counts:
        top, n = counts.most_common(1)[0]
        if n >= 2 and list(counts.values()).count(n) == 1:
            return top, counts
    return None, counts


def parse_reply(text: str) -> str:
    """Turn 'Reason: ... / Vote: SPAM' (two lines) into one tidy line 'SPAM - ...' (vote first, easy to read)."""
    m = re.search(r"vote:\s*([A-Za-z_ -]+)", text, re.I)
    vote = parse_vote(m.group(1)) if m else parse_vote(text)
    r = re.search(r"reason:\s*(.+)", text, re.I)
    reason = (r.group(1) if r else text.strip().splitlines()[0]).strip()
    return f"{vote} - {reason}"
