from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_country_info

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are an expert geography and world knowledge assistant.
When a user asks about a country, use the get_country_info tool to fetch the facts.
Present the data in a clear and interesting way — highlight the country's culture,
significance, interesting facts about its size or population, and anything that
makes it unique. Make geography feel fascinating."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    return create_react_agent(llm, [get_country_info])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 54)
    print("  🌐  Country Info Agent  (Ollama + RestCountries API)")
    print("=" * 54)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: get_country_info")
    print("  Try: 'Tell me about Japan' or 'What language do they speak in Brazil?'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
