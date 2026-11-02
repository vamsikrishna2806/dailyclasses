"""SQLite storage for usage tracking and user feedback.

On Vercel the file lives in /tmp and is lost when the instance restarts, so the
frontend also keeps its own copy in the browser (see static/app.js).
"""
import sqlite3
import time
from contextlib import contextmanager

from . import config

DB_PATH = config.DATA_DIR / "studio.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    feature TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    cost REAL DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    ok INTEGER DEFAULT 1,
    error TEXT
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    feature TEXT NOT NULL,
    prompt_version TEXT,
    rating INTEGER NOT NULL,
    comment TEXT,
    output_id TEXT,
    output_excerpt TEXT
);
"""


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init():
    with connect() as c:
        c.executescript(SCHEMA)


def log_usage(feature, model, prompt_tokens, completion_tokens, cost, latency_ms, ok=True, error=None):
    with connect() as c:
        c.execute(
            "INSERT INTO usage (ts, feature, model, prompt_tokens, completion_tokens, cost, latency_ms, ok, error)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (time.time(), feature, model, prompt_tokens, completion_tokens, cost, latency_ms, int(ok), error),
        )


def cost_today() -> float:
    start = time.time() - (time.time() % 86400)
    with connect() as c:
        row = c.execute("SELECT COALESCE(SUM(cost),0) FROM usage WHERE ts >= ?", (start,)).fetchone()
    return float(row[0])


def usage_summary() -> dict:
    with connect() as c:
        totals = dict(c.execute(
            "SELECT COUNT(*) calls, COALESCE(SUM(prompt_tokens),0) prompt_tokens,"
            " COALESCE(SUM(completion_tokens),0) completion_tokens, COALESCE(SUM(cost),0) cost,"
            " COALESCE(AVG(latency_ms),0) avg_latency_ms, COALESCE(SUM(1-ok),0) errors FROM usage").fetchone())
        by_feature = [dict(r) for r in c.execute(
            "SELECT feature, COUNT(*) calls, SUM(prompt_tokens+completion_tokens) tokens, SUM(cost) cost,"
            " AVG(latency_ms) avg_latency_ms FROM usage GROUP BY feature ORDER BY tokens DESC")]
        by_day = [dict(r) for r in c.execute(
            "SELECT date(ts,'unixepoch') day, SUM(prompt_tokens+completion_tokens) tokens, SUM(cost) cost,"
            " COUNT(*) calls FROM usage GROUP BY day ORDER BY day DESC LIMIT 14")]
        recent = [dict(r) for r in c.execute(
            "SELECT ts, feature, model, prompt_tokens, completion_tokens, cost, latency_ms, ok, error"
            " FROM usage ORDER BY id DESC LIMIT 25")]
    return {"totals": totals, "by_feature": by_feature, "by_day": by_day[::-1], "recent": recent,
            "cost_today": cost_today(), "daily_budget": config.DAILY_BUDGET_USD}


def clear_usage():
    with connect() as c:
        c.execute("DELETE FROM usage")


def add_feedback(feature, prompt_version, rating, comment, output_id, output_excerpt):
    with connect() as c:
        c.execute(
            "INSERT INTO feedback (ts, feature, prompt_version, rating, comment, output_id, output_excerpt)"
            " VALUES (?,?,?,?,?,?,?)",
            (time.time(), feature, prompt_version, rating, comment, output_id, (output_excerpt or "")[:500]),
        )


def feedback_summary() -> dict:
    with connect() as c:
        by_version = [dict(r) for r in c.execute(
            "SELECT feature, prompt_version, COUNT(*) n, AVG(rating) avg_rating,"
            " SUM(CASE WHEN rating>=4 THEN 1 ELSE 0 END) positive FROM feedback"
            " GROUP BY feature, prompt_version ORDER BY feature, prompt_version")]
        recent = [dict(r) for r in c.execute(
            "SELECT ts, feature, prompt_version, rating, comment, output_excerpt FROM feedback"
            " ORDER BY id DESC LIMIT 30")]
    return {"by_version": by_version, "recent": recent}
