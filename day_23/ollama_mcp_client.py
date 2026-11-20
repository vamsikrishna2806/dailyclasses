# Ollama + free live MCP server (DeepWiki) - very simple version
# pip install -r requirements.txt      |      ollama pull llama3.2

import asyncio
import ollama
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("https://mcp.deepwiki.com/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Get tools from the MCP server and give them to Ollama
            tools = (await session.list_tools()).tools
            ollama_tools = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]

            print("all the tools")
            print(ollama_tools)
            # 2. Ask Ollama a question
            question = input("Ask about a GitHub repo: ")
            messages = [{"role": "user", "content": question}]
            reply = ollama.chat(model="llama3.2", messages=messages, tools=ollama_tools)
            messages.append(reply.message)

            # 3. If Ollama wants a tool, run it on the MCP server
            for call in reply.message.tool_calls or []:
                print("Calling tool:", call.function.name)
                result = await session.call_tool(call.function.name, call.function.arguments)
                messages.append({"role": "tool", "content": result.content[0].text[:6000]})

            # 4. Ask Ollama again with the tool result -> final answer
            final = ollama.chat(model="llama3.2", messages=messages)
            print("\nAnswer:", final.message.content)


asyncio.run(main())
