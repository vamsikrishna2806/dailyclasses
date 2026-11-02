"""Token counting and cost estimates.

Uses tiktoken (the same tokenizer OpenAI uses). If it's missing or can't load its
vocabulary file (no internet), falls back to the rule of thumb: 1 token ~ 4 characters.
"""
from . import config

try:
    import tiktoken
except ImportError:
    tiktoken = None

_encoders = {}
_tiktoken_broken = False


def _encoder(model: str):
    global _tiktoken_broken
    if tiktoken is None or _tiktoken_broken:
        return None
    if model not in _encoders:
        try:
            try:
                _encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                _encoders[model] = tiktoken.get_encoding("o200k_base")
        except Exception:
            _tiktoken_broken = True
            return None
    return _encoders[model]


def count_tokens(text: str, model: str | None = None) -> int:
    if not text:
        return 0
    enc = _encoder(model or config.CHAT_MODEL)
    if enc is not None:
        return len(enc.encode(text, disallowed_special=()))
    return max(1, len(text) // 4)


def count_messages(messages: list[dict], model: str | None = None) -> int:
    # ~4 extra tokens per message for role/formatting, +2 for the reply primer
    return sum(count_tokens(m.get("content") or "", model) + 4 for m in messages) + 2


def truncate(text: str, max_tokens: int, model: str | None = None) -> str:
    enc = _encoder(model or config.CHAT_MODEL)
    if enc is not None:
        ids = enc.encode(text, disallowed_special=())
        return text if len(ids) <= max_tokens else enc.decode(ids[:max_tokens])
    return text[: max_tokens * 4]


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int = 0) -> float:
    price_in, price_out = config.PRICES.get(model, config.PRICES["gpt-4o-mini"])
    return (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000


def tokenizer_name() -> str:
    return "tiktoken" if _encoder(config.CHAT_MODEL) is not None else "approx (chars/4)"
