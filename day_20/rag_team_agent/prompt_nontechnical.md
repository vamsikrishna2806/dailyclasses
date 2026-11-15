# RAG Team Agent — Plain English Guide

## What does this agent do?

This agent is like **a librarian with a fact-checking colleague**. The librarian turns your question into search words and fetches the right pages. A writer answers using only those pages and quotes the page numbers. The colleague then checks every sentence against the pages — and if the pages do not contain the answer, the team honestly says so.

## How to talk to it

Ask the kind of question a new employee would ask:

- "How many vacation days do I get?"
- "Can I work from home?"
- "What is the CEO's salary?" (not in the handbook — watch it admit that!)

## How it works (simple version)

1. You ask a question
2. The **rewriter** turns it into search keywords
3. The **retriever** (plain code) pulls the best handbook passages
4. No passages? The team says it could not find the answer
5. The **answerer** replies using only those passages and cites them
6. The **checker** verifies every claim — unsupported answers go back for another try
7. You get a checked answer with sources

## The team

- **Rewriter** — makes good search keywords
- **Retriever** — not an AI — searches the handbook
- **Answerer** — answers only from the found passages
- **Checker** — makes sure nothing is invented

## Example conversation

```
You:    How many vacation days do I get?

[rewriter]  search keywords: vacation days annual leave
[retriever] found: ['HR-1']
[answerer]  You get 24 paid vacation days per year. [HR-1]
[checker]   GROUNDED

Answer: You get 24 paid vacation days per year. [HR-1]
   (✅ checked against the handbook)
```

## Why is this useful?

This is the pattern behind trustworthy company chatbots: answers come from *your* documents, with sources, and the bot admits when it does not know.
