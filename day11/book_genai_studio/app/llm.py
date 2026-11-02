"""One place for every OpenAI call: retries, friendly errors, token + cost logging."""
import time

import openai
from openai import OpenAI

from . import config, db
from .tokens import count_messages, count_tokens, estimate_cost


class LLMError(Exception):
    """An error with a status code, a short code, and a hint the UI can show."""

    def __init__(self, status: int, code: str, message: str, hint: str = ""):
        super().__init__(message)
        self.status, self.code, self.message, self.hint = status, code, message, hint

    def to_dict(self):
        return {"error": {"code": self.code, "message": self.message, "hint": self.hint}}


class Meter:
    """Adds up tokens and cost across the calls made for one user request."""

    def __init__(self):
        self.prompt_tokens = self.completion_tokens = self.calls = 0
        self.cost = 0.0
        self.started = time.time()

    def add(self, pt, ct, cost):
        self.prompt_tokens += pt
        self.completion_tokens += ct
        self.cost += cost
        self.calls += 1

    def to_dict(self):
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
            "cost_usd": round(self.cost, 6),
            "calls": self.calls,
            "latency_ms": int((time.time() - self.started) * 1000),
        }


def resolve_key(header_key: str | None) -> str:
    """A key typed in the UI (sent as X-OpenAI-Key) wins over the server's key."""
    return (header_key or "").strip() or config.OPENAI_API_KEY


def resolve_model(requested: str | None) -> str:
    if requested and requested in config.ALLOWED_MODELS:
        return requested
    return config.CHAT_MODEL


def map_error(e: Exception) -> LLMError:
    msg = str(e)
    if isinstance(e, openai.AuthenticationError):
        return LLMError(401, "invalid_api_key", "OpenAI rejected the API key.",
                        "Open Settings and paste a valid key (starts with sk-).")
    if isinstance(e, openai.PermissionDeniedError):
        return LLMError(403, "permission_denied", "This key can't use that model.",
                        "Pick another model in Settings.")
    if isinstance(e, openai.RateLimitError):
        if "insufficient_quota" in msg or "quota" in msg.lower():
            return LLMError(402, "quota_exceeded", "Your OpenAI account is out of credit.",
                            "Add billing at platform.openai.com, or keep using Demo mode.")
        return LLMError(429, "rate_limited", "Too many requests to OpenAI right now.",
                        "Wait a few seconds and try again.")
    if isinstance(e, openai.BadRequestError):
        if "context_length" in msg or "maximum context" in msg:
            return LLMError(400, "context_too_long", "The text is too long for the model.",
                            "Pick one chapter, or paste a shorter piece.")
        return LLMError(400, "bad_request", f"OpenAI said the request was invalid: {msg[:200]}")
    if isinstance(e, openai.NotFoundError):
        return LLMError(404, "model_not_found", "That model doesn't exist for this key.",
                        "Choose another model in Settings or set OPENAI_MODEL.")
    if isinstance(e, openai.APITimeoutError):
        return LLMError(504, "timeout", "OpenAI took too long to answer.", "Try again, or use shorter input.")
    if isinstance(e, openai.APIConnectionError):
        return LLMError(503, "network", "Couldn't reach OpenAI.", "Check the internet connection.")
    if isinstance(e, openai.APIStatusError):
        return LLMError(502, "upstream_error", "OpenAI had a server error.", "Try again in a moment.")
    return LLMError(500, "llm_error", f"Unexpected error: {msg[:200]}")


def _check_budget():
    if config.DAILY_BUDGET_USD > 0 and db.cost_today() >= config.DAILY_BUDGET_USD:
        raise LLMError(429, "budget_exceeded",
                       f"Today's spending limit (${config.DAILY_BUDGET_USD:.2f}) is reached.",
                       "Raise DAILY_BUDGET_USD or wait until tomorrow.")


def _client(key: str) -> OpenAI:
    return OpenAI(api_key=key, timeout=config.REQUEST_TIMEOUT, max_retries=config.MAX_RETRIES)


def _create(client, **kwargs):
    """Some newer models reject custom temperature; retry once without it."""
    try:
        return client.chat.completions.create(**kwargs)
    except openai.BadRequestError as e:
        if "temperature" in str(e) and "temperature" in kwargs:
            kwargs.pop("temperature")
            return client.chat.completions.create(**kwargs)
        raise


def chat(messages, *, key, feature, meter=None, model=None, temperature=0.4, max_tokens=1200) -> str:
    _check_budget()
    model = resolve_model(model)
    t0 = time.time()
    try:
        r = _create(_client(key), model=model, messages=messages,
                    temperature=temperature, max_completion_tokens=max_tokens)
    except openai.OpenAIError as e:
        err = map_error(e)
        db.log_usage(feature, model, 0, 0, 0, int((time.time() - t0) * 1000), ok=False, error=err.code)
        raise err from e
    text = r.choices[0].message.content or ""
    pt = r.usage.prompt_tokens if r.usage else count_messages(messages, model)
    ct = r.usage.completion_tokens if r.usage else count_tokens(text, model)
    cost = estimate_cost(model, pt, ct)
    db.log_usage(feature, model, pt, ct, cost, int((time.time() - t0) * 1000))
    if meter:
        meter.add(pt, ct, cost)
    if r.choices[0].finish_reason == "length":
        text += "\n\n_(Stopped at the length limit. Ask for a shorter output or say “continue”.)_"
    return text


def chat_stream(messages, *, key, feature, meter=None, model=None, temperature=0.4, max_tokens=1200):
    """Yields text pieces as they arrive. Logs usage at the end."""
    _check_budget()
    model = resolve_model(model)
    t0 = time.time()
    parts, usage = [], None
    try:
        stream = _create(_client(key), model=model, messages=messages, temperature=temperature,
                         max_completion_tokens=max_tokens, stream=True,
                         stream_options={"include_usage": True})
        for chunk in stream:
            if chunk.usage:
                usage = chunk.usage
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                piece = chunk.choices[0].delta.content
                parts.append(piece)
                yield piece
    except openai.OpenAIError as e:
        err = map_error(e)
        db.log_usage(feature, model, 0, 0, 0, int((time.time() - t0) * 1000), ok=False, error=err.code)
        raise err from e
    text = "".join(parts)
    pt = usage.prompt_tokens if usage else count_messages(messages, model)
    ct = usage.completion_tokens if usage else count_tokens(text, model)
    cost = estimate_cost(model, pt, ct)
    db.log_usage(feature, model, pt, ct, cost, int((time.time() - t0) * 1000))
    if meter:
        meter.add(pt, ct, cost)


def embed(texts: list[str], *, key, feature="embeddings", meter=None) -> list[list[float]]:
    _check_budget()
    model = config.EMBED_MODEL
    out = []
    client = _client(key)
    for i in range(0, len(texts), 96):
        batch = texts[i:i + 96]
        t0 = time.time()
        try:
            r = client.embeddings.create(model=model, input=batch)
        except openai.OpenAIError as e:
            err = map_error(e)
            db.log_usage(feature, model, 0, 0, 0, int((time.time() - t0) * 1000), ok=False, error=err.code)
            raise err from e
        out.extend(d.embedding for d in r.data)
        pt = r.usage.prompt_tokens if r.usage else sum(count_tokens(t) for t in batch)
        cost = estimate_cost(model, pt)
        db.log_usage(feature, model, pt, 0, cost, int((time.time() - t0) * 1000))
        if meter:
            meter.add(pt, 0, cost)
    return out
