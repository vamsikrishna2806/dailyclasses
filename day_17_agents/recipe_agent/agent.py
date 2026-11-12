from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import search_recipe

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a friendly and passionate chef assistant.
When a user asks for a recipe or cooking help, use the search_recipe tool to find it.
Present the ingredients clearly, explain the steps in simple language, and add
helpful cooking tips — substitutions, serving suggestions, or difficulty notes.
Make cooking feel approachable and fun for everyone."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.4)
    return create_react_agent(llm, [search_recipe])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 50)
    print("  🍳  Recipe Agent  (Ollama + TheMealDB)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: search_recipe")
    print("  Try: 'How do I make biryani?' or 'Give me a pasta recipe'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHappy cooking!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Happy cooking!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
