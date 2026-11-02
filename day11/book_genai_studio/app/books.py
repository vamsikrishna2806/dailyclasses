"""Turn an uploaded book into clean text, chapters and searchable chunks.

Pipeline:  file bytes -> pages of text -> cleaned full text -> chapters -> chunks (~450 tokens)
"""
import html
import io
import json
import re
import time
import uuid
import zipfile
from pathlib import Path

from . import config
from .tokens import count_tokens

SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".epub", ".html", ".htm"}
BOOKS_DIR = config.DATA_DIR / "books"
BOOKS_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_TOKENS = 450
OVERLAP_TOKENS = 80


class BookError(Exception):
    def __init__(self, status: int, code: str, message: str, hint: str = ""):
        super().__init__(message)
        self.status, self.code, self.message, self.hint = status, code, message, hint

    def to_dict(self):
        return {"error": {"code": self.code, "message": self.message, "hint": self.hint}}


# ---------------------------------------------------------------- text extraction

def _decode(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            if enc == "utf-16" and "\x00" in text:
                continue
            return text
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _html_to_text(markup: str) -> str:
    markup = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?is)<h[1-2][^>]*>(.*?)</h[1-2]>", lambda m: "\n\n# " + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n\n", markup)
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?i)</(p|div|li|h[3-6]|tr|blockquote|section)>", "\n\n", markup)
    markup = re.sub(r"<[^>]+>", "", markup)
    return html.unescape(markup)


def _epub_pages(data: bytes) -> tuple[list[str], str | None]:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise BookError(422, "bad_epub", "This EPUB file is damaged.")
    title = None
    order = []
    try:
        container = z.read("META-INF/container.xml").decode("utf-8", "replace")
        opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
        opf = z.read(opf_path).decode("utf-8", "replace")
        base = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
        t = re.search(r"<dc:title[^>]*>(.*?)</dc:title>", opf, re.S)
        title = html.unescape(t.group(1).strip()) if t else None
        manifest = {m.group(1): m.group(2) for m in re.finditer(r'<item\b[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', opf)}
        manifest.update({m.group(2): m.group(1) for m in re.finditer(r'<item\b[^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', opf)})
        for idref in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf):
            if idref in manifest:
                order.append(base + manifest[idref])
    except (KeyError, AttributeError):
        pass
    if not order:
        order = sorted(n for n in z.namelist() if n.lower().endswith((".xhtml", ".html", ".htm")))
    pages = []
    for name in order:
        try:
            pages.append(_html_to_text(z.read(name).decode("utf-8", "replace")))
        except KeyError:
            continue
    return pages, title


def extract(filename: str, data: bytes) -> tuple[list[str], str | None, bool]:
    """Returns (pages, title_from_metadata, has_real_page_numbers)."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        raise BookError(415, "unsupported_type", f"“{ext or 'no extension'}” files aren't supported.",
                        "Upload PDF, EPUB, DOCX, TXT, MD or HTML.")
    if ext in (".txt", ".md"):
        return [_decode(data)], None, False
    if ext in (".html", ".htm"):
        return [_html_to_text(_decode(data))], None, False
    if ext == ".epub":
        pages, title = _epub_pages(data)
        return pages, title, False
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(data))
        except Exception:
            raise BookError(422, "bad_docx", "Couldn't open this Word file.")
        lines = []
        for p in doc.paragraphs:
            style = (p.style.name if p.style is not None else "") or ""
            lines.append(("# " + p.text) if style.startswith(("Heading 1", "Title")) and p.text.strip() else p.text)
        title = doc.core_properties.title or None
        return ["\n\n".join(lines)], title, False
    # PDF
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            reader.decrypt("")
        pages = [(p.extract_text() or "") for p in reader.pages]
        title = (reader.metadata.title if reader.metadata else None) or None
    except Exception:
        raise BookError(422, "bad_pdf", "Couldn't read this PDF (damaged or password-protected).")
    return pages, title, True


def clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("­", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)        # join words split across lines
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------- chapters

_NUM = r"(?:\d+|[ivxlcdm]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|[a-z]+teen|twenty[a-z\- ]*|thirty[a-z\- ]*)"
CHAPTER_RE = re.compile(
    rf"^(?:#{{1,2}} .{{1,100}}|(?:chapter|part|book|section|act|lesson|unit) {_NUM}\b.{{0,80}}"
    r"|prologue|epilogue|introduction|preface|foreword|afterword|conclusion|appendix\b.{0,60})$",
    re.I | re.M,
)


def split_chapters(text: str) -> list[dict]:
    marks = [(m.start(), m.group(0).lstrip("# ").strip()) for m in CHAPTER_RE.finditer(text)]
    sections = []
    if marks and marks[0][0] > 0:
        sections.append(["Opening", 0])
    for start, title in marks:
        sections.append([title[:100], start])
    if not sections:
        sections = [["Opening", 0]]
    bounds = []
    for i, (title, start) in enumerate(sections):
        end = sections[i + 1][1] if i + 1 < len(sections) else len(text)
        bounds.append({"title": title, "start": start, "end": end})

    # Merge tiny sections (table-of-contents lines, stray headings) into the next one.
    merged = []
    carry_start = None
    for b in bounds:
        words = len(text[b["start"]:b["end"]].split())
        start = carry_start if carry_start is not None else b["start"]
        if words < 120 and b is not bounds[-1]:
            carry_start = start
            continue
        merged.append({"title": b["title"], "start": start, "end": b["end"]})
        carry_start = None

    # No real chapters? Make even-sized parts so "summarize by chapter" still works.
    if len(merged) < 2 and count_tokens(text) > 6000:
        merged, size, pos, n = [], 12000 * 4, 0, 1  # ~3000 words per part
        while pos < len(text):
            end = min(len(text), pos + size)
            if end < len(text):
                nl = text.rfind("\n\n", pos + size // 2, end)
                end = nl if nl > 0 else end
            merged.append({"title": f"Part {n}", "start": pos, "end": end})
            pos, n = end, n + 1
    return merged


# ---------------------------------------------------------------- chunks

_SENT_RE = re.compile(r"(?<=[.!?…”\"])\s+(?=[A-Z“\"'(\[])")


def split_sentences(text: str) -> list[str]:
    """Sentences, with short unpunctuated lines (titles, headings) kept as their own items."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        lines, buf = para.split("\n"), []
        for line in lines:
            s = line.strip()
            if s and len(s.split()) <= 12 and not re.search(r"[.!?…:;,”\"')]$", s):
                if buf:
                    out.extend(_SENT_RE.split(" ".join(buf)))
                    buf = []
                out.append(s)
            elif s:
                buf.append(s)
        if buf:
            out.extend(_SENT_RE.split(" ".join(buf)))
    return [s.strip() for s in out if s.strip()]


def _pieces(text: str) -> list[str]:
    """Paragraphs, with very long paragraphs broken into sentence groups."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if count_tokens(para) <= CHUNK_TOKENS:
            out.append(para)
            continue
        buf = ""
        for s in split_sentences(para):
            if buf and count_tokens(buf + " " + s) > CHUNK_TOKENS:
                out.append(buf)
                buf = s
            else:
                buf = (buf + " " + s).strip()
        if buf:
            out.append(buf)
    return out


def make_chunks(text: str, chapters: list[dict], page_starts: list[int] | None) -> list[dict]:
    chunks = []
    for ci, ch in enumerate(chapters):
        body = text[ch["start"]:ch["end"]]
        buf, buf_tokens, cursor = [], 0, ch["start"]
        pieces = _pieces(body)

        def flush():
            nonlocal cursor
            chunk_text = "\n\n".join(buf)
            pos = text.find(buf[0][:60], cursor)
            if pos >= 0:
                cursor = pos
            page = None
            if page_starts:
                page = sum(1 for s in page_starts if s <= max(pos, ch["start"]))
            chunks.append({"id": len(chunks), "chapter": ci, "page": page,
                           "tokens": count_tokens(chunk_text), "text": chunk_text})

        for p in pieces:
            t = count_tokens(p)
            if buf and buf_tokens + t > CHUNK_TOKENS:
                flush()
                last = buf[-1]
                lt = count_tokens(last)
                buf, buf_tokens = ([last], lt) if lt <= OVERLAP_TOKENS * 2 else ([], 0)
            buf.append(p)
            buf_tokens += t
        if buf:
            flush()
    return chunks


# ---------------------------------------------------------------- build + store

def build(filename: str, data: bytes) -> dict:
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise BookError(413, "file_too_large", f"File is over {config.MAX_UPLOAD_MB:g} MB.",
                        "Compress the PDF or upload a .txt version." +
                        (" (Vercel's free plan limits uploads to about 4.5 MB.)" if config.ON_VERCEL else ""))
    if not data:
        raise BookError(400, "empty_file", "The file is empty.")
    pages, meta_title, paged = extract(filename, data)
    cleaned = [clean(p) for p in pages]
    text, page_starts = "", []
    for p in cleaned:
        if not p:
            page_starts.append(len(text))
            continue
        if text:
            text += "\n\n"
        page_starts.append(len(text))
        text += p
    if len(text.split()) < 50:
        raise BookError(422, "no_text", "No readable text was found in this file.",
                        "If it's a scanned PDF, run OCR on it first (e.g. with Google Drive or Adobe).")
    n_tokens = count_tokens(text)
    if n_tokens > config.MAX_BOOK_TOKENS:
        raise BookError(413, "book_too_long", f"This book has about {n_tokens:,} tokens; the limit is "
                        f"{config.MAX_BOOK_TOKENS:,}.", "Split it into volumes or raise MAX_BOOK_TOKENS.")
    chapters = split_chapters(text)
    chunks = make_chunks(text, chapters, page_starts if paged else None)
    for i, ch in enumerate(chapters):
        ch["idx"] = i
        ch["tokens"] = sum(c["tokens"] for c in chunks if c["chapter"] == i)
        ch["words"] = len(text[ch["start"]:ch["end"]].split())
    title = (meta_title or "").strip() or Path(filename).stem.replace("_", " ").replace("-", " ").strip().title()
    return {
        "id": uuid.uuid4().hex[:12],
        "title": title[:120],
        "filename": filename,
        "created": time.time(),
        "pages": len(pages) if paged else None,
        "words": len(text.split()),
        "tokens": n_tokens,
        "text": text,
        "chapters": chapters,
        "chunks": chunks,
        "embeddings": None,
        "cache": {},
    }


def public(book: dict) -> dict:
    """Book info without the big fields."""
    return {k: book[k] for k in ("id", "title", "filename", "created", "pages", "words", "tokens")} | {
        "chapters": [{k: c[k] for k in ("idx", "title", "tokens", "words")} for c in book["chapters"]],
        "chunks": len(book["chunks"]),
        "semantic_search": book.get("embeddings") is not None,
    }


def portable(book: dict) -> dict:
    """Everything needed to rebuild the book on another server (no embeddings: too big)."""
    return {k: book[k] for k in ("id", "title", "filename", "created", "pages", "words", "tokens",
                                 "text", "chapters", "chunks")}


class Store:
    """Books live in memory, with a JSON copy on disk."""

    def __init__(self):
        self.books: dict[str, dict] = {}

    def _path(self, book_id):
        return BOOKS_DIR / f"{re.sub(r'[^a-f0-9]', '', book_id)}.json"

    def save(self, book: dict):
        self.books[book["id"]] = book
        try:
            self._path(book["id"]).write_text(json.dumps(book), encoding="utf-8")
        except OSError:
            pass  # disk is optional (e.g. read-only); memory copy still works

    def get(self, book_id: str) -> dict:
        if book_id in self.books:
            return self.books[book_id]
        p = self._path(book_id)
        if p.exists():
            book = json.loads(p.read_text(encoding="utf-8"))
            self.books[book_id] = book
            return book
        raise BookError(404, "book_not_found", "This server doesn't have that book any more.",
                        "Your browser has a copy; it will be re-sent automatically.")

    def all(self) -> list[dict]:
        for p in BOOKS_DIR.glob("*.json"):
            if p.stem not in self.books:
                try:
                    self.books[p.stem] = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
        return sorted(self.books.values(), key=lambda b: b["created"], reverse=True)

    def delete(self, book_id: str):
        self.books.pop(book_id, None)
        try:
            self._path(book_id).unlink(missing_ok=True)
        except OSError:
            pass


store = Store()
