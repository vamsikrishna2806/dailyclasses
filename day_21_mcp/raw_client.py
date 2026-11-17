"""
raw_client.py  -  Talk to an MCP server directly, no LLM involved.
Run:  python raw_client.py
"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
SERVER = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).parent / "servers" / "math_server.py")])


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"Connected to '{init.serverInfo.name}' (protocol {init.protocolVersion})")

            tools = await session.list_tools()
            for t in tools.tools:
                print(f"  tool: {t.name:10} - {t.description}")

            result = await session.call_tool("multiply", {"a": 6, "b": 7})
            print("multiply(6, 7) =", result.content[0].text)

            res = await session.read_resource("math://constants")
            print("resource math://constants ->", res.contents[0].text.replace("\n", " | "))

            prompt = await session.get_prompt("explain_step_by_step", {"problem": "2^10 + 5"})
            print("prompt ->", prompt.messages[0].content.text)
            print("Done. (that is exactly what LangGraph's adapter does for you)")


if __name__ == "__main__":
    asyncio.run(main())
