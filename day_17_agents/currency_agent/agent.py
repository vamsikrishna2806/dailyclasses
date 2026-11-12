from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import convert_currency

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a helpful currency and finance assistant.
When a user asks to convert money or asks about exchange rates, use the
convert_currency tool with the correct amount and currency codes (e.g. USD, EUR, INR, GBP, JPY).
Present the result clearly, mention the rate date, and add brief context
about the currencies involved if relevant."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.1)
    return create_react_agent(llm, [convert_currency])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 52)
    print("  💱  Currency Agent  (Ollama + Frankfurter.app)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: convert_currency")
    print("  Try: 'Convert 500 USD to INR' or '100 euros in Japanese yen'\n")
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
