"""
agent_graph.py  -  A LangGraph ReAct agent whose tools come from MCP servers.

    START -> agent (LLM) --tool_calls?--> tools (MCP) -> agent ... -> END

MCP servers used (each one is optional - missing ones are skipped):
  math   : our own stdio server                (servers/math_server.py)
  weather: our own LIVE weather server         (servers/weather_server.py -> Open-Meteo API)
  notes  : our own HTTP server                 (run servers/notes_server.py first)
  fetch  : OFFICIAL real-time web fetcher      (pip install mcp-server-fetch)
  time   : OFFICIAL current time / time zones  (pip install mcp-server-time)
  deepwiki: PUBLIC remote server for GitHub repo docs (internet, no key)
"""
import asyncio
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
OLLAMA_MODEL = "llama3.2"     # must support tool calling: llama3.2, llama3.1, qwen2.5:7b (smarter), mistral-nemo

# 1) Which MCP servers to connect to ------------------------------------------
SERVERS = {
    "math":     {"transport": "stdio", "command": PY, "args": [str(ROOT / "servers" / "math_server.py")]},
    "weather":  {"transport": "stdio", "command": PY, "args": [str(ROOT / "servers" / "weather_server.py")]},
    "notes":    {"transport": "streamable_http", "url": "http://127.0.0.1:8000/mcp"},
    "fetch":    {"transport": "stdio", "command": PY, "args": ["-m", "mcp_server_fetch"]},
    "time":     {"transport": "stdio", "command": PY, "args": ["-m", "mcp_server_time"]},
    "deepwiki": {"transport": "streamable_http", "url": "https://mcp.deepwiki.com/mcp"},
}

SYSTEM = """You are a helpful assistant connected to MCP tools.
- For ANY arithmetic, use the math tools (never calculate in your head).
- For the CURRENT time in a city, call get_current_time with an IANA timezone (e.g. "Asia/Tokyo").
  Use convert_time only when the user gives a specific time to convert.
- For live weather use get_current_weather / get_forecast.
- To read a web page (docs, Wikipedia, news) use the fetch tool.
- For questions about a GitHub repository use the deepwiki tools (repoName like "langchain-ai/langgraph").
- Use the notes tools to save or look up notes.
Answer briefly and say which tool gave you the data."""


# 2) Graph state: just a list of chat messages ---------------------------------
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


async def load_mcp_tools():
    """Connect to every server; skip the ones that are not available."""
    client = MultiServerMCPClient(SERVERS)
    tools = []
    for name in SERVERS:
        try:
            server_tools = await client.get_tools(server_name=name)
            tools += server_tools
            print(f"  [ok]   {name:9} -> {', '.join(t.name for t in server_tools)}")
        except Exception as e:  # server not installed / not running / offline
            print(f"  [skip] {name:9} -> {type(e).__name__}")
    return tools


async def build_graph():
    tools = await load_mcp_tools()
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0).bind_tools(tools)

    async def agent(state: State):
        reply = await llm.ainvoke([SystemMessage(SYSTEM)] + state["messages"])
        return {"messages": [reply]}

    g = StateGraph(State)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(tools))         # runs MCP tools/call for us
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)   # tool_calls? -> "tools" else END
    g.add_edge("tools", "agent")
    return g.compile(checkpointer=MemorySaver())  # memory across turns


async def main():
    print("Connecting to MCP servers...")
    graph = await build_graph()
    config = {"configurable": {"thread_id": "day21"}}
    print("\nAsk me anything (live weather, time, math, web pages, GitHub repos, notes). 'quit' to exit.")

    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"quit", "exit", "q"}:
            break
        if not q:
            continue
        async for update in graph.astream({"messages": [HumanMessage(q)]}, config, stream_mode="updates"):
            for node, data in update.items():
                msg = data["messages"][-1]
                if node == "agent" and getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        print(f"  -> [agent] calls {tc['name']}({tc['args']})")
                elif node == "tools":
                    for m in data["messages"]:
                        print(f"  <- [tool:{m.name}] {str(m.content)[:160]}")
                else:
                    print(f"\nAgent: {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
