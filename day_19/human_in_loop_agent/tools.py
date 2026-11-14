from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

OUTBOX = Path(__file__).parent / "outbox.txt"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    'Send' an email. For this demo it appends the email to outbox.txt
    (a real app would call SMTP / Gmail API here). This is the RISKY action
    that a human must approve first.
    """
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] To: {to}\nSubject: {subject}\n{body}\n{'-' * 40}\n")
    return f"Email to {to} saved in {OUTBOX.name}"
