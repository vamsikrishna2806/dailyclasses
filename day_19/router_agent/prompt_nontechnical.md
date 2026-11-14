# Router Agent — Plain English Guide

## What does this agent do?

This agent works like the **front desk of a company**. You ask a question, and the front desk quickly decides which department should answer it — billing, tech support, or general help. Then the right specialist replies.

## How to talk to it

Just ask naturally:

- "Is invoice 1002 paid?"
- "Can I get a refund for last month?"
- "My wifi keeps dropping"
- "I forgot my password"
- "What are your opening hours?"

## How it works (simple version)

1. You ask a question
2. A "router" reads it and picks the best department (it does NOT answer)
3. That one specialist looks things up with its own tools
4. You get the answer — and you can see which department was chosen

## The three departments

- **Billing** — checks invoices (amount and whether it is paid)
- **Tech Support** — finds fixes for wifi, passwords and crashes
- **General** — greetings, opening hours and everything else

## Example conversation

> **You:** Is invoice 1002 paid?
>
> *[router] → billing*
>
> **Agent:** Invoice 1002 is for $120.00 and has been overdue since 2026-10-20.

## Good to know

- Completely free and runs on your own computer — no account needed
- You can watch the routing decision printed before every answer
- Try questions that could fit two departments and see what the router chooses

## Limitations

- Uses small demo data (invoices 1001 and 1002; help topics wifi, password, crash)
- A small AI model can occasionally pick the wrong department
- Only one department answers each question
