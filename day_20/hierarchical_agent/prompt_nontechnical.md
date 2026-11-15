# Hierarchical Agent — Plain English Guide

## What does this agent do?

This agent is like a **small company**. A manager does not do the work — they ask the Product team first, then the Marketing team. Inside each team, a couple of workers do their parts and a team lead sums it all up for the manager.

## How to talk to it

Type a product idea in a few words:

- "a note-taking app"
- "a language learning app"
- "a budget tracker for students"

## How it works (simple version)

1. You give a product idea
2. The **manager** sends the **product team**
3. Researcher finds the audience → spec writer lists features → product lead writes the spec
4. The team reports back; the manager sends the **marketing team**
5. Copywriter writes the tagline → social planner writes posts → marketing lead assembles the campaign
6. The manager sees both teams are done and hands you the launch kit

## The team

- **Manager** — decides which team works next, never does the work
- **Product team** — researcher, spec writer, product lead
- **Marketing team** — copywriter, social planner, marketing lead

## Example conversation

```
You:    a note-taking app

🏢 [manager] -> product
    [researcher] asking the audience tool...
    [spec_writer] drafting features...
    [product_lead] merging into the product spec...
🏢 [manager] -> marketing
    [copywriter] writing tagline + pitch...
    [social_planner] writing social posts...
    [marketing_lead] assembling the campaign...
🏢 [manager] -> FINISH

PRODUCT SPEC: fast search, offline mode, sync ...
CAMPAIGN: "Organize Your Thoughts, Anywhere" ...
```

## Why is this useful?

Real organisations are hierarchical, and so are large AI systems. Nesting lets you grow from 3 agents to 30 without losing track of what is going on.
