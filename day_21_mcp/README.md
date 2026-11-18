# Day 21: MCP Zero → Hero

An animated, interactive, beginner-to-advanced tutorial on the **Model Context Protocol (MCP)**. It ends with a **LangGraph agent** that pulls **live data** from real MCP servers.

## Start here
1. **[index.html](index.html)**: the motion-graphics tutorial (16 chapters, quiz at the end). Open it in a browser.
2. **[HOW_TO_USE.md](HOW_TO_USE.md)**: run the servers and agents step by step.
3. **[architecture.html](architecture.html)**: component, graph, startup and request-flow diagrams.
4. **[prompt.md](prompt.md)**: the system prompt explained, plus test prompts for every server.
5. **[prompt_nontechnical.md](prompt_nontechnical.md)**: MCP explained in plain language.

## Tutorial chapters
| Level | Chapters |
|---|---|
| 0 · Zero | The N×M problem (interactive) · USB-C analogy · MCP vs REST vs function calling |
| 1 · Beginner | Host / Client / Server (clickable live diagram) · the 6 primitives (flip cards) |
| 2 · Intermediate | JSON-RPC anatomy · lifecycle step-through · stdio vs Streamable HTTP · end-to-end request simulator |
| 3 · Builder | Build a FastMCP server · raw client · real live MCP servers |
| 4 · Hero | LangGraph + MCP agent (animated graph + code) · security · cheat sheet · quiz |

## Quick run
```powershell
cd D:\getwork\day_21_mcp
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
ollama pull llama3.2
python agent/agent_graph.py
```

## Live servers the agent uses
- **weather** (ours): wraps the free Open-Meteo API, giving real current weather and forecasts
- **fetch** (official `mcp-server-fetch`): reads any web page that allows it
- **time** (official `mcp-server-time`): the real current time in any time zone
- **deepwiki** (public remote, `https://mcp.deepwiki.com/mcp`): Q&A about any GitHub repo
- **math** and **notes** (ours): the teaching servers (stdio and HTTP)

Tested 2026-11-16 with mcp 1.30, langchain-mcp-adapters 0.3.2, langgraph 1.2, and Ollama llama3.2.
