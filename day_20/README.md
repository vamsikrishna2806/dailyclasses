# Day 20 — 10 More Multi-Agent Architectures

Ten small, runnable multi-agent examples — one **pattern** per folder. Same stack as day 17 and day 19:
**LangChain + LangGraph + Ollama (`llama3.2`)**. Free, runs on your computer, **no API key**.

> 🎨 Open **[index.html](index.html)** in a browser for a clickable gallery of all 10 animated architecture diagrams.

## The 10 patterns

| # | Folder | Pattern | One-line idea | Level |
|---|---|---|---|---|
| 1 | [pipeline_agent](pipeline_agent/) | **Pipeline (assembly line)** | Agents work in a fixed order and each one passes its result to the next. | ⭐ easy |
| 2 | [parallel_agent](parallel_agent/) | **Parallel (fan-out / fan-in)** | Independent jobs run at the same time, then one agent merges the results. | ⭐ easy |
| 3 | [voting_agent](voting_agent/) | **Voting / ensemble** | Several agents with different personalities judge the same input and the majority wins. | ⭐⭐ medium |
| 4 | [debate_agent](debate_agent/) | **Debate (adversarial loop)** | Two agents with opposite jobs argue in turns and a neutral judge decides. | ⭐⭐ medium |
| 5 | [planner_executor_agent](planner_executor_agent/) | **Plan-and-Execute** | Think first and write a plan, then do the plan one step at a time with tools. | ⭐⭐ medium |
| 6 | [coder_tester_agent](coder_tester_agent/) | **Generate · Test · Debug loop** | One agent writes code, another writes tests, real Python runs them, and a debugger fixes failures. | ⭐⭐ medium |
| 7 | [rag_team_agent](rag_team_agent/) | **Multi-agent RAG (retrieve · answer · verify)** | One agent finds sources, one answers only from them, and a checker sends unsupported answers back. | ⭐⭐⭐ advanced |
| 8 | [swarm_agent](swarm_agent/) | **Swarm (peer-to-peer hand-offs)** | There is no boss — each agent decides who should take over next. | ⭐⭐⭐ advanced |
| 9 | [hierarchical_agent](hierarchical_agent/) | **Hierarchical teams (graphs inside a graph)** | A manager delegates to teams, and each team is its own small graph with workers and a lead. | ⭐⭐⭐ advanced |
| 10 | [blackboard_agent](blackboard_agent/) | **Blackboard (shared workspace)** | Specialists never talk to each other — they watch a shared board and add their part when they can. | ⭐⭐⭐ advanced |

Day 19 already covered four more patterns: **Router, Reflection, Supervisor, Human-in-the-loop**. Together you now know **14**.

## How to start (every folder works the same way)

1. Install **Python 3.10+** and **[Ollama](https://ollama.com/download)**, then run `ollama pull llama3.2` once.
2. Open a terminal **inside one folder** and read its **`HOW_TO_USE.md`** — exact commands, what to type, a **real** example session, experiments and fixes for common errors.
3. Open its **`architecture.html`** — click the steps to see which part of the diagram is working.

Every folder has the same files:

| File | Purpose |
|---|---|
| `HOW_TO_USE.md` | **Start here** — step-by-step guide, code tour, experiments, quiz |
| `agent.py` | The multi-agent graph (heavily commented) |
| `tools.py` | Tools and helper functions |
| `architecture.html` | Animated, clickable diagram with a step-by-step walkthrough |
| `prompt.md` | Every prompt used by the agents + a *build prompt* to recreate the agent with any AI |
| `prompt_nontechnical.md` | Plain-English explanation (good for non-programmers) |
| `README.md` | Short overview |
| `requirements.txt` | `langchain`, `langchain-ollama`, `langgraph` |

## Every `agent.py` has the same 5 parts

```
1. PROMPTS   one system prompt per role         (what each agent is told)
2. State     a TypedDict                         (the shared notebook all agents read & write)
3. Nodes     one function per agent / step       (read state → do work → return changes)
4. Graph     build_agent(): add_node + add_edge  (WHO runs, in WHAT order, with which loops)
5. ask/main  run the graph and talk to the user
```

Learn to read one file and you can read all ten.

## Which pattern should I use?

```
Do the steps ALWAYS happen in the same order?  ──yes──►  PIPELINE
        │ no
Are the jobs independent of each other?        ──yes──►  PARALLEL  (merge at the end)
        │ no
Does one answer need to be CHECKED / improved?
        ├─ by running real code  ─────────────────────►  CODER-TESTER
        ├─ against source documents  ─────────────────►  RAG TEAM
        ├─ by arguing both sides  ────────────────────►  DEBATE
        └─ by asking several judges  ─────────────────►  VOTING
Is it a long task that needs planning + tools?  ─────────►  PLANNER-EXECUTOR
Who decides what happens next?
        ├─ each agent decides  ───────────────────────►  SWARM
        ├─ a manager of teams  ───────────────────────►  HIERARCHICAL
        └─ nobody: rules on a shared board  ──────────►  BLACKBOARD
```

## Words you will meet

| Word | Meaning |
|---|---|
| **Node** | One step in the graph — usually one agent (one LLM call, maybe plus a tool). |
| **Edge** | An arrow: "after A, run B". |
| **Conditional edge** | An arrow chosen by a Python function: "if X go to B, else go to C". Loops are conditional edges that point backwards. |
| **State** | The shared notebook (a `TypedDict`) every node reads from and writes to. |
| **Tool** | A normal function the system can run (calculator, database lookup, Python runner). Tools give exact answers; LLMs give language. |
| **Fan-out / fan-in** | Start several nodes together / wait for all of them. |
| **Guard rail** | A plain-Python check that protects against a small model's mistakes (hop limits, validating a choice, verifying a verifier). |
| **ReAct agent** | An LLM that can decide to call tools in a loop (`create_react_agent`). |

## Tips for teachers

- Run the **same input** twice. The text changes but the *shape* of the run (which nodes, which order) should not — that is what we are studying.
- Each `HOW_TO_USE.md` ends with *Check yourself* questions and has 4 experiments with increasing difficulty.
- Small models fail sometimes. That is a feature for teaching: look at the guard rails in the code and ask *"what would go wrong without this line?"*
