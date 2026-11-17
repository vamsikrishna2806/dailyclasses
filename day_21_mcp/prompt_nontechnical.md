# MCP explained without jargon

## The one-sentence version
**MCP is a universal plug that lets an AI assistant use outside tools and information,** like a USB-C port, but for AI.

## The restaurant story 🍽️
| In the restaurant | In MCP |
|---|---|
| **You**, the customer | the user |
| **The waiter**, who takes your order and brings the food | the *host app* (Claude Desktop, or our agent program) |
| **The chef**, who decides what to cook | the *AI model* (Llama, Claude…) |
| **The order slip**, always in the same format | the *MCP message* |
| **Suppliers**: the bakery, the farm, the fish market | the *MCP servers* (weather, time, notes…) |
| The bakery's own oven and recipes | the real systems behind servers (a weather website, a database) |

The chef never leaves the kitchen to go to the bakery. The chef writes an order slip, and the waiter's system sends it.
Because **every supplier understands the same order slip**, the restaurant can add a new supplier any time without retraining the chef.

## What our agent can do (and which "supplier" it uses)
| You ask… | It asks this server | Is the data live? |
|---|---|---|
| "What's the weather in Hyderabad?" | Weather (uses the free Open-Meteo service) | ✅ yes, right now |
| "What time is it in Tokyo?" | Time (an official MCP server) | ✅ yes |
| "What's 23 × 19?" | Math (we built it) | — |
| "Summarise this web page…" | Fetch (an official MCP server) | ✅ yes |
| "What is the LangGraph project on GitHub?" | DeepWiki (a public server on the internet) | ✅ yes |
| "Save a note…" | Notes (we built it) | — |

## Why it matters
- **Before MCP:** every AI app had to build its own connection to every tool. 5 apps × 10 tools = 50 pieces of custom work.
- **With MCP:** each app learns MCP once, and each tool learns MCP once. 5 + 10 = 15.

## Is it safe?
An MCP server is a program, so only install ones you trust. Our agent prints every action it takes (`-> [agent] calls ...`), so you can always see what it's doing.

## Try it (plain-language prompts)
- "Is it hot in Hyderabad right now?"
- "If it's 9 in the morning in New York, what time is it in India?"
- "Tell me the 3-day forecast for Paris and save it as a note."
