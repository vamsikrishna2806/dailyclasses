# 📚 Book GenAI Studio — Day 9: Build Your First GenAI App

Upload **any book** (PDF, EPUB, DOCX, TXT, MD, HTML) and:

| Feature | What it does |
|---|---|
| 📝 **Summarizer** | Whole book (chapter by chapter, with a progress bar), one chapter, or pasted text. 6 styles × 3 lengths. Long text is split and combined automatically (map-reduce). |
| 💬 **Ask the book** | Multi-turn chat that streams answers word by word, cites passages (`[S1]`, with chapter and page), rewrites follow-up questions, and can search one chapter or the whole book. Chats are saved in the browser. |
| ✨ **Content generator** | Quiz, flashcards, study notes, blog post, social thread, newsletter, book-club questions, character profiles, timeline, lesson plan, or custom — from the book, a chapter, a topic, pasted text, or a free topic. |
| 🧪 **Prompt Lab** | Every output records its prompt version (v1/v2). Star ratings per version, blind A/B compare, CSV export — so you can improve prompts with evidence. |
| 📊 **Usage** | Tokens, cost, response time and errors per call, per feature and per day. Live token counter and cost estimate before you run anything. Optional daily spending limit. |

Also: 📋 copy-to-clipboard and ⬇ Markdown download on every output, friendly error messages with fixes, light/dark theme, and a **Demo mode** that works without an API key (simple offline algorithms), so you can try everything for free first.

**Full step-by-step guide (build + free Vercel deploy):** open [`../IMPLEMENTATION_GUIDE.html`](../IMPLEMENTATION_GUIDE.html) in a browser.

## Run locally

```bash
cd book_genai_studio
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Mac/Linux: cp .env.example .env   — then add your key (optional)
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — click **Try the sample book**. API docs: http://127.0.0.1:8000/docs

No key? It runs in Demo mode. Add a key in `.env` or in the app's ⚙️ Settings.

## Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

14 tests: chapter detection, bad files, Vercel book recovery, all three features in Demo mode, and the AI path with a fake OpenAI (no money spent): follow-up rewriting, map-reduce, A/B compare, error mapping.

## Deploy free on Vercel (short version)

1. Push this repo to GitHub.
2. vercel.com → **Add New → Project** → import the repo → **Root Directory:** `day9/book_genai_studio`.
3. Environment variables: `DAILY_BUDGET_USD=1`, `MAX_UPLOAD_MB=4`, and **optionally** `OPENAI_API_KEY` (see warning).
4. Deploy. Open the URL.

> ⚠️ If you put your own key on a public URL, **anyone** with the link spends your money. Safer: leave `OPENAI_API_KEY` empty so each visitor pastes their own key in Settings, or keep `DAILY_BUDGET_USD` low.

How the app handles Vercel's free-plan limits:

| Limit | What the app does |
|---|---|
| Request body ≤ 4.5 MB | Upload limit set to 4 MB on Vercel, checked in the browser before sending. |
| Each function call has a time limit | Whole-book summaries run one chapter per request from the browser (3 at a time), never one giant request. |
| `/tmp` storage is wiped on restart, and instances don't share it | The browser keeps every processed book in IndexedDB. If the server answers `book_not_found`, the browser re-sends it and retries — automatically. |
| Usage/feedback DB is lost on restart | The browser keeps its own usage and feedback log; feedback exports to CSV. |

## Heroku / Render

`Procfile` and `.python-version` are included. Heroku has no free plan any more (Eco dynos ~US$5/month): `heroku create`, `heroku config:set OPENAI_API_KEY=...`, `git subtree push --prefix day9/book_genai_studio heroku main`. Render.com has a free web service: build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Project layout

```
book_genai_studio/
├─ app/
│  ├─ main.py        FastAPI routes + error handlers
│  ├─ config.py      settings from env vars, prices
│  ├─ books.py       read files → clean text → chapters → chunks; book store
│  ├─ retrieval.py   BM25 keyword search + embeddings, fused (RRF); offline helpers
│  ├─ services.py    summarize (map-reduce), chat (RAG + SSE streaming), generate
│  ├─ prompts.py     all prompts, versioned v1/v2 for A/B tests
│  ├─ llm.py         OpenAI calls: retries, friendly errors, token + cost logging
│  ├─ tokens.py      tiktoken counting, cost estimate
│  └─ db.py          SQLite: usage + feedback
├─ static/           index.html, style.css, app.js (no build step)
├─ api/index.py      Vercel entry point
├─ tests/            pytest suite
├─ samples/          original sample book
├─ vercel.json  Procfile  .python-version  requirements.txt  .env.example
└─ EVALUATION.md     user-testing plan + prompt iteration log
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | mode (live/demo), models, limits, prices |
| POST | `/api/books` | upload a file (multipart `file`) |
| POST | `/api/books/restore` | re-send a processed book (used automatically) |
| GET/DELETE | `/api/books/{id}` | book info / delete |
| GET | `/api/books/{id}/chapters/{i}` | chapter text preview |
| POST | `/api/summarize` | `scope`: `text` · `chapter` · `notes` · `combine` |
| POST | `/api/chat` | streaming SSE: `meta` → `delta`… → `done` / `error` |
| POST | `/api/generate` | content generator |
| POST | `/api/compare` | run prompt v1 and v2 on the same input |
| POST | `/api/tokens` | count tokens + estimate cost |
| GET/DELETE | `/api/usage` | usage dashboard data |
| POST/GET | `/api/feedback` | save rating / ratings per prompt version |

Prices in `app/config.py` are estimates — check https://openai.com/api/pricing and update them.
