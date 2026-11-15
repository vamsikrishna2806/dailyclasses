import re

from langchain_core.tools import tool

# Fake order "database" so the demo works offline — no API key needed.
ORDERS = {
    "5001": {"item": "Laptop stand", "status": "delivered", "total": 39.00, "note": "delivered 2026-11-02"},
    "5002": {"item": "Wireless mouse", "status": "shipped", "total": 25.00, "note": "in transit, arrives in 2 days"},
    "5003": {"item": "USB-C cable", "status": "refunded", "total": 12.00, "note": "already refunded on 2026-10-28"},
}

REFUND_LOG = []   # every approved refund is recorded here


@tool
def get_order_status(order_id: str) -> str:
    """Look up an order by its number (e.g. 5001) and return item, status and total."""
    o = ORDERS.get(order_id.strip())
    if not o:
        return f"No order found with id '{order_id}'."
    return f"Order {order_id}: {o['item']}, ${o['total']:.2f}, status = {o['status']} ({o['note']})."


@tool
def issue_refund(order_id: str) -> str:
    """Refund an order by its number. Only DELIVERED orders can be refunded."""
    o = ORDERS.get(order_id.strip())
    if not o:
        return f"Refund failed: no order '{order_id}'."
    if o["status"] != "delivered":
        return f"Refund refused: order {order_id} is '{o['status']}', only delivered orders can be refunded."
    o["status"] = "refunded"
    REFUND_LOG.append(order_id)
    return f"Refund approved: ${o['total']:.2f} for order {order_id} returns to the customer's card in 3-5 days."


def parse_handoff(text: str, default: str = "done"):
    """
    Split an agent reply into (message for the customer, who is next).
    The agent ends with a line like 'HANDOFF: refunds'. No valid line => `default`.
    """
    matches = re.findall(r"HANDOFF:\s*(orders|refunds|triage|done)", text, re.I)
    target = matches[-1].lower() if matches else default
    message = re.sub(r"HANDOFF:.*", "", text, flags=re.I).strip()
    return message, target
