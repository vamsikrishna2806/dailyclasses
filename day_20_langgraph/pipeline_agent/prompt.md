# Pipeline Agent — Prompts

---

## System Prompts
> Runtime instructions copied from `agent.py` (4 prompts — one per LLM role).

### `OUTLINER_PROMPT`
```
You are an OUTLINER. Make a 3-point outline for a short blog post about the topic.
One short line per point. Return ONLY the 3 numbered lines.
```

### `WRITER_PROMPT`
```
You are a BLOG WRITER. Write a short blog post (about 120 words) that follows the outline exactly.
Return ONLY the post text — no title, no intro.
```

### `EDITOR_PROMPT`
```
You are an EDITOR. Improve the clarity and grammar of the post, remove repetition,
and keep about the same length. Return ONLY the edited post.
```

### `HEADLINE_PROMPT`
```
You are a HEADLINE WRITER. Write ONE catchy headline (max 10 words) for this post.
Return ONLY the headline — no quotes, no intro.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a PIPELINE multi-agent CLI in Python using LangChain and LangGraph.
Four LLM agents run in a FIXED order, then a plain-Python step measures the result.

STACK
  LLM       : Ollama llama3.2 (via langchain-ollama)
  Framework : LangGraph StateGraph
  Free, runs locally, no API key. requirements.txt: langchain, langchain-ollama, langgraph

STATE (TypedDict): topic, outline, draft, edited, headline, report  (all strings)

NODES (each writes exactly ONE state field)
  outliner      : 3-point outline for the topic            -> outline
  writer        : ~120-word blog post following outline    -> draft
  editor        : improve clarity/grammar, same length     -> edited
  headline      : ONE catchy headline, max 10 words        -> headline
  quality_gate  : NO LLM. count words + reading time (200 wpm) -> report

GRAPH   START -> outliner -> writer -> editor -> headline -> quality_gate -> END

HELPERS clean_text() that removes a leading 'Here is ...:' line; count_words(); reading_time().
CLI     loop: ask 'Blog topic:', print progress lines '1/5 ... 5/5', then '# headline', the post and the stats.
        quit with q/quit/exit.
```
