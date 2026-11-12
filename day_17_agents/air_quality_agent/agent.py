from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_air_quality

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a helpful environmental health assistant.
When a user asks about air quality in a city, use the get_air_quality tool.
Explain the AQI reading in plain language — what it means for daily activities,
who might be most affected (children, elderly, people with asthma), and practical
advice like whether to exercise outdoors, wear a mask, or keep windows closed.
Be clear, caring, and actionable."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    return create_react_agent(llm, [get_air_quality])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 56)
    print("  🌿  Air Quality Agent  (Ollama + Open-Meteo AQ API)")
    print("=" * 56)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: get_air_quality")
    print("  Try: 'Is the air safe in Delhi today?' or 'Air quality in London'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBreath easy!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Breathe easy!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
