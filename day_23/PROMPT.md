# Prompt used to generate day_23

## 1. The program

```
Write a very simple Python program that connects a local Ollama model (llama3.2)
to a free, live, remote MCP server (DeepWiki: https://mcp.deepwiki.com/mcp, no API key).
Use the `mcp` package (streamablehttp_client + ClientSession) and the `ollama` package.
Steps: connect and initialize, list the server's tools, convert them to Ollama tool
format, ask one question from input(), run any tool calls Ollama asks for with
session.call_tool, then call Ollama again and print the final answer.
Keep it short (one main() function, no classes, comments for each step).
Save it as day_23/ollama_mcp_client.py, add a requirements.txt (mcp>=1.10,<2 and ollama),
and test it inside a venv (python -m venv .venv).
```

## 2. logic.html

```
Create day_23/logic.html explaining ollama_mcp_client.py, in the same style as the
other days' logic.html pages (single HTML file, CSS variables on :root with light and
dark mode, a card with the file path, "Setup and run" commands, "Logic step by step"
as a numbered list, a table showing how the messages list grows
(user -> assistant tool_call -> tool -> assistant answer), sample output, a green
"Key idea" box and an orange "Note" box, and links to flow.html and PROMPT.md).
Simple English for beginners.
```

## 3. animation.html (Day 13 style motion graphics)

```
Create day_23/animation.html in the same style as day13_langchain/langchain_animation.html:
reuse its CSS, SVG helpers (B, T, E, C, A) and animation engine, and replace the
scenes with 6 new ones for ollama_mcp_client.py:
  01 Three helpers (Python = messenger, Ollama = brain, DeepWiki = toolbox)
  02 Connect and say hello (streamablehttp_client, ClientSession, initialize)
  03 Get the tool menu (list_tools, translate inputSchema -> parameters)
  04 Ollama decides (question + tools -> tool_call, it does not run the tool)
  05 Python runs the tool (call_tool, result added as role "tool", [:6000])
  06 The final answer (messages list grows, ollama.chat again, print answer)
Each scene: title, one-line idea, a "like" analogy for beginners, 4-5 steps,
key words, and the matching code. Do the same for day_21_mcp/animation.html with
10 scenes: N x M problem, host/client/server, tools/resources/prompts, JSON-RPC
message, lifecycle, stdio vs Streamable HTTP, FastMCP server, raw client,
MultiServerMCPClient, LangGraph agent loop.
```

## 4. flow.html

```
Create day_23/flow.html: a very simple step-by-step page for beginners that
explains ollama_mcp_client.py. Show 3 helpers at the top with emoji and a
nickname: Python program (messenger 🐍), Ollama (brain 🧠), MCP server (toolbox 🧰).
Below, show 5 numbered steps as cards. Each card has an emoji arrow (who talks
to whom), one or two plain-English sentences written like a conversation, and the
one matching code line:
  1. Python asks the toolbox "What tools do you have?" (list_tools)
  2. Python gives the brain the question and the tool list (ollama.chat with tools)
  3. The brain asks Python "Please run ask_wiki_question for me" (tool_calls)
  4. Python runs the tool on the toolbox and gets the result (call_tool)
  5. Python gives the result to the brain, which writes the answer (ollama.chat)
Cards start faded and appear one by one when the student presses Next; add a
Start again button. At the end show: "the brain decides, Python runs, the MCP
server has the tools". Single HTML file, no libraries, light/dark mode, mobile friendly.
```
