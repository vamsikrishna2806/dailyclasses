# Coder-Tester Agent — Plain English Guide

## What does this agent do?

This agent is like a **tiny software team**. One person writes the code, another writes the checks, then a real computer runs the checks. If something fails, a third person reads the error message and repairs the code, and the checks are run again.

## How to talk to it

Describe one small function and give it a name:

- "is_palindrome(s) that ignores case and spaces"
- "fizzbuzz(n) returning a list of strings"

## How it works (simple version)

1. You describe a function
2. The **coder** writes it
3. The **tester** writes a few checks (asserts)
4. A **real Python process** runs the code with the checks
5. If something fails, the **debugger** reads the error and fixes the code — then it is tested again
6. When all checks pass (or after 3 fixes) you get the code

## The team

- **Coder** — writes the function
- **Tester** — writes the checks
- **Runner** — not an AI — real Python that runs everything
- **Debugger** — reads error messages and repairs the code

## Example conversation

```
You:    is_palindrome(s) that ignores case and spaces

[coder]    writing the function...
[tester]   writing asserts...
[runner]   ✅ all tests passed

✅ PASSED all tests
--- code ---
def is_palindrome(s):
    s = ''.join(c for c in s if c.isalnum()).lower()
    return s == s[::-1]
```

## Why is this useful?

Checking AI output with real tools is the single best way to make agents reliable. The same idea powers coding assistants that run your test-suite automatically.
