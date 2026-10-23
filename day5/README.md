# ChatGPT Question & Answer Web Application

A responsive modern web application built with Vanilla HTML, CSS, and JavaScript that sends questions to the OpenAI ChatGPT API and displays the assistant's response.

## Features & Implementation

### ✅ Task 1: UI with Question Textbox and Submit Button
- **Question Textbox** (`#question-textbox`): Multi-line input area with placeholder instructions, live character counter, and clear button.
- **Submit Button** (`#submit-btn`): Styled interactive button with gradient glow, hover animations, and loading spinner state.
- **Keyboard Shortcut**: Press `Ctrl + Enter` (or `Cmd + Enter`) anywhere inside the question box to submit immediately.
- **Sample Questions**: Clickable quick chips at the bottom to test questions with a single click.

### ✅ Task 2: Calling the ChatGPT API
- **Direct OpenAI Chat Completions Integration**:
  - Endpoint: `https://api.openai.com/v1/chat/completions`
  - Dynamic Model Selection: Supports `gpt-4o-mini`, `gpt-4o`, and `gpt-3.5-turbo`.
  - Secure Local Key Management: Stores API key in memory / browser `localStorage` without exposing it to any external server.
  - Robust Error Handling: Explicit status checks, 60s timeout handling (`AbortController`), and informative toast notifications.

### ✅ Task 3: Putting the Response in the Answer Textbox
- **Answer Textbox** (`#answer-textbox`): Automatically populated with the response received from `choices[0].message.content`.
- **Response Metrics**: Live response time tracking (e.g. `1.24s`), character count, model identifier, and timestamp.
- **Copy to Clipboard** (`#copy-btn`): Single-click copy button with real-time visual feedback.

---

## How to Run

### Method 1: Open Directly in Browser
Simply double-click `index.html` or open it with any web browser (Chrome, Edge, Firefox, Safari).

### Method 2: Serve Locally with Python
```powershell
python -m http.server 3000
```
Then navigate to: `http://localhost:3000`

### Method 3: Serve Locally with Node `npx serve`
```powershell
npx serve .
```

---

## How to Use
1. Open the application.
2. In the **API Configuration** card at the top, enter your OpenAI API Key (`sk-...`).
3. Type your question in the **Question** textbox or pick one of the quick suggestions.
4. Click **Submit Question** (or press `Ctrl + Enter`).
5. Watch the real-time loading state as ChatGPT processes your query.
6. The answer will be displayed in the **Answer** textbox!
