from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from tools import web_search

# Change to any model you have pulled: llama3.2, mistral, qwen2.5, etc.
OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are an expert political analyst and geopolitical strategist.
Your role is to analyze political scenarios, current events, elections, policy decisions,
international relations, and world affairs with clarity and balance.

When analyzing a scenario:
1. Use the web_search tool to find current, factual information.
2. Present multiple perspectives without personal bias.
3. Explain the key players, their motivations, and likely outcomes.
4. Highlight risks, opportunities, and historical context where relevant.
5. Keep your analysis concise, structured, and evidence-based.

Always cite your sources by mentioning where you found the information."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    tools = [web_search]
    agent = create_react_agent(llm, tools)
    return agent


def ask(agent, user_input: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content


def main():
    print("=" * 58)
    print("  🏛️  Political Scenario Agent  (Ollama + DuckDuckGo)")
    print("=" * 58)
    print(f"  Model  : {OLLAMA_MODEL}")
    print(f"  Tool   : web_search (DuckDuckGo — free, no API key)")
    print("  Type 'quit' to exit\n")
    print("  Example queries:")
    print("  - What is the current political situation in France?")
    print("  - Analyze the impact of US-China trade tensions.")
    print("  - What are the key issues in the upcoming UK elections?\n")

    agent = build_agent()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Stay informed!")
            break

        print("\nAgent: ", end="", flush=True)
        response = ask(agent, user_input)
        print(response)
        print()


if __name__ == "__main__":
    main()
