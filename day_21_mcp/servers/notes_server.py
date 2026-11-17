"""
notes_server.py  -  An MCP server over Streamable HTTP (a tiny web service)
Run:  python servers/notes_server.py      ->  http://127.0.0.1:8000/mcp
"""
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Notes", host="127.0.0.1", port=8000)
NOTES: list[dict] = []          # in-memory "database"


@mcp.tool()
def add_note(title: str, body: str) -> str:
    """Save a note with a title and a body. Returns a confirmation."""
    note = {"id": len(NOTES) + 1, "title": title, "body": body,
            "created": datetime.now().isoformat(timespec="seconds")}
    NOTES.append(note)
    return f"Saved note #{note['id']}: {title}"


@mcp.tool()
def list_notes() -> list[dict]:
    """Return every saved note."""
    return NOTES


@mcp.tool()
def search_notes(keyword: str) -> list[dict]:
    """Find notes whose title or body contains the keyword (case-insensitive)."""
    k = keyword.lower()
    return [n for n in NOTES if k in n["title"].lower() or k in n["body"].lower()]


@mcp.resource("notes://all")
def all_notes() -> str:
    """All notes as plain text."""
    return "\n".join(f"#{n['id']} {n['title']}: {n['body']}" for n in NOTES) or "(no notes yet)"


if __name__ == "__main__":
    # HTTP transport: printing is fine here (stdout is not the protocol channel)
    print("Notes MCP server -> http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http")
