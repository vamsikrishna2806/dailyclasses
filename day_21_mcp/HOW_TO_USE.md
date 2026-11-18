# How to run the MCP agents (step by step)

This guide takes you from an empty terminal to a LangGraph agent that pulls **live data** from real MCP servers.
Commands are for **Windows PowerShell**. The macOS/Linux equivalents are shown where they differ.

---

## 0. What you need

| Need | Why | Check |
|---|---|---|
| Python 3.10+ | runs servers + agent | `python --version` |
| Ollama | the local LLM (the agent's "brain") | `ollama --version` |
| A tool-calling model | must be able to emit `tool_calls` | `ollama list` |
| Internet | weather, fetch, DeepWiki are live | — |

Models that work: `llama3.2` (default, 2 GB), `llama3.1`, **`qwen2.5:7b` (best at choosing tools)**, `mistral-nemo`.
To change the model, edit `OLLAMA_MODEL` at the top of `agent/agent_graph.py`.

---

## 1. One-time setup

```powershell
cd D:\getwork\day_21_mcp
python -m venv .venv
.venv\Scripts\activate             # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2               # or: ollama pull qwen2.5:7b
```

`requirements.txt` installs:
- `mcp[cli]`: the official MCP SDK (FastMCP, client, `mcp dev` Inspector)
- `langchain-mcp-adapters`: turns MCP tools into LangChain tools (`MultiServerMCPClient`)
- `langgraph`, `langchain`, `langchain-ollama`: the agent
- `mcp-server-fetch`, `mcp-server-time`: two **official, real** MCP servers

---

## 2. Learn in this order (each step builds on the last)

### Step A: open the tutorial
Double-click `index.html` (or open it in any browser). Go through chapters 01 → 16.

### Step B: test a server by hand with the MCP Inspector
```powershell
npx @modelcontextprotocol/inspector .venv\Scripts\python.exe servers/math_server.py
```
In the browser UI: **Connect** → **Tools** → **List Tools** → `multiply` → `a=6, b=7` → **Run**. You should see `42.0`.
Do the same for the live weather server:
```powershell
npx @modelcontextprotocol/inspector .venv\Scripts\python.exe servers/weather_server.py
```
> This starts the same Inspector as `mcp dev servers/math_server.py`, but without needing `mcp.exe` or `uv`.
> `mcp dev` requires `uv` to be installed. Some Windows machines also block the unsigned `mcp.exe` launcher (Device Guard).

**Stopping the Inspector and freeing its ports.** The Inspector uses port **6274** for the browser UI and port **6277** for its proxy. To stop it, press **Ctrl+C** in its terminal (answer `Y` if asked `Terminate batch job?`). This also stops the server it launched.

If you closed the terminal or a port is still in use, check what is listening:
```powershell
Get-NetTCPConnection -LocalPort 6274,6277 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess
```
If that prints anything, stop those processes (no output means the ports are already free):
```powershell
Get-NetTCPConnection -LocalPort 6274,6277 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
To run on different ports instead, set them before starting:
```powershell
$env:CLIENT_PORT=7000; $env:SERVER_PORT=7001; npx @modelcontextprotocol/inspector .venv\Scripts\python.exe servers/weather_server.py
```
Run `get_current_weather` with `city = Hyderabad`. It returns the real current temperature.

### Step C: talk to a server from code, with no LLM
```powershell
python raw_client.py
```
Expected output:
```
Connected to 'Math' (protocol 2025-11-25)
  tool: add        - Add two numbers and return the sum.
  tool: multiply   - Multiply two numbers and return the product.
  tool: power      - Raise base to the power of exponent.
multiply(6, 7) = 42.0
resource math://constants -> pi = 3.14159 | e = 2.71828 | golden_ratio = 1.61803
prompt -> Solve step by step. Use the math tools for EVERY calculation:
...
```
(You will also see `INFO Processing request ...` lines. That is the server logging to stderr, which is normal.)

### Step D (optional): start the HTTP server
The `notes` server is a **remote-style** server (Streamable HTTP). It must already be running before the agent starts.
Open a **second terminal**:
```powershell
cd D:\getwork\day_21_mcp; .venv\Scripts\activate
python servers/notes_server.py      # -> http://127.0.0.1:8000/mcp   (Ctrl+C to stop)
```
If you skip this, the agent prints `[skip] notes` and carries on without it.

### Step E: run the full LangGraph agent (custom graph)
```powershell
python agent/agent_graph.py
```
You'll see which servers connected:
```
Connecting to MCP servers...
  [ok]   math      -> add, multiply, power
  [ok]   weather   -> get_current_weather, get_forecast
  [ok]   notes     -> add_note, list_notes, search_notes
  [ok]   fetch     -> fetch
  [ok]   time      -> get_current_time, convert_time
  [ok]   deepwiki  -> ask_wiki_question, read_wiki_contents, read_wiki_structure
```
Then chat. Every tool call is printed:
```
You: What is the weather in Hyderabad right now?
  -> [agent] calls get_current_weather({'city': 'Hyderabad'})
  <- [tool:get_current_weather] {"city": "Hyderabad", "temperature_c": 25.7, ... "conditions": "clear sky"}
Agent: The current weather in Hyderabad is clear sky with a temperature of 25.7°C ...
```
Type `quit` to exit. Try the prompts in [`prompt.md`](prompt.md).

### Step F: run the 25-line prebuilt agent
```powershell
python agent/agent_prebuilt.py
```
It asks one fixed question (Tokyo time + Hyderabad weather) and prints the answer. It runs the same ReAct loop through LangChain's `create_agent`.

### Step G: use your servers in Claude Desktop / Cursor / VS Code
Copy `claude_desktop_config.example.json` into your host's MCP config. For Claude Desktop that's
`%APPDATA%\Claude\claude_desktop_config.json`. Restart the app. The same servers then work there with no code changes.
The example already points `"command"` at `D:/getwork/day_21_mcp/.venv/Scripts/python.exe`, so the host uses the venv's installed packages. Change that path if your project lives elsewhere.

---

## 3. Which file does what

```
day_21_mcp/
├── index.html                  ← the animated Zero-to-Hero tutorial (start here)
├── architecture.html           ← one-page architecture diagrams of the agent
├── HOW_TO_USE.md               ← this guide
├── prompt.md                   ← system prompt explained + test prompts per server
├── prompt_nontechnical.md      ← the same ideas in plain language
├── requirements.txt
├── raw_client.py               ← MCP client with no LLM (connect → list → call)
├── claude_desktop_config.example.json
├── servers/
│   ├── math_server.py          ← stdio · tools + resource + prompt (the basics)
│   ├── weather_server.py       ← stdio · LIVE Open-Meteo API wrapped as MCP
│   └── notes_server.py         ← Streamable HTTP · http://127.0.0.1:8000/mcp
└── agent/
    ├── agent_graph.py          ← custom LangGraph StateGraph + ToolNode + memory
    └── agent_prebuilt.py       ← same idea with create_agent (shortest version)
```

### The servers the agent connects to

| Name | Kind | Transport | Live? | Tools |
|---|---|---|---|---|
| math | ours | stdio | — | add, multiply, power |
| weather | ours (wraps Open-Meteo) | stdio | ✅ | get_current_weather, get_forecast |
| notes | ours | streamable_http | — | add_note, list_notes, search_notes |
| fetch | **official** (`mcp-server-fetch`) | stdio | ✅ | fetch(url) |
| time | **official** (`mcp-server-time`) | stdio | ✅ | get_current_time, convert_time |
| deepwiki | **public remote** (`https://mcp.deepwiki.com/mcp`) | streamable_http | ✅ | ask_wiki_question, read_wiki_structure, read_wiki_contents |

---

## 4. Add your own MCP server to the agent (3 steps)

1. Write it (copy `servers/weather_server.py` as a template):
   ```python
   @mcp.tool()
   async def my_tool(arg: str) -> str:
       """Clear description: the LLM reads this to decide when to call it."""
       ...
   ```
2. Register it in `SERVERS` in `agent/agent_graph.py`:
   ```python
   "mine": {"transport": "stdio", "command": PY, "args": [str(ROOT / "servers" / "my_server.py")]},
   # or a remote one:
   "remote": {"transport": "streamable_http", "url": "https://example.com/mcp",
              "headers": {"Authorization": "Bearer <token from env var>"}},
   ```
3. Mention it in the `SYSTEM` prompt ("For X, use my_tool"). Small models rely on this hint.

---

## 5. Troubleshooting

| Symptom | Cause → Fix |
|---|---|
| `[skip] notes -> ExceptionGroup` | The HTTP server isn't running → do Step D, or ignore it |
| `[skip] deepwiki` | No internet, or the remote server is down → the agent still works without it |
| `[skip] fetch` / `time` | Package missing → `pip install mcp-server-fetch mcp-server-time` |
| `model "..." not found` | `ollama pull llama3.2` (the name must match `OLLAMA_MODEL`) |
| `does not support tools` | That model can't call tools → use llama3.2 / llama3.1 / qwen2.5 |
| Agent answers without calling a tool, or picks the wrong one | Small model → switch to `qwen2.5:7b`, or make the SYSTEM prompt more explicit |
| `fetch` says robots.txt forbids it | That site blocks bots. The fetch server respects that → use a different page, or write a server that calls the site's official API (like `weather_server.py`) |
| A stdio server you wrote hangs or garbles | You used `print()` → stdout is the protocol channel; log to **stderr** |
| `Address already in use :8000` | notes server is already running → reuse it, or stop the other one |
