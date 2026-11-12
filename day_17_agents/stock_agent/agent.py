from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_stock_price

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a stock market data assistant.
When a user asks about a stock, use the get_stock_price tool with the correct
ticker symbol (e.g. AAPL for Apple, TSLA for Tesla, RELIANCE.NS for Indian stocks).
Present the data clearly — price, change, and key stats.
Note: This is live market data for informational purposes only.
Never give financial advice or buy/sell recommendations."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.1)
    return create_react_agent(llm, [get_stock_price])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 50)
    print("  📈  Stock Agent  (Ollama + yfinance)")
    print("=" * 50)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: get_stock_price")
    print("  Try: 'What is Apple stock price?' or 'How is TSLA doing today?'\n")
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
