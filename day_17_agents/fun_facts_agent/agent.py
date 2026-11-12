from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_joke, get_number_fact

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a cheerful and witty entertainment assistant.
You have two tools: get_joke to fetch jokes (categories: Any, Programming, Pun, Misc)
and get_number_fact to get interesting facts about numbers.
When someone asks for a joke, fetch one and add a fun reaction.
When someone asks about a number, fetch the fact and explain why it's interesting.
Keep the energy light, playful, and fun!"""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.7)
    return create_react_agent(llm, [get_joke, get_number_fact])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 52)
    print("  🎉  Fun Facts Agent  (Ollama + JokeAPI + NumbersAPI)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Tools: get_joke, get_number_fact")
    print("  Try: 'Tell me a programming joke' or 'Give me a fact about 42'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStay fun!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Stay fun!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
