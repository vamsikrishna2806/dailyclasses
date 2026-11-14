from langchain_core.tools import tool

# Fake "databases" so the demo works offline — no API key needed.
INVOICES = {
    "1001": "Invoice 1001: $49.00, paid on 2026-10-02.",
    "1002": "Invoice 1002: $120.00, OVERDUE since 2026-10-20.",
}

KNOWLEDGE_BASE = {
    "wifi": "Restart the router, wait 30 seconds, then reconnect. Still stuck? Forget the network and rejoin.",
    "password": "Click 'Forgot password' on the login page. A reset link is emailed within 2 minutes.",
    "crash": "Update the app to the latest version, then clear the cache in Settings > Storage.",
}


@tool
def lookup_invoice(invoice_id: str) -> str:
    """Look up an invoice by its number (e.g. 1001) and return amount and payment status."""
    return INVOICES.get(invoice_id.strip(), f"No invoice found with id '{invoice_id}'.")


@tool
def search_kb(keyword: str) -> str:
    """Search the tech-support knowledge base for a keyword like wifi, password or crash."""
    for key, answer in KNOWLEDGE_BASE.items():
        if key in keyword.lower():
            return answer
    return "No article found. Ask the customer for more details."
