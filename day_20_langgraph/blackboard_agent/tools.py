import re

# Fake grocery prices (dollars) so the demo works offline.
PRICES = {
    "chicken": 8.0, "beef": 10.0, "fish": 9.0, "salmon": 11.0, "tofu": 3.0, "eggs": 3.0,
    "rice": 2.0, "pasta": 2.0, "bread": 2.5, "potato": 2.0, "beans": 1.5, "lentils": 2.0,
    "tomato": 2.0, "onion": 1.0, "carrot": 1.5, "broccoli": 3.0, "spinach": 2.5, "pepper": 2.5,
    "cheese": 4.0, "milk": 2.0, "yogurt": 2.5, "butter": 3.5, "oil": 3.0, "garlic": 1.0,
}
DEFAULT_PRICE = 3.0


def pantry_text() -> str:
    """The shop's price list as one line — the chef may ONLY use these items, so costs are meaningful."""
    return ", ".join(f"{k} ${v:g}" for k, v in PRICES.items())


def price_of(item: str) -> float:
    """Price of one grocery item (matches by keyword; unknown items cost $3)."""
    name = item.lower()
    for key, price in PRICES.items():
        if key in name:
            return price
    return DEFAULT_PRICE


def parse_list(text: str) -> list:
    """Turn '- chicken\\n- rice' into ['chicken', 'rice'] (no duplicates, original order)."""
    items = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*•]\s*(.+)$", line)
        if m:
            item = re.sub(r"[\(\[].*?[\)\]]", "", m.group(1)).strip(" .,:;").lower()
            if item and item not in items:
                items.append(item)
    return items


def parse_budget(text: str, default: float = 30.0) -> float:
    """Find '$25' or '25 dollars' in the request."""
    m = re.search(r"\$\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*dollars", text)
    return float(m.group(1) or m.group(2)) if m else default
