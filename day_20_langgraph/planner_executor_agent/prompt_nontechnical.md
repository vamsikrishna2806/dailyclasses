# Planner-Executor Agent — Plain English Guide

## What does this agent do?

This agent is like a **careful student with a calculator**. First they write down a plan on paper. Then they do one step at a time, pressing the buttons on a real calculator instead of guessing. At the end they write the answer in one sentence.

## How to talk to it

Type a small maths word problem:

- "I buy 3 pens at $2 and 4 notebooks at $5. How much in total?"
- "A shirt costs $40 and is 25% off. What do I pay?"

## How it works (simple version)

1. You give a word problem
2. The **planner** writes a numbered plan (no calculating yet)
3. The **executor** takes step 1, writes the calculation, and a real **calculator** computes it
4. Repeat for every step, using earlier results
5. The **answerer** writes the final answer in one sentence

## The team

- **Planner** — breaks the problem into small steps
- **Executor** — does one step at a time, asking the calculator tool
- **Calculator** — a tool — exact arithmetic, never wrong
- **Answerer** — turns the results into a clear sentence

## Example conversation

```
You:    I buy 3 pens at $2 and 4 notebooks at $5, then get 10% off. What do I pay?

[planner] plan:
  1. Multiply 3 pens by $2
  2. Multiply 4 notebooks by $5
  3. Add the two results
  4. Multiply the total by 0.9
[executor] step 1: CALC: 3 * 2  =>  6
[executor] step 2: CALC: 4 * 5  =>  20
[executor] step 3: CALC: 6 + 20  =>  26
[executor] step 4: CALC: 26 * 0.9  =>  23.4

Answer: You pay $23.40 after the 10% discount.
```

## Why is this useful?

Language models are bad at exact arithmetic but good at planning. Combining a planner with tools gives you the best of both — the basis of most serious AI agents.
