import re

# A tiny made-up company handbook (so the demo works offline and answers are checkable).
DOCS = [
    {"id": "HR-1", "title": "Vacation policy", "text": "Every employee gets 24 paid vacation days per year. Requests must be made 2 weeks in advance through the HR portal. Up to 5 unused days carry over to the next year."},
    {"id": "HR-2", "title": "Sick leave", "text": "Employees get 10 paid sick days per year. Tell your manager before 9am on the first day. A doctor's note is needed after 3 days in a row."},
    {"id": "HR-3", "title": "Remote work", "text": "Employees may work from home up to 3 days per week. Tuesday and Thursday are office days for team meetings. Fully remote work needs director approval."},
    {"id": "FIN-1", "title": "Expense claims", "text": "Submit expense receipts within 30 days in the Finance app. Meals while travelling are reimbursed up to $40 per day. Flights must be booked through the company travel desk."},
    {"id": "IT-1", "title": "Laptops", "text": "New employees receive a laptop on day one. Laptops are replaced every 3 years. Report a lost or stolen laptop to IT security within 24 hours."},
    {"id": "IT-2", "title": "Passwords and security", "text": "Passwords must have at least 12 characters and be changed every 90 days. Two-factor authentication is mandatory for email and the VPN."},
    {"id": "OPS-1", "title": "Office hours", "text": "The office is open Monday to Friday, 8am to 7pm. Core meeting hours are 10am to 4pm. The cafeteria serves lunch from 12pm to 2pm."},
    {"id": "HR-4", "title": "Training budget", "text": "Each employee has a yearly training budget of $1,200 for courses, books and conferences. Get your manager's approval before you buy."},
]

STOPWORDS = set("a an the is are do does how many much what when where who can i my me we our of to in on for and or it be at by with you your get".split())


def keywords(text: str) -> list:
    words = re.findall(r"[a-z0-9']+", text.lower())
    # tiny "stemmer": passwords -> password, days -> day (so singular and plural words match)
    words = [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words]
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def search_docs(query: str, k: int = 2) -> list:
    """
    Very simple search: score each document by how many query keywords it contains.
    (A real system would use embeddings + a vector store, as you learned on day 12.)
    """
    terms = set(keywords(query))
    scored = []
    for doc in DOCS:
        words = set(keywords(doc["title"] + " " + doc["text"]))
        score = len(terms & words)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda p: -p[0])
    if not scored:
        return []
    best = scored[0][0]
    # keep only passages that are nearly as relevant as the best one (drops weak matches)
    return [doc for score, doc in scored[:k] if score >= max(1, 0.6 * best)]


def format_context(docs: list) -> str:
    return "\n".join(f"[{d['id']}] {d['title']}: {d['text']}" for d in docs)
