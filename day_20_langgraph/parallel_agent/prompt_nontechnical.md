# Parallel Agent — Plain English Guide

## What does this agent do?

This agent is like a **travel agency with three clerks**. You ask for a trip and all three clerks start at once — one checks flights, one hotels, one activities. Only when all three are done does the manager combine their notes into one plan.

## How to talk to it

Type a city (one of Paris, Tokyo, Goa, New York):

- "Paris"
- "Goa"
- "I want to visit Tokyo"

## How it works (simple version)

1. You name a city
2. Flights, hotels and activities specialists all start **at the same time**
3. Each one looks up its own information with its own tool
4. The planner **waits until all three are done**
5. The planner merges everything into a 3-day itinerary with a budget tip

## The team

- **Flights specialist** — finds flight options
- **Hotels specialist** — finds places to stay
- **Activities specialist** — finds things to do
- **Planner** — merges the three reports into one plan

## Example conversation

```
You:    Paris

[activities] searching...
[flights]    searching...
[hotels]     searching...
[planner]    all 3 reports arrived — merging into one plan

Day 1: Arrive in Paris, check in to Hostel Seine, walk around Montmartre.
Day 2: Louvre Museum, then an evening Seine cruise.
Day 3: Eiffel Tower.
Budget tip: Budget Air ($310) and Hostel Seine ($45/night) are the cheapest.
```

## Why is this useful?

Any time you have several independent lookups (search many sources, check many files, ask many experts) running them in parallel saves time, and the merge step gives one clean answer.
