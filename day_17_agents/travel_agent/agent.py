from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from tools import get_destination_info

# Change to any model you have pulled: llama3.2, mistral, qwen2.5, etc.
OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a friendly and knowledgeable travel assistant.
When a user asks about a travel destination, use the get_destination_info tool
to fetch real-time weather and conditions. Based on the data, give helpful,
concise travel advice — what to pack, best activities, and anything relevant
for the trip. Always be encouraging and practical."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    tools = [get_destination_info]
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
    print("=" * 55)
    print("  🌍  Travel Agent  (Ollama + LangGraph + Open-Meteo)")
    print("=" * 55)
    print(f"  Model : {OLLAMA_MODEL}")
    print(f"  Tool  : get_destination_info (Open-Meteo — free)")
    print("  Type 'quit' to exit\n")

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
            print("Safe travels!")
            break

        print("\nAgent: ", end="", flush=True)
        response = ask(agent, user_input)
        print(response)
        print()


if __name__ == "__main__":
    main()
