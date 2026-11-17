# Prompts for the MCP agent

There are three kinds of "prompt" in this project. It helps to keep them apart:

| Kind | Where it lives | Who writes it | What it does |
|---|---|---|---|
| **System prompt** | `SYSTEM` in `agent/agent_graph.py` | you (the developer) | Tells the LLM *how to behave* and *which tool to use for what* |
| **Tool descriptions** | the docstring of every `@mcp.tool()` | the server author | Sent through `tools/list`; the LLM reads them to choose a tool |
| **MCP prompts** | `@mcp.prompt()` in a server | the server author | Reusable templates the *user* picks (e.g. a slash command in Claude Desktop) |
| **User prompts** | what you type at `You:` | the user | The actual question |

---

## 1. The system prompt (explained line by line)

```text
You are a helpful assistant connected to MCP tools.
- For ANY arithmetic, use the math tools (never calculate in your head).
- For the CURRENT time in a city, call get_current_time with an IANA timezone (e.g. "Asia/Tokyo").
  Use convert_time only when the user gives a specific time to convert.
- For live weather use get_current_weather / get_forecast.
- To read a web page (docs, Wikipedia, news) use the fetch tool.
- For questions about a GitHub repository use the deepwiki tools (repoName like "langchain-ai/langgraph").
- Use the notes tools to save or look up notes.
Answer briefly and say which tool gave you the data.
```

| Line | Why it's there |
|---|---|
| "never calculate in your head" | LLMs make arithmetic mistakes. This forces `tools/call` on the math server |
| get_current_time **vs** convert_time | In testing, `llama3.2` picked `convert_time` for "what time is it in Tokyo?". One explicit line fixed it |
| IANA timezone example | The time server rejects "Tokyo"; it needs `Asia/Tokyo`. The example teaches the format |
| repoName format | DeepWiki expects `owner/repo`; without the hint, small models send just `langgraph` |
| "say which tool gave you the data" | Makes the answer traceable, so you can see MCP working |

**Rule of thumb:** the bigger the model, the shorter this prompt can be. With `qwen2.5:7b` or Claude, the tool docstrings alone are usually enough. With `llama3.2` (3B), explicit routing hints help a lot.

---

## 2. Writing good tool descriptions (server side)

The docstring **is** the prompt the LLM sees for each tool:

```python
# ❌ vague: the model doesn't know when to use it, or what it returns
@mcp.tool()
def wx(c: str): ...

# ✅ clear: says what, when, units, and what comes back
@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """Get the LIVE current weather for a city (temperature in Celsius, wind, conditions)."""
```
Checklist: verb + object · say "LIVE"/"current" if it's real-time · units · argument format · one tool = one job.

---

## 3. Test prompts (copy and paste at `You:`)

### 🌦️ weather server (live)
- `What is the weather in Hyderabad right now?`
- `Will it rain in London in the next 3 days?`
- `Which is warmer right now, Delhi or Dubai?` → two tool calls
- `Weather in Atlantis?` → shows a **tool error** coming back, and the model recovering

### ⏰ time server (official, live)
- `What time is it in Tokyo?`
- `When it's 9:00 AM in New York, what time is it in Hyderabad?` → `convert_time`

### 🧮 math server
- `What is 23 times 19?`
- `What is 2 to the power of 16, plus 100?` → chained calls (power → add)

### 🌐 fetch server (official, live web)
- `Fetch https://modelcontextprotocol.io/docs/getting-started/intro and tell me what MCP is in 2 lines.`
- `Read https://en.wikipedia.org/wiki/Model_Context_Protocol and summarise it.`

### 📚 deepwiki (public remote server)
- `Using deepwiki, what is langchain-ai/langgraph and what are its main concepts?`
- `Ask deepwiki how modelcontextprotocol/python-sdk implements FastMCP tools.`

### 📝 notes server (start `python servers/notes_server.py` first)
- `Save a note titled "mcp" saying "host, client, server"`
- `List all my notes`
- `Search my notes for mcp`

### 🦸 multi-server "hero" prompts (several servers in one answer)
- `What time is it in Tokyo, and what's the weather in Hyderabad in Fahrenheit?`
  → time + weather + math (°C × 1.8 + 32)
- `Get the 3-day forecast for Paris, then save it as a note called "paris trip".`
  → weather → notes
- `Ask deepwiki what LangGraph is, then save a one-line summary as a note.`
  → deepwiki → notes
- `What's the max temperature difference between Delhi and Mumbai today?`
  → weather ×2 → math

---

## 4. The MCP prompt in `math_server.py`

```python
@mcp.prompt()
def explain_step_by_step(problem: str) -> str:
    """Template: solve a math problem step by step."""
    return f"Solve step by step. Use the math tools for EVERY calculation:\n{problem}"
```
- In **Claude Desktop** it appears in the "+" / slash menu. The user picks it and fills in `problem`.
- In code: `await session.get_prompt("explain_step_by_step", {"problem": "2^10 + 5"})` (see `raw_client.py`).
- With the adapters: `await client.get_prompt("math", "explain_step_by_step", {"problem": "..."})` returns LangChain messages you can pass straight to the agent.
