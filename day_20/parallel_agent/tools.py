from langchain_core.tools import tool

# Fake travel "databases" so the demo works offline — no API key needed.
CITIES = {
    "paris": {
        "flights": "Air France 08:10 → $420 round trip (7h) | Budget Air 14:30 → $310 round trip (9h, 1 stop)",
        "hotels": "Hotel Lumière (4★) $180/night near Louvre | Hostel Seine (2★) $45/night in Le Marais",
        "activities": "Louvre Museum ($20) | Eiffel Tower summit ($30) | Seine evening cruise ($15) | Montmartre walk (free)",
    },
    "tokyo": {
        "flights": "JAL 11:00 → $950 round trip (13h) | ANA 22:15 → $880 round trip (14h, 1 stop)",
        "hotels": "Shinjuku Grand (4★) $150/night | Capsule Stay (2★) $40/night in Asakusa",
        "activities": "Senso-ji Temple (free) | teamLab Planets ($28) | Tsukiji food tour ($60) | Shibuya Crossing (free)",
    },
    "goa": {
        "flights": "IndiGo 06:20 → $120 round trip (2h) | Air India 18:40 → $150 round trip (2h)",
        "hotels": "Palm Beach Resort (4★) $90/night | Backpackers Nest (2★) $15/night",
        "activities": "Baga Beach (free) | Dudhsagar Falls trip ($25) | Old Goa churches (free) | Sunset cruise ($12)",
    },
    "new york": {
        "flights": "Delta 07:45 → $380 round trip (6h) | JetBlue 19:00 → $290 round trip (7h, 1 stop)",
        "hotels": "Midtown Plaza (4★) $220/night | Brooklyn Bunk (2★) $70/night",
        "activities": "Statue of Liberty ferry ($25) | Central Park (free) | Met Museum ($30) | Broadway show ($110)",
    },
}


def find_city(text: str):
    """Return the known city mentioned in the text, or None."""
    t = text.lower()
    return next((c for c in CITIES if c in t), None)


def _lookup(city: str, kind: str) -> str:
    data = CITIES.get(city.strip().lower())
    return data[kind] if data else f"No {kind} data for '{city}'. Known cities: {', '.join(CITIES)}."


@tool
def search_flights(city: str) -> str:
    """Find flight options to a city (e.g. Paris, Tokyo, Goa, New York)."""
    return _lookup(city, "flights")


@tool
def search_hotels(city: str) -> str:
    """Find hotel options in a city (e.g. Paris, Tokyo, Goa, New York)."""
    return _lookup(city, "hotels")


@tool
def search_activities(city: str) -> str:
    """Find things to do in a city (e.g. Paris, Tokyo, Goa, New York)."""
    return _lookup(city, "activities")
