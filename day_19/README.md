# Day 19 — Agentic Architectures

Four small agents, one per architecture. Same stack as day 17: **LangChain + LangGraph + Ollama (`llama3.2`)**, free, runs on your computer.

| Folder | Architecture | One-line idea | You type |
|---|---|---|---|
| [router_agent](router_agent/) | **Router** | One agent picks *who* answers | a support question |
| [reflection_agent](reflection_agent/) | **Reflection** | Write → critique → revise, in a loop | what to write |
| [supervisor_agent](supervisor_agent/) | **Supervisor + workers** | A boss delegates, workers report back | a topic |
| [human_in_loop_agent](human_in_loop_agent/) | **Human in the loop** | The graph pauses until you approve | an email request |

## How to start (every folder works the same way)

1. Install **Python 3.10+** and **[Ollama](https://ollama.com/download)**, then run `ollama pull llama3.2` once.
2. Open a terminal **inside one folder** and read its **`HOW_TO_USE.md`** — it has the exact commands, what to type, what you should see, and fixes for common errors.
3. Each folder contains:

| File | Purpose |
|---|---|
| `HOW_TO_USE.md` | **Start here** — step-by-step usage guide |
| `agent.py` | The agent (the graph) |
| `tools.py` | The tools the agent can call |
| `architecture.html` | Open in a browser — animated diagram |
| `prompt.md` | The prompts + a "build prompt" to recreate the agent with any AI |
| `prompt_nontechnical.md` | Plain-English explanation |
| `README.md` | Short overview |

Suggested order: Router → Reflection → Supervisor → Human in the loop.
