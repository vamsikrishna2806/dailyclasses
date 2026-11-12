# Math Tutor Agent

A mathematics assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `solve_math` — symbolic computation via [SymPy](https://www.sympy.org/) (runs locally, no internet needed)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Solve x^2 - 9 = 0
- What is the derivative of x^3 + 2x?
- Integrate sin(x)
- Calculate sqrt(144) + 5^2
