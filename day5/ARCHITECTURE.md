# Application Architecture - ChatGPT Q&A Assistant

This document outlines the architecture, component interaction, and data flow of the ChatGPT Q&A Web Application.

---

## 1. System Architecture Diagram

```
+===================================================================================+
|                               USER BROWSER / CLIENT                               |
+===================================================================================+
|                                                                                   |
|  [ PRESENTATION LAYER (index.html + style.css) ]                                  |
|  +-----------------------------------------------------------------------------+  |
|  |  +------------------------ API Config Drawer ----------------------------+  |  |
|  |  |  [API Key Input] (Masked)    [Model Select] (gpt-4o-mini / gpt-4o)     |  |  |
|  |  +-----------------------------------------------------------------------+  |  |
|  |                                                                             |  |
|  |  +---- Task 1: Question Section -----+  +---- Task 3: Answer Section -----+ |  |
|  |  |  [ Question Textbox ]             |  |  [ Answer Textbox (Readonly) ]  | |  |
|  |  |  - Text input (Ctrl+Enter)        |  |  - Displays AI response         | |  |
|  |  |  - Char Counter                   |  |  - Metrics (Time, Tokens)       | |  |
|  |  |  - [ Clear Button ]               |  |  - [ Copy to Clipboard Button ] | |  |
|  |  |  - [ Submit Button 🚀 ]           |  |                                 | |  |
|  |  +-----------------------------------+  +---------------------------------+ |  |
|  |                                                                             |  |
|  |  [ Toast & Notification Container ] (Feedback, errors & success alerts)     |  |
|  +-----------------------------------------------------------------------------+  |
|                                       |                                           |
|                                  DOM Events                                       |
|                                       v                                           |
|  [ LOGIC & CONTROLLER LAYER (app.js) ]                                            |
|  +-----------------------------------------------------------------------------+  |
|  |  - Event Handlers (click, input, keydown)                                   |  |
|  |  - Form Validator & Loading State Controller (disable inputs, spinner)       |  |
|  |  - Toast Notification Dispatcher                                            |  |
|  |  - API Request Engine (Fetch API + AbortController with 60s timeout guard)  |  |
|  +-----------------------------------------------------------------------------+  |
|                 |                                             |                   |
|          Local Read/Write                              HTTPS Fetch                |
|                 v                                             v                   |
|  +-------------------------------+                            |                   |
|  |  Browser localStorage         |                            |                   |
|  |  (Caches API Key securely)    |                            |                   |
|  +-------------------------------+                            |                   |
+===============================================================|===================+
                                                                |
                                             POST /v1/chat/completions
                                             Authorization: Bearer <API_KEY>
                                             Payload: { model, messages, temp }
                                                                |
                                                                v
+===================================================================================+
|                              EXTERNAL AI CLOUD (OpenAI)                           |
+===================================================================================+
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | OpenAI Gateway & Auth Check (Validates Bearer token & rate limits)          |  |
|  +-----------------------------------------------------------------------------+  |
|                                       |                                           |
|                                       v                                           |
|  +-----------------------------------------------------------------------------+  |
|  | LLM Inference Engine (GPT-4o-mini / GPT-4o / GPT-3.5-Turbo)                 |  |
|  +-----------------------------------------------------------------------------+  |
|                                       |                                           |
|                                       v                                           |
|  +-----------------------------------------------------------------------------+  |
|  | JSON Response Generator ({ choices: [{ message: { content } }], usage })    |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
+===================================================================================+
```

---

## 2. Sequence & Data Flow Diagram

```
User               index.html / DOM            app.js                  OpenAI API
 |                        |                      |                         |
 |--- 1. Enters Question->|                      |                         |
 |--- 2. Clicks Submit--->|                      |                         |
 |                        |--- 3. Submit Event ->|                         |
 |                        |                      |-- 4. Validate Inputs    |
 |                        |                      |-- 5. Read API Key       |
 |                        |<-- 6. UI: Loading ---|                         |
 |                        |   (Spinner & Lock)   |                         |
 |                        |                      |--- 7. HTTPS POST ------>|
 |                        |                      |    /chat/completions    |
 |                        |                      |                         |-- 8. LLM Inference
 |                        |                      |<-- 9. HTTP 200 (JSON) --|
 |                        |                      |                         |
 |                        |<-- 10. Write Answer -|                         |
 |                        |    to Answer Box     |                         |
 |                        |<-- 11. Reset State --|                         |
 |                        |    & Show Toast      |                         |
 |<-- 12. Reads Answer ---|                      |                         |
```

---

## 3. Layer Breakdown

### A. Presentation Layer (`index.html` & `style.css`)
- **Semantic Structure**: Modern HTML5 layout dividing the application into header branding, configuration drawer, question card (Task 1), answer card (Task 3), sample suggestion chips, and toast container.
- **Glassmorphic Styling**: Ambient background gradients, responsive 2-column grid collapsing gracefully to single column on mobile/tablet viewports.
- **Interactive Feedback**: Real-time character counters, animated button loading spinners, and focus rings.

### B. Logic & Controller Layer (`app.js`)
- **State Management**: Tracks request pending state, input validity, and elapsed response times.
- **Task 1 Execution**: Listens for click events on `#submit-btn` and `Ctrl + Enter` / `Cmd + Enter` hotkeys on `#question-textbox`.
- **Task 2 Execution**: Issues asynchronous requests to `https://api.openai.com/v1/chat/completions` using the Fetch API with:
  - Dynamic model selection (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`)
  - Bearer token authentication
  - Request timeout guard via `AbortController` (60s limit)
  - Detailed error mapping (quota exhaustion, invalid keys, server timeouts)
- **Task 3 Execution**: Extracts `choices[0].message.content`, populates the `#answer-textbox`, computes character count and response time, and restores button states.

### C. Persistence Layer (Browser `localStorage`)
- Caches the user's OpenAI API key under the key `chatgpt_qa_api_key` for convenience between sessions.
- Key remains strictly client-side and is never sent to intermediate servers.

### D. External Services (OpenAI API)
- Remote inference server evaluating prompts and returning structured JSON payloads containing generated answers, token metrics, and model signatures.

---

## 4. Key Architectural Decisions

1. **Client-Side Serverless Design**: Runs directly in any web browser without requiring a backend runtime (e.g. Node.js or Python), minimizing deployment overhead.
2. **Defensive Error Handling**: All network requests are wrapped in `try...catch` blocks with explicit checks for HTTP status codes, network errors, and abort timeouts.
3. **Clipboard Integration**: Uses modern `navigator.clipboard.writeText()` with an automatic fallback for legacy browser compatibility.
