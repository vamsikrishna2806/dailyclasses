/**
 * ChatGPT Q&A Assistant
 * Implementation of Task 1, Task 2, and Task 3
 */

document.addEventListener('DOMContentLoaded', () => {
  // =========================================================================
  // DOM Elements
  // =========================================================================
  // Config elements
  const configToggleBtn = document.getElementById('config-toggle-btn');
  const configContent = document.getElementById('config-content');
  const configChevron = document.getElementById('config-chevron');
  const apiKeyInput = document.getElementById('api-key-input');
  const toggleKeyVisibilityBtn = document.getElementById('toggle-key-visibility-btn');
  const apiStatusBadge = document.getElementById('api-status-badge');
  const modelSelect = document.getElementById('model-select');

  // Task 1: Question Elements & Submit Button
  const questionTextbox = document.getElementById('question-textbox');
  const questionCharCount = document.getElementById('question-char-count');
  const clearQuestionBtn = document.getElementById('clear-question-btn');
  const submitBtn = document.getElementById('submit-btn');
  const networkStatus = document.getElementById('network-status');
  const networkStatusText = document.getElementById('network-status-text');

  // Task 3: Answer Elements
  const answerTextbox = document.getElementById('answer-textbox');
  const answerCharCount = document.getElementById('answer-char-count');
  const responseTimeBadge = document.getElementById('response-time-badge');
  const copyBtn = document.getElementById('copy-btn');
  const copyText = document.getElementById('copy-text');
  const modelUsedTag = document.getElementById('model-used-tag');
  const timestampTag = document.getElementById('timestamp-tag');

  // Suggestions & Toasts
  const chipButtons = document.querySelectorAll('.chip-btn');
  const toastContainer = document.getElementById('toast-container');

  // =========================================================================
  // State Management
  // =========================================================================
  const STORAGE_KEY = 'chatgpt_qa_api_key';
  let isRequestPending = false;

  // Initialize stored API key if available
  const savedKey = localStorage.getItem(STORAGE_KEY);
  if (savedKey) {
    apiKeyInput.value = savedKey;
    updateKeyBadge(true);
  } else {
    updateKeyBadge(false);
  }

  // =========================================================================
  // UI Helpers & Notifications
  // =========================================================================
  function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Choose icon
    let iconSvg = '';
    if (type === 'error') {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    } else if (type === 'success') {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
    } else {
      iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.6rem;">
        ${iconSvg}
        <span>${message}</span>
      </div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px) scale(0.95)';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }

  function updateKeyBadge(hasKey) {
    if (hasKey) {
      apiStatusBadge.textContent = 'API Key Configured';
      apiStatusBadge.classList.add('active');
    } else {
      apiStatusBadge.textContent = 'API Key Needed';
      apiStatusBadge.classList.remove('active');
    }
  }

  function setStatus(state, message) {
    const dot = networkStatus.querySelector('.indicator-dot');
    dot.className = `indicator-dot ${state}`;
    networkStatusText.textContent = message;
  }

  // =========================================================================
  // Config & API Key Handling
  // =========================================================================
  configToggleBtn.addEventListener('click', () => {
    configContent.classList.toggle('collapsed');
    configChevron.classList.toggle('rotated');
  });

  apiKeyInput.addEventListener('input', (e) => {
    const key = e.target.value.trim();
    if (key.length > 0) {
      localStorage.setItem(STORAGE_KEY, key);
      updateKeyBadge(true);
    } else {
      localStorage.removeItem(STORAGE_KEY);
      updateKeyBadge(false);
    }
  });

  toggleKeyVisibilityBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleKeyVisibilityBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
          <line x1="1" y1="1" x2="23" y2="23"></line>
        </svg>
      `;
    } else {
      apiKeyInput.type = 'password';
      toggleKeyVisibilityBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
      `;
    }
  });

  // =========================================================================
  // TASK 1: Question Textbox & UI Event Handlers
  // =========================================================================
  // Character count updates
  questionTextbox.addEventListener('input', () => {
    const len = questionTextbox.value.length;
    questionCharCount.textContent = `${len.toLocaleString()} character${len === 1 ? '' : 's'}`;
  });

  // Clear button
  clearQuestionBtn.addEventListener('click', () => {
    questionTextbox.value = '';
    questionCharCount.textContent = '0 characters';
    questionTextbox.focus();
  });

  // Shortcut: Ctrl + Enter to submit
  questionTextbox.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  });

  // Sample prompt chips
  chipButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const prompt = btn.getAttribute('data-prompt');
      questionTextbox.value = prompt;
      questionCharCount.textContent = `${prompt.length} characters`;
      questionTextbox.focus();
      showToast('Sample question loaded!', 'info', 2000);
    });
  });

  // Submit button click handler
  submitBtn.addEventListener('click', handleSubmit);

  // =========================================================================
  // TASK 2: Calling the ChatGPT API
  // =========================================================================
  async function callChatGPTAPI(apiKey, model, question) {
    const endpoint = 'https://api.openai.com/v1/chat/completions';

    const payload = {
      model: model,
      messages: [
        {
          role: 'system',
          content: 'You are a knowledgeable, concise, and helpful AI assistant. Provide direct, structured, and insightful answers.'
        },
        {
          role: 'user',
          content: question
        }
      ],
      temperature: 0.7
    };

    // Controller for request timeout (60 seconds)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        // Detailed error messages based on OpenAI error schema
        const errorMsg = data?.error?.message || `Server returned error status ${response.status}`;
        throw new Error(errorMsg);
      }

      // Return the assistant's reply text
      if (data.choices && data.choices.length > 0 && data.choices[0].message) {
        return {
          content: data.choices[0].message.content,
          model: data.model || model,
          usage: data.usage
        };
      } else {
        throw new Error('No answer choice was returned by ChatGPT API.');
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out after 60 seconds. Please check your connection.');
      }
      throw error;
    }
  }

  // =========================================================================
  // TASK 3: Main Submission Flow & Populating Answer Textbox
  // =========================================================================
  async function handleSubmit() {
    if (isRequestPending) return;

    const question = questionTextbox.value.trim();
    if (!question) {
      showToast('Please enter a question before submitting.', 'error');
      questionTextbox.focus();
      return;
    }

    const apiKey = (apiKeyInput.value || '').trim();
    if (!apiKey) {
      showToast('Please provide your OpenAI API key in the configuration bar.', 'error');
      // Automatically expand configuration accordion so user sees where to enter key
      configContent.classList.remove('collapsed');
      configChevron.classList.add('rotated');
      apiKeyInput.focus();
      return;
    }

    const selectedModel = modelSelect.value;

    // Set UI to loading state
    isRequestPending = true;
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    questionTextbox.disabled = true;
    setStatus('loading', `Contacting ChatGPT (${selectedModel})...`);

    // Prepare answer box for incoming content
    answerTextbox.value = 'Waiting for response from ChatGPT...';
    answerCharCount.textContent = 'Generating...';
    responseTimeBadge.style.display = 'none';

    const startTime = performance.now();

    try {
      // Task 2: Execute the API Call
      const result = await callChatGPTAPI(apiKey, selectedModel, question);
      const elapsedSeconds = ((performance.now() - startTime) / 1000).toFixed(2);

      // Task 3: Put the response in the Answer textbox
      answerTextbox.value = result.content;
      
      // Update metadata & char counter
      const charLength = result.content.length;
      answerCharCount.textContent = `${charLength.toLocaleString()} character${charLength === 1 ? '' : 's'}`;
      
      responseTimeBadge.textContent = `${elapsedSeconds}s`;
      responseTimeBadge.style.display = 'inline-block';

      modelUsedTag.textContent = `Model: ${result.model}`;
      const now = new Date();
      timestampTag.textContent = `Time: ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;

      setStatus('ready', 'Response received successfully');
      showToast('Answer received successfully!', 'success', 2500);

    } catch (err) {
      console.error('ChatGPT API Error:', err);
      // Display clear failure state in answer textbox
      answerTextbox.value = `[Error occurred while fetching response]\n\n${err.message}\n\nPlease verify that your OpenAI API key is valid and has active quota.`;
      answerCharCount.textContent = 'Error';
      setStatus('error', 'Request failed');
      showToast(`Error: ${err.message}`, 'error', 6000);

    } finally {
      // Reset UI state
      isRequestPending = false;
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      questionTextbox.disabled = false;
      questionTextbox.focus();
    }
  }

  // =========================================================================
  // Clipboard Copy Handling
  // =========================================================================
  copyBtn.addEventListener('click', async () => {
    const textToCopy = answerTextbox.value.trim();
    if (!textToCopy || textToCopy.startsWith('Waiting for response') || textToCopy.startsWith('[Error')) {
      showToast('No valid answer to copy yet.', 'info', 2000);
      return;
    }

    try {
      await navigator.clipboard.writeText(textToCopy);
      copyText.textContent = 'Copied!';
      copyBtn.style.borderColor = 'var(--accent-emerald)';
      copyBtn.style.color = 'var(--accent-emerald)';
      showToast('Answer copied to clipboard!', 'success', 2000);

      setTimeout(() => {
        copyText.textContent = 'Copy';
        copyBtn.style.borderColor = '';
        copyBtn.style.color = '';
      }, 2000);
    } catch (e) {
      // Fallback for older browsers
      answerTextbox.select();
      document.execCommand('copy');
      showToast('Answer copied to clipboard!', 'success', 2000);
    }
  });
});
