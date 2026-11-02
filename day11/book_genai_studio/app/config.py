"""App settings. Everything can be changed with environment variables (or a .env file)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Vercel sets VERCEL=1. Its filesystem is read-only except /tmp, and /tmp is wiped
# whenever a new server instance starts, so we treat stored data as a cache there.
ON_VERCEL = bool(os.getenv("VERCEL"))
DATA_DIR = Path(os.getenv("DATA_DIR") or ("/tmp/book_studio" if ON_VERCEL else BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
ALLOWED_MODELS = [m.strip() for m in os.getenv(
    "ALLOWED_MODELS", "gpt-4o-mini,gpt-4o,gpt-4.1-mini,gpt-4.1").split(",") if m.strip()]

REQUEST_TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "2"))  # SDK retries 429/5xx with backoff

# Vercel rejects request bodies over 4.5 MB, so keep uploads under that there.
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "4" if ON_VERCEL else "25"))
MAX_BOOK_TOKENS = int(os.getenv("MAX_BOOK_TOKENS", "800000"))
DAILY_BUDGET_USD = float(os.getenv("DAILY_BUDGET_USD", "0"))  # 0 = no limit

# USD per 1M tokens: (input, output). Check https://openai.com/api/pricing and edit.
PRICES = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "text-embedding-3-small": (0.02, 0.0),
    "text-embedding-3-large": (0.13, 0.0),
}
