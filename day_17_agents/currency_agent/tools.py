import requests
from langchain_core.tools import tool


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount between any two currencies using live exchange rates.
    Example: amount=100, from_currency='USD', to_currency='INR'.
    Uses Frankfurter.app — free, no API key, updated daily.
    """
    frm = from_currency.upper().strip()
    to = to_currency.upper().strip()

    r = requests.get(
        "https://api.frankfurter.app/latest",
        params={"from": frm, "to": to},
        timeout=10
    )
    data = r.json()

    if "rates" not in data:
        return f"Could not get exchange rate for {frm} → {to}. Check the currency codes."

    rate = data["rates"][to]
    converted = amount * rate

    return (
        f"{amount:,.2f} {frm} = {converted:,.2f} {to}\n"
        f"Exchange rate : 1 {frm} = {rate} {to}\n"
        f"Rate date     : {data.get('date', 'N/A')}"
    )
