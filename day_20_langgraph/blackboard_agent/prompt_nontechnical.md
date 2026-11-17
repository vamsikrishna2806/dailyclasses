# Blackboard Agent — Plain English Guide

## What does this agent do?

This agent is like **a whiteboard in a meeting room**. The nutritionist writes dietary rules on it. When the chef sees rules on the board, they add a menu. When the shopper sees a menu, they add a shopping list. The auditor checks the cost — and if it is too high, wipes the menu off so the chef has to try again.

## How to talk to it

Describe meals and a budget:

- "Vegetarian dinners for 3 days under $20"
- "Cheap high-protein dinners under $25"

## How it works (simple version)

1. You describe the meals and the budget; it is written on the **board**
2. A plain-code **controller** asks: who can add something right now?
3. The **nutritionist** adds dietary rules
4. The **chef** sees the rules and adds a menu
5. The **shopper** sees the menu and adds a shopping list with a cost
6. The **auditor** compares cost and budget — too high? It erases the menu so the chef redoes it
7. When nobody can add anything new, you get the board's content

## The team

- **Controller** — not an AI — checks the rules and wakes a specialist
- **Nutritionist** — writes dietary rules
- **Chef** — plans the menu
- **Shopper** — makes the shopping list and cost
- **Auditor** — checks the budget, can erase the menu

## Example conversation

```
You:    Vegetarian dinners for 3 days under $20

[board] -> nutritionist
[board] -> chef
[board] -> shopper   (total $27.50)
[board] -> auditor   over budget -> erasing menu
[board] -> chef      (cheaper version)
[board] -> shopper   (total $17.00)
[board] -> auditor   APPROVED ✅
[board] -> DONE
```

## Why is this useful?

The blackboard pattern shines when many experts contribute to ONE growing result (diagnosis, design, planning) and you do not know in advance who will be needed or in what order.
