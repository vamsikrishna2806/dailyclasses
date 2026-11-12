# Air Quality Agent — Plain English Guide

## What does this agent do?

This agent checks the current air quality for any city in the world and tells you whether it's safe to go outside. It gives you the Air Quality Index (AQI) score plus a plain-English health recommendation.

## How to talk to it

Just ask naturally:

- "What is the air quality in Delhi?"
- "Is it safe to go outside in Beijing today?"
- "How is the pollution in Mumbai?"
- "Air quality in London?"
- "Should I wear a mask outside in Lahore?"

## How it works (simple version)

1. You ask about a city
2. The agent first finds the city's coordinates (latitude/longitude)
3. Then it fetches the latest air pollution measurements
4. It calculates the AQI and gives you health advice

## What is AQI?

AQI stands for **Air Quality Index**. It's a number from 0 to 500+ that tells you how clean or polluted the air is:

| AQI | Level | What it means |
|-----|-------|---------------|
| 0–50 | 🟢 Good | Safe for everyone |
| 51–100 | 🟡 Moderate | Generally fine; sensitive people be cautious |
| 101–150 | 🟠 Unhealthy for Some | Kids, elderly, and people with asthma: take care |
| 151–200 | 🔴 Unhealthy | Limit prolonged outdoor activity |
| 201–300 | 🟣 Very Unhealthy | Avoid outdoors if possible |
| 301+ | ⚫ Hazardous | Stay indoors! Use air purifier |

## What you get back

- AQI score and health category
- PM2.5 level (fine particles — the most harmful)
- PM10 level (coarser dust particles)
- Ozone (O₃), Nitrogen Dioxide (NO₂), Carbon Monoxide (CO)
- Plain-English health recommendation

## Example conversation

> **You:** How is the air quality in London?
>
> **Agent:** 🌱 **London Air Quality Report**
>
> AQI: 42 (Good ✅)
>
> | Pollutant | Level |
> |-----------|-------|
> | PM2.5 | 8.2 µg/m³ |
> | PM10 | 14.5 µg/m³ |
> | Ozone | 55.3 µg/m³ |
>
> The air quality in London is currently good. It is safe for all outdoor activities. Enjoy your day!

## Good to know

- Completely free, no account needed
- Works for cities worldwide
- Data updates hourly from weather stations
- Measurements are in µg/m³ (micrograms per cubic metre)

## Limitations

- Some very small towns may not have nearby measurement stations
- Not a medical device — consult a doctor for health decisions
- Data reflects the city centre; your local neighbourhood may differ
