"""Run with:  pytest -q
Uses a temporary data folder, Demo mode, and a fake OpenAI for the "live" tests (no money spent)."""
import io
import json
import os
import tempfile
from pathlib import Path

os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["OPENAI_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import llm, main, services  # noqa: E402
from app.books import split_chapters  # noqa: E402

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "the_lighthouse_apprentice.txt"
client = TestClient(main.app)


def upload(name="book.txt", data=None):
    data = data if data is not None else SAMPLE.read_bytes()
    return client.post("/api/books", files={"file": (name, io.BytesIO(data), "text/plain")})


def sse(text):
    events = []
    for block in text.strip().split("\n\n"):
        ev = next(line[7:] for line in block.splitlines() if line.startswith("event: "))
        data = json.loads(next(line[6:] for line in block.splitlines() if line.startswith("data: ")))
        events.append((ev, data))
    return events


@pytest.fixture(scope="module")
def book():
    r = upload("the_lighthouse_apprentice.txt")
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------- books
def test_chapters_detected(book):
    titles = [c["title"] for c in book["book"]["chapters"]]
    assert titles == ["Chapter 1: The Letter", "Chapter 2: Harrow Point", "Chapter 3: The Logbook",
                      "Chapter 4: The Storm", "Chapter 5: The New Keeper"]


def test_unsupported_and_empty_files():
    assert upload("virus.exe", b"abc").json()["error"]["code"] == "unsupported_type"
    assert upload("empty.txt", b"").json()["error"]["code"] == "empty_file"
    assert upload("tiny.txt", b"hello there").json()["error"]["code"] == "no_text"


def test_no_headings_makes_parts():
    text = ("This is a sentence about nothing in particular. " * 2000)
    parts = split_chapters(text)
    assert len(parts) > 1 and parts[0]["title"] == "Part 1"


def test_restore_after_server_forgets(book):
    bid = book["book"]["id"]
    main.store.delete(bid)
    assert client.get(f"/api/books/{bid}").json()["error"]["code"] == "book_not_found"
    assert client.post("/api/books/restore", json=book["portable"]).status_code == 200
    assert client.get(f"/api/books/{bid}").status_code == 200


# ---------------------------------------------------------------- demo mode features
def test_demo_summarize_chapter(book):
    r = client.post("/api/summarize", json={"book_id": book["book"]["id"], "scope": "chapter", "chapter": 3})
    assert r.status_code == 200 and r.json()["mode"] == "demo" and "Demo mode" in r.json()["output"]


def test_summarize_needs_enough_text():
    assert client.post("/api/summarize", json={"text": "too short"}).json()["error"]["code"] == "too_short"


def test_demo_chat_cites_sources(book):
    r = client.post("/api/chat", json={"book_id": book["book"]["id"],
                                       "messages": [{"role": "user", "content": "Who signed the logbook A.O.?"}]})
    events = sse(r.text)
    meta = events[0][1]
    assert events[0][0] == "meta" and meta["sources"]
    assert "Logbook" in meta["sources"][0]["label"]
    assert events[-1][0] == "done"


def test_demo_generate_quiz(book):
    r = client.post("/api/generate", json={"book_id": book["book"]["id"], "content_type": "quiz"})
    assert r.status_code == 200 and "Answer:" in r.json()["output"]


def test_tokens_and_validation():
    r = client.post("/api/tokens", json={"text": "hello world"}).json()
    assert r["tokens"] >= 2 and r["estimated_cost_usd"] >= 0
    assert client.post("/api/feedback", json={"feature": "qa", "rating": 9}).status_code == 422


def test_feedback_stats():
    client.post("/api/feedback", json={"feature": "summarize", "prompt_version": "v1", "rating": 2})
    client.post("/api/feedback", json={"feature": "summarize", "prompt_version": "v2", "rating": 5})
    rows = {r["prompt_version"]: r for r in client.get("/api/feedback").json()["by_version"] if r["feature"] == "summarize"}
    assert rows["v2"]["avg_rating"] > rows["v1"]["avg_rating"]


# ---------------------------------------------------------------- "live" mode with a fake OpenAI
@pytest.fixture
def fake_openai(monkeypatch):
    calls = []

    def fake_chat(messages, *, key, feature, meter=None, model=None, **kw):
        calls.append((feature, messages))
        if meter:
            meter.add(100, 20, 0.0001)
        return f"FAKE {feature} answer [S1]"

    def fake_stream(messages, *, key, feature, meter=None, model=None, **kw):
        calls.append((feature, messages))
        if meter:
            meter.add(100, 20, 0.0001)
        yield "The answer "
        yield "is Adaeze [S1]."

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(llm, "chat_stream", fake_stream)
    return calls


def test_live_followup_question_is_rewritten(book, fake_openai):
    msgs = [{"role": "user", "content": "Who is Elias?"}, {"role": "assistant", "content": "The keeper."},
            {"role": "user", "content": "What did he promise?"}]
    r = client.post("/api/chat", json={"book_id": book["book"]["id"], "messages": msgs},
                    headers={"X-OpenAI-Key": "sk-test"})
    events = sse(r.text)
    assert [f for f, _ in fake_openai] == ["qa_rewrite", "qa"]
    text = "".join(d["t"] for e, d in events if e == "delta")
    assert text == "The answer is Adaeze [S1]."
    assert events[-1][1]["usage"]["calls"] == 2


def test_live_compare_runs_both_versions(book, fake_openai):
    r = client.post("/api/compare", headers={"X-OpenAI-Key": "sk-test"}, json={
        "feature": "summarize", "summarize": {"book_id": book["book"]["id"], "scope": "chapter", "chapter": 0}})
    j = r.json()
    assert j["v1"]["prompt_version"] == "v1" and j["v2"]["prompt_version"] == "v2"


def test_long_text_uses_map_reduce(fake_openai):
    long_text = "\n\n".join(f"Paragraph {i}. " + "The keeper climbed the stairs again. " * 60 for i in range(150))
    r = client.post("/api/summarize", json={"text": long_text}, headers={"X-OpenAI-Key": "sk-test"})
    assert r.status_code == 200
    assert len(fake_openai) > 2  # several note calls + one final call


def test_openai_errors_become_friendly(book, monkeypatch):
    def boom(*a, **k):
        raise llm.LLMError(401, "invalid_api_key", "OpenAI rejected the API key.", "Open Settings")
    monkeypatch.setattr(services.llm, "chat", boom)
    r = client.post("/api/generate", json={"book_id": book["book"]["id"]}, headers={"X-OpenAI-Key": "sk-bad"})
    assert r.status_code == 401 and r.json()["error"]["code"] == "invalid_api_key"
