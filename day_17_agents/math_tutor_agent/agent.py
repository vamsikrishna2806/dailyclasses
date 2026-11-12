from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import solve_math

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a patient and encouraging mathematics tutor.
When a user asks a maths question, use the solve_math tool to compute the answer.
Then explain the solution step by step in simple language — how you got there,
what concept is involved, and why it works. Use the solve_math tool for:
  - Arithmetic: '2 + 2', '15% of 200'
  - Algebra: 'solve x^2 - 9', 'solve 2*x + 5 = 15'
  - Calculus: 'diff x^3 + 2*x', 'integrate sin(x)'
Make maths feel less scary and more logical."""


def build_agent():
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.2)
    return create_react_agent(llm, [solve_math])


def ask(agent, user_input):
    result = agent.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]})
    return result["messages"][-1].content


def main():
    print("=" * 52)
    print("  🧮  Math Tutor Agent  (Ollama + SymPy)")
    print("=" * 52)
    print(f"  Model: {OLLAMA_MODEL}  |  Tool: solve_math")
    print("  Try: 'Solve x^2 - 9 = 0' or 'What is the derivative of x^3?'\n")
    agent = build_agent()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKeep calculating!"); break
        if not user_input: continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Keep calculating!"); break
        print("\nAgent:", ask(agent, user_input), "\n")


if __name__ == "__main__":
    main()
