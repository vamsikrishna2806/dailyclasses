"""
agent_prebuilt.py  -  Same agent in ~25 lines using a prebuilt ReAct agent.
"""
import asyncio
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

try:                                    # LangChain >= 1.0
    from langchain.agents import create_agent

    def make_agent(llm, tools, prompt):
        return create_agent(llm, tools, system_prompt=prompt)
except ImportError:                     # older LangGraph
    from langgraph.prebuilt import create_react_agent

    def make_agent(llm, tools, prompt):
        return create_react_agent(llm, tools, prompt=prompt)

ROOT = Path(__file__).resolve().parent.parent


async def main():
    client = MultiServerMCPClient({
        "weather":  {"transport": "stdio", "command": sys.executable, "args": [str(ROOT / "servers" / "weather_server.py")]},
        "time":     {"transport": "stdio", "command": sys.executable, "args": ["-m", "mcp_server_time"]},
        "fetch":    {"transport": "stdio", "command": sys.executable, "args": ["-m", "mcp_server_fetch"]},
        "deepwiki": {"transport": "streamable_http", "url": "https://mcp.deepwiki.com/mcp"},
    })
    tools = await client.get_tools()                 # MCP tools -> LangChain tools
    agent = make_agent(ChatOllama(model="llama3.2", temperature=0), tools,
                       "Always use tools for live data (time, weather, web pages, GitHub repos).")

    question = "What time is it in Tokyo right now, and what's the weather in Hyderabad?"
    result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
