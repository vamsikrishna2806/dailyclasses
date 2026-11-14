# Human-in-the-Loop Agent — Plain English Guide

## What does this agent do?

This agent is an **email assistant that always asks permission first**. It writes the email for you, then **stops and waits**. Nothing is sent until you say "approve". If you do not like it, tell it what to change and it writes a new version.

## How to talk to it

1. Say what the email is about:
   - "Ask Priya to move tomorrow's meeting to 3pm"
   - "Thank my teacher for the great class"
   - "Politely decline the invitation to the Saturday event"
2. Type the recipient's email address
3. Read the draft, then either:
   - type **approve** to send, or
   - type what to change, like **make it shorter** or **sound more formal**

## How it works (simple version)

1. You describe the email
2. The AI writes a draft
3. The agent **pauses** and shows you the draft
4. You approve — or give feedback and it rewrites
5. Only after you approve is the email "sent"

## Why does it pause?

Some actions cannot be undone — sending an email, paying money, deleting files. For those, a human should always have the last word. This pattern is called **human-in-the-loop**.

## Example conversation

> **You:** Ask Priya to move tomorrow's meeting to 3pm
>
> **Agent (draft):** Hi Priya, I was wondering if you could move tomorrow's meeting to 3pm...
>
> **You:** make it shorter
>
> **Agent (new draft):** Hi Priya, could you please move tomorrow's meeting to 3pm?...
>
> **You:** approve
>
> **Agent:** Email to priya@example.com saved in outbox.txt

## Good to know

- Free and runs on your own computer, no account needed
- This demo does NOT really send mail — it saves it in a file called `outbox.txt`
- You can ask for as many rewrites as you like

## Limitations

- Emails are only saved to a file, not delivered
- The draft ends with a placeholder like "[Your Name]" — edit it or ask the agent to change it
- Paused drafts are kept in memory only, so closing the program forgets them
