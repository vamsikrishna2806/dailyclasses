from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import search_wikipedia

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a knowledgeable research assistant with access to Wikipedia.
When a user asks about any topic, person, event, or concept, use the search_wikipedia
tool to get factual information. Summarise clearly, highlight the most important points,
and add context to make the information meaningful. Always mention the Wikipedia source URL."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    return create_react_agent(llm, [search_wikipedia])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 52)
    print("  📚  Wikipedia Agent  (Ollama + Wikipedia API)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: search_wikipedia")
    print("  Try: 'Who is Marie Curie?' or 'Explain the French Revolution'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKeep exploring!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Keep exploring!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
