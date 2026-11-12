from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import search_github_repos

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a helpful open-source code discovery assistant.
When a user asks about code, libraries, or projects on GitHub, use the
search_github_repos tool to find the best repositories.
Summarise the top results, explain what each project does, highlight star counts
as a measure of popularity, and recommend which one might be best for the user's needs."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    return create_react_agent(llm, [search_github_repos])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 54)
    print("  🐙  GitHub Agent  (Ollama + GitHub Public API)")
    print("=" * 54)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: search_github_repos")
    print("  Try: 'Find the best Python web frameworks' or 'LangChain repos'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHappy coding!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Happy coding!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
