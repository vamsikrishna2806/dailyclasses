from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import define_word

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a knowledgeable vocabulary and language assistant.
When a user asks about a word, use the define_word tool to look it up.
Explain the definition clearly, highlight interesting usage, provide examples
in context, and suggest when and how to use the word naturally in conversation.
Help users expand their vocabulary in an engaging way."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    return create_react_agent(llm, [define_word])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 50)
    print("  📖  Dictionary Agent  (Ollama + Free Dictionary API)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: define_word")
    print("  Try: 'What does ephemeral mean?' or 'Define serendipity'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKeep learning!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Keep learning!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
