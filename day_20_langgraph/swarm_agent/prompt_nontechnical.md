# Swarm Agent — Plain English Guide

## What does this agent do?

This agent is like a **shop help desk where staff pass your call on**. The receptionist listens to you, then says "let me put you through to Orders". Orders checks your parcel, and if you want a refund, hands you to the Refunds desk. There is no manager directing traffic — each person knows who should help next.

## How to talk to it

Write like a customer and include a 4-digit order number (5001, 5002 or 5003):

- "Order 5001 arrived broken, I want my money back"
- "Where is my order 5002?"

## How it works (simple version)

1. You write a message
2. **Triage** says hello and passes you to **Orders**
3. **Orders** looks up your order with a tool and explains its status
4. If you want a refund and the order is delivered, Orders passes you to **Refunds**
5. **Refunds** processes it with a tool and confirms
6. The last agent says `DONE` and the conversation ends

## The team

- **Triage** — front desk, decides who helps
- **Orders** — looks up order status
- **Refunds** — issues refunds for delivered orders

## Example conversation

```
You:    Order 5001 arrived broken, I want my money back

[triage]  Sorry to hear that — passing you to our orders team.
   ↪ hands off to: orders
[orders]  Your laptop stand was delivered on 2026-11-02; I'll pass you to refunds.
   ↪ hands off to: refunds
[refunds] Refund approved: $39.00 returns to your card in 3-5 days.
   ↪ hands off to: done
```

## Why is this useful?

Hand-offs are how real support systems work, and they make it easy to grow: adding a new department is just adding one agent and one rule.
