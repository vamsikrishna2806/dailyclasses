"""Find the passages of a book that best match a question.

Two searches, combined:
  * BM25 keyword search  - always available, free, good for names and exact terms
  * Embedding search     - needs an OpenAI key, good for meaning ("why was she angry?")
Results are merged with Reciprocal Rank Fusion (RRF): a passage ranked high by
either search ends up near the top.
"""
import math
import re
from collections import Counter

import numpy as np

WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
STOP = set("""a about above after again against all am an and any are as at be because been before being
below between both but by can could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my myself
no nor not now of off on once only or other our ours ourselves out over own same she should so some such than
that the their theirs them themselves then there these they this those through to too under until up very was
we were what when where which while who whom why will with would you your yours yourself yourselves also
said says say one may might shall upon unto thee thou thy""".split())


INITIALS = re.compile(r"\b(?:[a-z]\.){2,}")


def _stem(w: str) -> str:
    """Tiny stemmer so 'logbooks', 'climbed', 'climbing' match 'logbook', 'climb'."""
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4 and not w.endswith("ss"):
            return w[: -len(suf)]
    return w


def tokenize(text: str) -> list[str]:
    low = text.lower()
    words = [_stem(w) for w in WORD.findall(low) if w not in STOP and len(w) > 1]
    return words + [i.replace(".", "") + "_init" for i in INITIALS.findall(low)]  # keep "A.O." as one token


class BM25:
    def __init__(self, docs: list[str], k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(d)) for d in docs]
        self.lens = [sum(d.values()) for d in self.docs]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 0
        df = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for d, length in zip(self.docs, self.lens):
            s = 0.0
            for w in q:
                f = d.get(w)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self.avg or 1)))
            out.append(s)
        return out


_bm25_cache: dict[str, BM25] = {}


def _bm25(book) -> BM25:
    key = f"{book['id']}:{len(book['chunks'])}"
    if key not in _bm25_cache:
        _bm25_cache[key] = BM25([c["text"] for c in book["chunks"]])
    return _bm25_cache[key]


def search(book: dict, query: str, k: int = 6, chapter: int | None = None, query_vec=None) -> list[dict]:
    chunks = book["chunks"]
    allowed = [i for i, c in enumerate(chunks) if chapter is None or c["chapter"] == chapter]
    if not allowed:
        return []
    bm = _bm25(book).scores(query)
    ranked_lists = [sorted(allowed, key=lambda i: bm[i], reverse=True)]
    if query_vec is not None and book.get("embeddings"):
        m = np.asarray(book["embeddings"], dtype=np.float32)
        q = np.asarray(query_vec, dtype=np.float32)
        sims = m @ q / (np.linalg.norm(m, axis=1) * np.linalg.norm(q) + 1e-9)
        ranked_lists.append(sorted(allowed, key=lambda i: sims[i], reverse=True))
    elif max(bm[i] for i in allowed) == 0:
        return []  # no keyword overlap at all and no semantic search
    fused = Counter()
    for ranked in ranked_lists:
        for rank, i in enumerate(ranked[:50]):
            fused[i] += 1 / (60 + rank)
    top = [i for i, _ in fused.most_common(k)]
    return [chunks[i] | {"score": round(fused[i], 5)} for i in top]


# ---------------------------------------------------------------- offline helpers (Demo mode)

def extractive_summary(text: str, n_sentences: int = 8) -> list[str]:
    """Pick the sentences that use the text's most important words."""
    from .books import split_sentences
    sents = [s for s in split_sentences(text)
             if 6 <= len(s.split()) <= 60 and re.search(r"[.!?…”\"']$", s)]
    if len(sents) <= n_sentences:
        return sents
    freq = Counter(tokenize(text))
    top = max(freq.values()) if freq else 1
    scored = []
    for i, s in enumerate(sents):
        words = tokenize(s)
        if not words:
            continue
        score = sum(freq[w] / top for w in words) / (len(words) ** 0.6)
        score *= 1.15 if i < len(sents) * 0.1 else 1.0  # openings matter
        scored.append((score, i))
    # spread picks across the text: best sentence from each slice
    picked = set()
    slices = max(1, n_sentences)
    size = len(sents) / slices
    for s in range(slices):
        lo, hi = int(s * size), int((s + 1) * size)
        best = max(((sc, i) for sc, i in scored if lo <= i < hi), default=None)
        if best:
            picked.add(best[1])
    return [sents[i] for i in sorted(picked)]


def best_sentences(passages: list[str], query: str, n: int = 4) -> list[str]:
    from .books import split_sentences
    q = set(tokenize(query))
    cands = []
    for p in passages:
        for s in split_sentences(p):
            overlap = len(q & set(tokenize(s)))
            if overlap:
                cands.append((overlap / (len(s.split()) ** 0.3), s))
    cands.sort(reverse=True)
    seen, out = set(), []
    for _, s in cands:
        if s not in seen:
            out.append(s)
            seen.add(s)
        if len(out) == n:
            break
    return out


FILLER = set("""every would could like time back still just even much many made make know knew went
come came first last long little great never always only other into over than then them they well what
when where which while will with without because before after again away down here there these those
thought looked something nothing anything everything someone people thing things later another""".split())


def keywords(text: str, n: int = 12) -> list[str]:
    freq = Counter(w for w in WORD.findall(text.lower())
                   if len(w) > 3 and not w.isdigit() and w not in FILLER and w not in STOP)
    return [w for w, _ in freq.most_common(n)]
