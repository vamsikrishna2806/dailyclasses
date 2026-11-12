# Currency Agent — Plain English Guide

## What does this agent do?

This agent converts money between different currencies using live exchange rates. Ask it how much your money is worth in another country's currency and it will tell you instantly.

## How to talk to it

Just ask in plain English:

- "Convert 100 USD to EUR"
- "How much is 500 euros in Indian rupees?"
- "What is 1000 dollars in Japanese yen?"
- "Convert 200 pounds to Canadian dollars"

## How it works (simple version)

1. You tell it the amount and the two currencies
2. It fetches the latest exchange rate (updated daily from the European Central Bank)
3. It calculates the converted amount
4. It shows you the result with the rate used

## What you get back

- The converted amount
- The exchange rate (e.g., 1 USD = 83.50 INR)
- The date the rate is from

## Supported currencies (examples)

| Code | Currency |
|------|----------|
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| INR | Indian Rupee |
| JPY | Japanese Yen |
| AUD | Australian Dollar |
| CAD | Canadian Dollar |
| AED | UAE Dirham |

170+ currencies total — just ask!

## Example conversation

> **You:** Convert 1000 USD to JPY
>
> **Agent:** 1,000 USD = 149,250 JPY
> Exchange rate: 1 USD = 149.25 JPY (as of 2026-11-12)

## Good to know

- Rates update **daily** (not real-time tick-by-tick)
- Completely free, no account or API key needed
- Uses European Central Bank official reference rates
- You can say "dollars", "euros", "rupees" and it will understand

## Limitations

- Not for trading — rates are daily reference rates, not live market prices
- Does not include bank fees or spreads (actual exchange at a bank may differ)
- Cryptocurrency is not supported
