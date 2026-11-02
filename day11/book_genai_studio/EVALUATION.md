# Evaluation: user testing, feedback and prompt iteration

The goal: prove with evidence that outputs are good, and get better each round.

## 1. Run a user-testing session (30 min per person, 5 people is enough to find most problems)

**Setup:** deployed URL, sample book loaded, a book the tester chose, screen recording on (with consent).

**Tasks to give the tester (don't help them):**

1. Upload a book of your choice. *(Watch: do they understand the upload status? Any errors?)*
2. Get a short summary of one chapter, then of the whole book.
3. Ask the book 3 questions, including one follow-up like “why did she do that?”.
4. Click a source tag `[S1]`. Does the passage really support the answer?
5. Make a quiz from one chapter. Copy it somewhere.
6. Rate every output with stars and write one comment.

**Ask after:** What was confusing? Which output would you actually use? What was wrong or made up?

## 2. What to measure

| Metric | How | Target |
|---|---|---|
| Avg rating per prompt version | Prompt Lab table | ≥ 4.0 ★ |
| % happy (4–5 ★) | Prompt Lab table | ≥ 75% |
| Grounded answers | For 20 questions, check each `[S#]` passage supports the claim | ≥ 90% |
| “Not in the book” honesty | Ask 5 questions the book doesn't answer | 5/5 say so |
| Blind A/B wins | Prompt Lab → Blind compare, 20+ votes | new version wins > 55% |
| Cost per feature | Usage tab | know it, keep it low |
| Speed | Usage tab avg response | < 5 s for chat start |
| Errors | Usage tab errors | 0 unexplained |

## 3. The prompt iteration loop

1. Read the low-rated outputs and comments (Export feedback CSV).
2. Group complaints: *too long*, *invented facts*, *missing names*, *boring*, *wrong format*…
3. Write a new version in `app/prompts.py` (e.g. `"v3"`) that fixes the top complaint. Change **one thing** at a time.
4. Run blind compares (v2 vs v3) on the same chapters; collect 20+ votes.
5. Keep the winner. Write what changed and why in the log below.

## 4. Iteration log (fill this in)

| Date | Feature | Change | Why (feedback) | Result |
|---|---|---|---|---|
| example | qa | v1 → v2: require `[S#]` citations, say “couldn't find it” instead of guessing | Testers couldn't tell if answers were made up | v2 avg 4.4★ vs v1 3.1★ (n=24) |
| | | | | |
