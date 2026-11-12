# Math Tutor Agent — Plain English Guide

## What does this agent do?

This agent is your personal maths tutor. It can solve equations, calculate derivatives and integrals, and explain maths step by step in plain English. The best part: it runs entirely on your computer — no internet needed!

## How to talk to it

Just describe your problem naturally:

- "Solve x squared minus 9"
- "What is the derivative of x cubed?"
- "Integrate sin(x)"
- "What is 2 to the power of 10?"
- "Find the roots of x^2 + 5x + 6"
- "Differentiate 3x² + 2x + 1"
- "What is the integral of x² from 0 to 3?"

## How it works (simple version)

1. You describe a maths problem
2. The agent translates it into a formal expression
3. SymPy (a maths library) solves it exactly on your computer
4. The agent explains the answer step by step

**No internet needed** — all calculations happen locally on your machine.

## What it can solve

| Type | Example | Answer |
|------|---------|--------|
| Arithmetic | 2¹⁰ | 1024 |
| Algebra | x² - 9 = 0 | x = 3 or x = -3 |
| Derivatives | d/dx of x³ | 3x² |
| Integrals | ∫cos(x) dx | sin(x) + C |
| Simplification | 2x + 3x | 5x |

## Example conversations

> **You:** Solve x squared minus 16
>
> **Agent:** Solving x² - 16 = 0:
>
> Step 1: Move 16 to the other side: x² = 16
> Step 2: Take the square root of both sides: x = ±√16
> Step 3: √16 = 4
>
> **Answer: x = 4 or x = -4**
>
> This makes sense because 4² = 16 and (-4)² = 16. 

---

> **You:** What is the derivative of x cubed?
>
> **Agent:** The derivative of x³ is **3x²**.
>
> Using the power rule: d/dx(xⁿ) = n·xⁿ⁻¹
> So d/dx(x³) = 3·x³⁻¹ = 3x²

## Good to know

- Gives **exact** answers (not decimal approximations unless asked)
- Works with the variable `x` by default
- Completely free and runs offline — no internet required
- Great for school, university, or just satisfying curiosity

## Limitations

- Best for single-variable problems (default variable is x)
- Very complex multi-variable systems may need careful formatting
- It solves equations — it doesn't draw graphs (yet!)
- For complex word problems, you may need to convert them to equations first
