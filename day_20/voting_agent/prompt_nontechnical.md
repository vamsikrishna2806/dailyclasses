# Voting Panel Agent — Plain English Guide

## What does this agent do?

This agent is like **a jury**. Three people with different temperaments read the same message and each vote *spam* or *not spam* and say why. Someone simply counts the hands. Only if they cannot agree does a judge step in.

## How to talk to it

Paste a short message:

- "URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1"
- "Hi Sam, are we still meeting for lunch at 1pm tomorrow?"

## How it works (simple version)

1. You paste a message
2. Three jurors read it **at the same time**
3. Each juror votes SPAM, NOT_SPAM or UNSURE with a short reason
4. A counter (plain code) tallies the votes
5. Two or more agree → that is the answer
6. No majority → a judge breaks the tie

## The team

- **Strict guard** — suspicious of everything
- **Friendly juror** — trusting, but not naive
- **Data analyst** — uses a tool that counts warning signs
- **Tally** — not an AI — counts votes
- **Judge** — only used for ties

## Example conversation

```
You:    URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1

[strict]   SPAM - Too good to be true, suspicious link and urgency.
[friendly] SPAM - Suspicious link and urgent tone are red flags.
[evidence] SPAM - Contains multiple warning signs.
[tally]    votes = {'SPAM': 3}  ->  SPAM

🚫 FINAL: SPAM   (decided by majority vote)
```

## Why is this useful?

Voting is a cheap way to make AI decisions more reliable — it is used for moderation, fraud checks and anywhere a single wrong answer is costly.
