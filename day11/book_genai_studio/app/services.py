"""The three features. Each one has a live path (OpenAI) and a Demo path (offline, no key)."""
import json
import random
import re
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import llm, prompts
from .books import split_sentences
from .llm import LLMError, Meter
from .retrieval import best_sentences, extractive_summary, keywords, search
from .tokens import count_tokens, truncate

SINGLE_CALL_LIMIT = 12000   # tokens we send in one summarize call
WINDOW = 6000               # piece size for map-reduce
DEMO_NOTE = "\n\n> **Demo mode** – made offline without AI. Add an OpenAI key in Settings for real AI output."


def _out_id():
    return uuid.uuid4().hex[:10]


def _windows(text: str, size: int = WINDOW) -> list[str]:
    """Split text into pieces of about `size` tokens, on paragraph breaks."""
    out, buf = [], []
    buf_tokens = 0
    for para in re.split(r"\n\s*\n", text):
        t = count_tokens(para)
        if buf and buf_tokens + t > size:
            out.append("\n\n".join(buf))
            buf, buf_tokens = [], 0
        buf.append(truncate(para, size))
        buf_tokens += min(t, size)
    if buf:
        out.append("\n\n".join(buf))
    return out


# ================================================================== SUMMARIZE

def _notes(text, title, part, key, model, meter) -> str:
    """Dense notes for one piece of a book (map step)."""
    if not key:
        return " ".join(extractive_summary(text, 6))
    pieces = _windows(text) if count_tokens(text) > SINGLE_CALL_LIMIT else [text]

    def one(i_piece):
        i, piece = i_piece
        label = part if len(pieces) == 1 else f"{part}, piece {i + 1}/{len(pieces)}"
        return llm.chat([{"role": "user", "content": prompts.NOTES_PROMPT.format(title=title, part=label, text=piece)}],
                        key=key, feature="summarize", meter=meter, model=model, temperature=0.2, max_tokens=500)

    with ThreadPoolExecutor(max_workers=4) as pool:
        return "\n\n".join(pool.map(one, enumerate(pieces)))


def summarize(*, text, title, scope, length, style, version, key, model, book=None, chapter=None, notes=None):
    """scope: text | chapter | notes (map step for one chapter) | combine (reduce step)."""
    meter = Meter()
    words = prompts.LENGTHS.get(length, 300)
    style_desc = prompts.STYLES.get(style, prompts.STYLES["bullets"])
    version = prompts.pick_version("summarize", version)
    p = prompts.SUMMARIZE[version]

    if scope == "notes":
        ch = book["chapters"][chapter]
        cache_key = f"notes:{chapter}"
        cached = (book.get("cache") or {}).get(cache_key) if key else None
        out = cached or _notes(text, title, ch["title"], key, model, meter)
        if key and not cached:
            book.setdefault("cache", {})[cache_key] = out
        return {"output": out, "cached": bool(cached), "usage": meter.to_dict(), "mode": "live" if key else "demo"}

    if scope == "combine":
        joined = "\n\n".join(f"## {n['title']}\n{n['notes']}" for n in notes)
        text = joined

    tokens_in = count_tokens(text)
    if not key:
        n = {"short": 4, "medium": 8, "detailed": 15}.get(length, 8)
        sents = extractive_summary(text, n)
        kw = ", ".join(keywords(text, 8))
        out = f"**Key ideas:** {kw}\n\n" + "\n".join(f"- {s}" for s in sents) + DEMO_NOTE
        return {"output": out, "output_id": _out_id(), "prompt_version": "demo", "usage": meter.to_dict(),
                "tokens_in": tokens_in, "mode": "demo"}

    if scope == "combine":
        msgs = [{"role": "system", "content": prompts.SUMMARIZE["v2"]["system"]},
                {"role": "user", "content": prompts.COMBINE_PROMPT.format(
                    title=title, words=words, style=style_desc, text=truncate(text, SINGLE_CALL_LIMIT * 2))}]
    else:
        if tokens_in > SINGLE_CALL_LIMIT:  # long chapter / long paste: map-reduce
            text = _notes(text, title, "this section", key, model, meter)
        msgs = [{"role": "system", "content": p["system"]},
                {"role": "user", "content": p["user"].format(words=words, style=style_desc, text=text)}]
    out = llm.chat(msgs, key=key, feature="summarize", meter=meter, model=model,
                   temperature=0.3, max_tokens=int(words * 2.2) + 200)
    return {"output": out, "output_id": _out_id(), "prompt_version": version, "usage": meter.to_dict(),
            "tokens_in": tokens_in, "mode": "live"}


# ================================================================== Q&A CHAT

def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _trim_history(messages: list[dict], budget: int = 3000) -> list[dict]:
    """Keep the newest messages that fit in the token budget."""
    kept, used = [], 0
    for m in reversed(messages):
        t = count_tokens(m["content"])
        if kept and used + t > budget:
            break
        kept.append({"role": m["role"], "content": truncate(m["content"], budget)})
        used += t
    return kept[::-1]


def _source_label(book, c):
    ch = book["chapters"][c["chapter"]]["title"]
    return f"{ch}" + (f", p. {c['page']}" if c.get("page") else "")


def chat_events(*, book, messages, chapter, version, key, model):
    """Generator of Server-Sent Events: meta -> delta* -> done (or error)."""
    meter = Meter()
    out_id = _out_id()
    try:
        history = _trim_history(messages)
        question = history[-1]["content"]
        if not book:
            if not key:
                yield _sse("meta", {"sources": [], "prompt_version": "demo", "output_id": out_id})
                msg = ("I'm in **Demo mode**, so I can only answer from an uploaded book. Upload a book and pick "
                       "it at the top, or add an OpenAI key in Settings to chat about anything.")
                yield _sse("delta", {"t": msg})
                yield _sse("done", {"usage": meter.to_dict(), "mode": "demo"})
                return
            yield _sse("meta", {"sources": [], "prompt_version": "general", "output_id": out_id})
            msgs = [{"role": "system", "content": prompts.GENERAL_CHAT_SYSTEM}] + history
            for piece in llm.chat_stream(msgs, key=key, feature="chat", meter=meter, model=model):
                yield _sse("delta", {"t": piece})
            yield _sse("done", {"usage": meter.to_dict(), "mode": "live"})
            return

        # 1. Follow-up questions ("what did she do next?") -> standalone search question
        search_q = question
        user_turns = [m for m in history if m["role"] == "user"]
        if key and len(user_turns) > 1:
            hist = "\n".join(f"{m['role']}: {m['content'][:400]}" for m in history[-6:-1])
            search_q = llm.chat([{"role": "user", "content": prompts.CONDENSE_PROMPT.format(history=hist, question=question)}],
                                key=key, feature="qa_rewrite", meter=meter, model=model, temperature=0, max_tokens=80).strip()

        # 2. Retrieve passages (keyword + semantic when available)
        qvec = None
        if key and book.get("embeddings"):
            qvec = llm.embed([search_q], key=key, feature="embeddings", meter=meter)[0]
        hits = search(book, search_q, k=6, chapter=chapter, query_vec=qvec)
        sources = [{"tag": f"S{i + 1}", "label": _source_label(book, c), "chapter": c["chapter"],
                    "page": c.get("page"), "text": c["text"][:1200]} for i, c in enumerate(hits)]
        version = prompts.pick_version("qa", version)
        yield _sse("meta", {"sources": sources, "prompt_version": version if key else "demo",
                            "output_id": out_id, "search_query": search_q})

        # 3. Answer
        if not key:
            if not hits:
                ans = "I couldn't find anything about that in the book. Try other words, like a character's name."
            else:
                sents = best_sentences([h["text"] for h in hits[:4]], search_q, 4)
                ans = "Here's what the book says:\n\n" + "\n".join(
                    f"- {s} [S{next((i + 1 for i, h in enumerate(hits) if s[:40] in h['text'].replace(chr(10), ' ')), 1)}]"
                    for s in sents) + DEMO_NOTE
            for w in re.findall(r"\S+\s*", ans):
                yield _sse("delta", {"t": w})
            yield _sse("done", {"usage": meter.to_dict(), "mode": "demo"})
            return

        context = "\n\n".join(f"[{s['tag']}] ({s['label']})\n{h['text']}" for s, h in zip(sources, hits)) \
            or "(no matching passages found)"
        system = prompts.QA[version]["system"].format(title=book["title"], context=context)
        msgs = [{"role": "system", "content": system}] + history
        for piece in llm.chat_stream(msgs, key=key, feature="qa", meter=meter, model=model, temperature=0.2):
            yield _sse("delta", {"t": piece})
        yield _sse("done", {"usage": meter.to_dict(), "mode": "live"})
    except LLMError as e:
        yield _sse("error", e.to_dict()["error"])
    except Exception as e:  # never leave the browser hanging
        yield _sse("error", {"code": "server_error", "message": str(e)[:200], "hint": "Try again."})


# ================================================================== CONTENT GENERATOR

def _material(book, chapter, topic, text, budget=9000) -> str:
    if text:
        return truncate(text, budget)
    if chapter is not None:
        ch = book["chapters"][chapter]
        return truncate(book["text"][ch["start"]:ch["end"]], budget)
    if topic:
        hits = search(book, topic, k=12)
        if hits:
            return "\n\n".join(h["text"] for h in hits)
    # whole book: evenly spaced passages from start to end
    chunks = book["chunks"]
    take = max(1, min(len(chunks), budget // 450))
    step = len(chunks) / take
    return "\n\n".join(chunks[int(i * step)]["text"] for i in range(take))


def _demo_content(kind: str, material: str) -> str:
    sents = extractive_summary(material, 15)
    kw = keywords(material, 20)
    if kind == "quiz":
        lines, n = ["## Quiz (fill in the blank)"], 0
        for s in sents:
            word = next((w for w in kw if re.search(rf"\b{re.escape(w)}\b", s, re.I)), None)
            if not word:
                continue
            n += 1
            options = random.sample([w for w in kw if w != word], k=min(3, len(kw) - 1)) + [word]
            random.shuffle(options)
            q = re.sub(rf"\b{re.escape(word)}\b", "_____", s, count=1, flags=re.I)
            lines.append(f"**{n}. {q}**\n" + "\n".join(f"- {chr(65 + i)}) {o}" for i, o in enumerate(options))
                         + f"\n\n*Answer: {word}*\n")
            if n == 8:
                break
        return "\n".join(lines)
    if kind == "flashcards":
        rows, used = ["| Front | Back |", "|---|---|"], set()
        for s in sents[:12]:
            word = next((w for w in kw if w not in used and re.search(rf"\b{re.escape(w)}\b", s, re.I)), None)
            if word:
                used.add(word)
                rows.append(f"| What does the text say about **{word}**? | {s.replace('|', '/')} |")
        return "\n".join(rows)
    if kind == "timeline":
        return "| # | Event |\n|---|---|\n" + "\n".join(f"| {i + 1} | {s.replace('|', '/')} |" for i, s in enumerate(sents[:10]))
    return (f"## Key themes\n{', '.join(kw[:10])}\n\n## Main points\n" + "\n".join(f"- {s}" for s in sents[:10]))


def generate(*, book, chapter, topic, text, content_type, tone, audience, extra, version, key, model):
    meter = Meter()
    if not text and not book:
        if not topic:
            raise LLMError(400, "no_input", "Pick a book, paste text, or type a topic.")
        if not key:
            raise LLMError(400, "needs_key", "Demo mode can only create content from a book or pasted text.",
                           "Upload a book, paste text, or add an OpenAI key in Settings.")
    material = _material(book, chapter, topic, text) if (book or text) else f"Topic: {topic}"
    title = book["title"] if book else "the provided material"
    if not key:
        out = _demo_content(content_type, material) + DEMO_NOTE
        return {"output": out, "output_id": _out_id(), "prompt_version": "demo", "usage": meter.to_dict(),
                "tokens_in": count_tokens(material), "mode": "demo"}
    version = prompts.pick_version("generate", version)
    p = prompts.GENERATE[version]
    spec = prompts.CONTENT_TYPES.get(content_type, prompts.CONTENT_TYPES["custom"])
    if topic and (book or text):
        extra = f"Focus on: {topic}. {extra}".strip()
    user = p["user"].format(spec=spec, tone=tone or "clear and friendly", audience=audience or "general readers",
                            extra=extra or "none", material=material, title=title)
    out = llm.chat([{"role": "system", "content": p["system"]}, {"role": "user", "content": user}],
                   key=key, feature="generate", meter=meter, model=model, temperature=0.7, max_tokens=2000)
    return {"output": out, "output_id": _out_id(), "prompt_version": version, "usage": meter.to_dict(),
            "tokens_in": count_tokens(material), "mode": "live"}


def embed_book(book, key) -> dict:
    meter = Meter()
    book["embeddings"] = llm.embed([c["text"] for c in book["chunks"]], key=key, meter=meter)
    return meter.to_dict()


def first_sentences(text, n=2):
    return " ".join(split_sentences(text)[:n])
