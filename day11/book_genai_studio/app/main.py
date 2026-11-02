"""Book GenAI Studio – FastAPI backend.

Run locally:   uvicorn app.main:app --reload      then open http://127.0.0.1:8000
API docs:      http://127.0.0.1:8000/docs
"""
from typing import Literal

from fastapi import FastAPI, File, Header, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import books, config, db, llm, prompts, services
from .books import BookError, store
from .llm import LLMError
from .tokens import count_tokens, estimate_cost, tokenizer_name

app = FastAPI(title="Book GenAI Studio", version="1.0",
              description="Upload a book, then summarize it, chat with it and create content from it.")
db.init()
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


# ------------------------------------------------------------------ errors → friendly JSON

@app.exception_handler(LLMError)
@app.exception_handler(BookError)
async def known_error(_: Request, e):
    return JSONResponse(e.to_dict(), status_code=e.status)


@app.exception_handler(Exception)
async def unknown_error(_: Request, e: Exception):
    return JSONResponse({"error": {"code": "server_error", "message": "Something went wrong on the server.",
                                   "hint": str(e)[:200]}}, status_code=500)


# ------------------------------------------------------------------ request models

Feature = Literal["summarize", "qa", "generate", "chat"]


class SummarizeIn(BaseModel):
    book_id: str | None = None
    text: str | None = Field(None, max_length=400_000)
    scope: Literal["text", "chapter", "notes", "combine"] = "text"
    chapter: int | None = None
    notes: list[dict] | None = None  # for scope=combine: [{title, notes}]
    length: Literal["short", "medium", "detailed"] = "medium"
    style: str = "bullets"
    prompt_version: str = "auto"
    model: str | None = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=20_000)


class ChatIn(BaseModel):
    book_id: str | None = None
    chapter: int | None = None
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=60)
    prompt_version: str = "auto"
    model: str | None = None


class GenerateIn(BaseModel):
    book_id: str | None = None
    chapter: int | None = None
    topic: str | None = Field(None, max_length=500)
    text: str | None = Field(None, max_length=200_000)
    content_type: str = "study_notes"
    tone: str = "clear and friendly"
    audience: str = "general readers"
    extra: str = Field("", max_length=1000)
    prompt_version: str = "auto"
    model: str | None = None


class CompareIn(BaseModel):
    feature: Literal["summarize", "generate"]
    summarize: SummarizeIn | None = None
    generate: GenerateIn | None = None


class TokensIn(BaseModel):
    text: str = Field("", max_length=2_000_000)
    model: str | None = None
    expected_output_tokens: int = 500


class FeedbackIn(BaseModel):
    feature: Feature
    prompt_version: str | None = None
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=2000)
    output_id: str | None = None
    output_excerpt: str = ""


# ------------------------------------------------------------------ helpers

def _book(book_id):
    return store.get(book_id) if book_id else None


def _chapter_text(book, idx):
    if idx is None or not (0 <= idx < len(book["chapters"])):
        raise BookError(400, "bad_chapter", "That chapter doesn't exist.")
    ch = book["chapters"][idx]
    return book["text"][ch["start"]:ch["end"]]


# ------------------------------------------------------------------ pages

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/api/health")
def health(x_openai_key: str | None = Header(None)):
    key = llm.resolve_key(x_openai_key)
    return {"ok": True, "mode": "live" if key else "demo", "server_key": bool(config.OPENAI_API_KEY),
            "model": config.CHAT_MODEL, "models": config.ALLOWED_MODELS, "tokenizer": tokenizer_name(),
            "max_upload_mb": config.MAX_UPLOAD_MB, "on_vercel": config.ON_VERCEL, "prices": config.PRICES}


@app.get("/api/sample", include_in_schema=False)
def sample_book():
    return FileResponse(config.BASE_DIR / "samples" / "the_lighthouse_apprentice.txt", media_type="text/plain")


@app.get("/api/prompts")
def prompt_catalog():
    return prompts.catalog()


# ------------------------------------------------------------------ books

@app.post("/api/books")
async def upload_book(file: UploadFile = File(...), x_openai_key: str | None = Header(None)):
    data = await file.read()
    book = await run_in_threadpool(books.build, file.filename or "book.txt", data)
    key = llm.resolve_key(x_openai_key)
    warning, usage = None, None
    if key:
        try:
            usage = await run_in_threadpool(services.embed_book, book, key)
        except LLMError as e:
            warning = f"Semantic search is off ({e.message}). Keyword search still works."
    store.save(book)
    return {"book": books.public(book), "portable": books.portable(book), "warning": warning, "usage": usage}


@app.post("/api/books/restore")
def restore_book(payload: dict):
    """The browser re-sends a book this server instance forgot (common on Vercel)."""
    need = {"id", "title", "text", "chapters", "chunks"}
    if not need <= payload.keys():
        raise BookError(400, "bad_restore", "Book data is incomplete.")
    book = {**payload, "embeddings": None, "cache": {}}
    book.setdefault("created", 0)
    for k in ("filename", "pages", "words", "tokens"):
        book.setdefault(k, None)
    store.save(book)
    return {"book": books.public(book)}


@app.get("/api/books")
def list_books():
    return [books.public(b) for b in store.all()]


@app.get("/api/books/{book_id}")
def get_book(book_id: str):
    return books.public(store.get(book_id))


@app.get("/api/books/{book_id}/chapters/{idx}")
def get_chapter(book_id: str, idx: int):
    book = store.get(book_id)
    text = _chapter_text(book, idx)
    return {"idx": idx, "title": book["chapters"][idx]["title"], "text": text[:20000],
            "truncated": len(text) > 20000}


@app.delete("/api/books/{book_id}")
def delete_book(book_id: str):
    store.delete(book_id)
    return {"deleted": book_id}


# ------------------------------------------------------------------ features

@app.post("/api/summarize")
async def summarize(body: SummarizeIn, x_openai_key: str | None = Header(None)):
    key = llm.resolve_key(x_openai_key)
    book = _book(body.book_id)
    text, title = body.text or "", "the text"
    if book:
        title = book["title"]
        if body.scope in ("chapter", "notes"):
            text = _chapter_text(book, body.chapter)
    if body.scope == "combine" and not body.notes:
        raise BookError(400, "no_notes", "Nothing to combine.")
    if body.scope in ("chapter", "notes") and not book:
        raise BookError(400, "no_book", "Pick a book first.")
    if body.scope == "text" and len(text.split()) < 20:
        raise BookError(400, "too_short", "Paste at least a few sentences (20+ words) to summarize.")
    result = await run_in_threadpool(
        services.summarize, text=text, title=title, scope=body.scope, length=body.length, style=body.style,
        version=body.prompt_version, key=key, model=body.model, book=book, chapter=body.chapter, notes=body.notes)
    if book and body.scope == "notes" and key:
        store.save(book)  # keep cached notes
    return result


@app.post("/api/chat")
def chat(body: ChatIn, x_openai_key: str | None = Header(None)):
    if body.messages[-1].role != "user":
        raise BookError(400, "bad_messages", "The last message must be from the user.")
    book = _book(body.book_id)  # raises book_not_found before the stream starts
    events = services.chat_events(book=book, messages=[m.model_dump() for m in body.messages],
                                  chapter=body.chapter, version=body.prompt_version,
                                  key=llm.resolve_key(x_openai_key), model=body.model)
    return StreamingResponse(events, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/generate")
async def generate(body: GenerateIn, x_openai_key: str | None = Header(None)):
    book = _book(body.book_id)
    if body.chapter is not None and book:
        _chapter_text(book, body.chapter)  # validate
    return await run_in_threadpool(
        services.generate, book=book, chapter=body.chapter, topic=body.topic, text=body.text,
        content_type=body.content_type, tone=body.tone, audience=body.audience, extra=body.extra,
        version=body.prompt_version, key=llm.resolve_key(x_openai_key), model=body.model)


@app.post("/api/compare")
async def compare(body: CompareIn, x_openai_key: str | None = Header(None)):
    """Run the same input through prompt v1 and v2 so a person can pick the better one."""
    results = {}
    for v in ("v1", "v2"):
        if body.feature == "summarize" and body.summarize:
            req = body.summarize.model_copy(update={"prompt_version": v, "scope": "text" if body.summarize.text else body.summarize.scope})
            results[v] = await summarize(req, x_openai_key)
        elif body.feature == "generate" and body.generate:
            results[v] = await generate(body.generate.model_copy(update={"prompt_version": v}), x_openai_key)
        else:
            raise BookError(400, "bad_compare", "Send the matching request body.")
    return results


# ------------------------------------------------------------------ tokens, usage, feedback

@app.post("/api/tokens")
def tokens(body: TokensIn):
    model = llm.resolve_model(body.model)
    n = count_tokens(body.text, model)
    return {"tokens": n, "words": len(body.text.split()), "chars": len(body.text), "model": model,
            "tokenizer": tokenizer_name(),
            "estimated_cost_usd": round(estimate_cost(model, n, body.expected_output_tokens), 6),
            "fits_in_one_call": n <= services.SINGLE_CALL_LIMIT}


@app.get("/api/usage")
def usage():
    return db.usage_summary()


@app.delete("/api/usage")
def clear_usage():
    db.clear_usage()
    return {"cleared": True}


@app.post("/api/feedback")
def feedback(body: FeedbackIn):
    db.add_feedback(body.feature, body.prompt_version, body.rating, body.comment, body.output_id, body.output_excerpt)
    return {"saved": True}


@app.get("/api/feedback")
def feedback_stats():
    return db.feedback_summary()
