/*
=============================================================================
LAYER: Frontend Client-Side Logic Layer (static/script.js)
DESCRIPTION:
  This file implements the Vanilla JavaScript Single-Page Application (SPA) logic.
  It performs asynchronous HTTP requests (GET, POST, PATCH, DELETE) to the Flask
  REST API endpoints, manages local state, handles user interactions, updates
  the task counter ("X of Y tasks done"), renders the Neumorphic task items,
  and provides real-time filtering (All / Active / Done) and due date tracking.
=============================================================================
*/

// Strict mode ensures cleaner JavaScript and catches common bugs
"use strict";

// ---------------------------------------------------------------------------
// Application State
// ---------------------------------------------------------------------------
const state = {
  // Array of all task objects fetched from the REST API
  tasks: [],
  // Current active filter: 'all' | 'active' | 'done'
  currentFilter: "all",
  // Loading status flag
  isLoading: false,
};

// ---------------------------------------------------------------------------
// DOM Elements Cache
// ---------------------------------------------------------------------------
const elements = {
  // Form and inputs
  addTaskForm: document.getElementById("add-task-form"),
  taskTitleInput: document.getElementById("task-title-input"),
  taskDateInput: document.getElementById("task-date-input"),
  addTaskBtn: document.getElementById("add-task-btn"),
  formError: document.getElementById("form-error"),

  // Metrics and progress
  tasksCounter: document.getElementById("tasks-counter"),
  progressBarFill: document.getElementById("progress-bar-fill"),
  percentBadge: document.getElementById("percent-badge"),

  // Filter tabs and counts
  filterPills: document.querySelectorAll(".filter-pill"),
  countAll: document.getElementById("count-all"),
  countActive: document.getElementById("count-active"),
  countDone: document.getElementById("count-done"),

  // Task list and feedback containers
  tasksList: document.getElementById("tasks-list"),
  tasksLoading: document.getElementById("tasks-loading"),
  emptyState: document.getElementById("empty-state"),
  emptyDescription: document.getElementById("empty-description"),
  toastContainer: document.getElementById("toast-container"),
};

// ---------------------------------------------------------------------------
// API Service Layer (REST Calls via fetch)
// ---------------------------------------------------------------------------
const API = {
  // Base URL for tasks endpoint
  BASE_URL: "/api/tasks",

  /**
   * Fetch all tasks from GET /api/tasks
   */
  async getAllTasks() {
    const response = await fetch(this.BASE_URL);
    if (!response.ok) {
      throw new Error(`Failed to load tasks (Status: ${response.status})`);
    }
    return await response.json();
  },

  /**
   * Create a new task via POST /api/tasks
   */
  async createTask(title, dueDate) {
    const response = await fetch(this.BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: title,
        due_date: dueDate || null,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to create task");
    }
    return data;
  },

  /**
   * Update task status or fields via PATCH /api/tasks/<id>
   */
  async updateTask(id, updates) {
    const response = await fetch(`${this.BASE_URL}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to update task");
    }
    return data;
  },

  /**
   * Delete a task via DELETE /api/tasks/<id>
   */
  async deleteTask(id) {
    const response = await fetch(`${this.BASE_URL}/${id}`, {
      method: "DELETE",
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to delete task");
    }
    return data;
  },
};

// ---------------------------------------------------------------------------
// UI Toast Notifications
// ---------------------------------------------------------------------------
function showToast(message, type = "info") {
  // Create toast container element
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  elements.toastContainer.appendChild(toast);

  // Automatically fade out and remove after 3.2 seconds
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(15px)";
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 280);
  }, 3200);
}

// ---------------------------------------------------------------------------
// Date Helper & Badge Formatter
// ---------------------------------------------------------------------------
function formatDueDateBadge(dateString, isDone) {
  if (!dateString) return "";

  // Parse target date and today's date (ignoring time component)
  const targetDate = new Date(dateString + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const diffTime = targetDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  let statusClass = "";
  let displayText = "";

  if (diffDays < 0 && !isDone) {
    statusClass = "overdue";
    displayText = `Overdue (${Math.abs(diffDays)}d ago)`;
  } else if (diffDays === 0) {
    statusClass = "today";
    displayText = "Due Today";
  } else if (diffDays === 1) {
    displayText = "Due Tomorrow";
  } else {
    // Format as Month Day (e.g., Oct 25)
    displayText = targetDate.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
  }

  return `
    <span class="due-badge ${statusClass}" title="Due: ${dateString}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="16" y1="2" x2="16" y2="6"></line>
        <line x1="8" y1="2" x2="8" y2="6"></line>
        <line x1="3" y1="10" x2="21" y2="10"></line>
      </svg>
      ${displayText}
    </span>
  `;
}

// ---------------------------------------------------------------------------
// Render & Metric Calculations
// ---------------------------------------------------------------------------

/**
 * Update the counters, progress bar, and filter counts.
 * Requirement 5: Show a counter: "3 of 5 tasks done"
 */
function updateMetrics() {
  const total = state.tasks.length;
  const doneCount = state.tasks.filter((t) => t.done).length;
  const activeCount = total - doneCount;

  // Requirement 5 text update: "3 of 5 tasks done"
  elements.tasksCounter.textContent = `${doneCount} of ${total} tasks done`;

  // Calculate percentage
  const percentage = total === 0 ? 0 : Math.round((doneCount / total) * 100);
  elements.progressBarFill.style.width = `${percentage}%`;
  elements.percentBadge.textContent = `${percentage}%`;

  // Update filter counts
  elements.countAll.textContent = total;
  elements.countActive.textContent = activeCount;
  elements.countDone.textContent = doneCount;
}

/**
 * Filter and render the tasks into the DOM.
 */
function renderTasks() {
  // Filter tasks based on currentFilter
  let filtered = state.tasks;
  if (state.currentFilter === "active") {
    filtered = state.tasks.filter((t) => !t.done);
  } else if (state.currentFilter === "done") {
    filtered = state.tasks.filter((t) => t.done);
  }

  // Clear existing list items
  elements.tasksList.innerHTML = "";

  // Handle empty state
  if (filtered.length === 0) {
    elements.emptyState.classList.remove("hidden");
    if (state.tasks.length === 0) {
      elements.emptyDescription.textContent = "No tasks yet. Create your first task above!";
    } else if (state.currentFilter === "active") {
      elements.emptyDescription.textContent = "Awesome job! You have no active tasks pending.";
    } else if (state.currentFilter === "done") {
      elements.emptyDescription.textContent = "No completed tasks yet. Check off a task when finished!";
    }
  } else {
    elements.emptyState.classList.add("hidden");

    // Construct task list items
    filtered.forEach((task) => {
      const li = document.createElement("li");
      li.className = `task-item ${task.done ? "is-done" : ""}`;
      li.id = `task-item-${task.id}`;
      li.setAttribute("data-id", task.id);

      // Sanitize title for safe display
      const safeTitle = document.createElement("div");
      safeTitle.textContent = task.title;
      const sanitizedTitle = safeTitle.innerHTML;

      // Due date markup
      const dueDateBadge = formatDueDateBadge(task.due_date, task.done);

      li.innerHTML = `
        <div class="task-content-wrapper">
          <!-- Requirement 3: Checkbox to toggle done status -->
          <label class="custom-checkbox-label" title="Mark as ${task.done ? 'active' : 'done'}">
            <input 
              type="checkbox" 
              class="custom-checkbox-input" 
              ${task.done ? "checked" : ""} 
              data-action="toggle-done"
              data-id="${task.id}"
            />
            <span class="checkbox-visual">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </label>

          <div class="task-info">
            <span class="task-title">${sanitizedTitle}</span>
            ${dueDateBadge ? `<div class="task-meta">${dueDateBadge}</div>` : ""}
          </div>
        </div>

        <!-- Requirement 4: Delete button -->
        <button 
          type="button" 
          class="delete-btn" 
          data-action="delete-task" 
          data-id="${task.id}"
          title="Delete task"
          aria-label="Delete task: ${sanitizedTitle}"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
        </button>
      `;

      elements.tasksList.appendChild(li);
    });
  }

  // Update counters and progress bar
  updateMetrics();
}

// ---------------------------------------------------------------------------
// Event Handlers & User Actions
// ---------------------------------------------------------------------------

/**
 * Initial load of all tasks from Flask REST API
 */
async function loadTasks() {
  state.isLoading = true;
  elements.tasksLoading.classList.remove("hidden");
  elements.tasksList.classList.add("hidden");

  try {
    const tasks = await API.getAllTasks();
    state.tasks = tasks;
    renderTasks();
  } catch (error) {
    console.error("Error loading tasks:", error);
    showToast(error.message || "Failed to load tasks from server", "danger");
  } finally {
    state.isLoading = false;
    elements.tasksLoading.classList.add("hidden");
    elements.tasksList.classList.remove("hidden");
  }
}

/**
 * Requirement 2: Add a new task with text box and "Add" button
 */
async function handleAddTask(e) {
  e.preventDefault();

  const title = elements.taskTitleInput.value.trim();
  const dueDate = elements.taskDateInput.value;

  // Client validation
  if (!title) {
    elements.formError.textContent = "Please enter a task description.";
    elements.formError.classList.remove("hidden");
    elements.taskTitleInput.focus();
    return;
  }

  elements.formError.classList.add("hidden");
  elements.addTaskBtn.disabled = true;

  try {
    // Call POST /api/tasks
    const createdTask = await API.createTask(title, dueDate);

    // Add to local state (active tasks appear at the top)
    state.tasks.unshift(createdTask);

    // Re-render tasks and update progress
    renderTasks();

    // Reset input fields
    elements.taskTitleInput.value = "";
    elements.taskDateInput.value = "";
    elements.taskTitleInput.focus();

    showToast("Task added successfully!", "success");
  } catch (error) {
    console.error("Error adding task:", error);
    showToast(error.message || "Could not add task", "danger");
  } finally {
    elements.addTaskBtn.disabled = false;
  }
}

/**
 * Requirement 3: Toggle task completion status (strike-through style)
 */
async function handleToggleDone(taskId, newDoneStatus) {
  try {
    // Optimistically update local state for immediate snappy UI feedback
    const taskIndex = state.tasks.findIndex((t) => t.id === taskId);
    if (taskIndex === -1) return;

    const previousDone = state.tasks[taskIndex].done;
    state.tasks[taskIndex].done = newDoneStatus;
    renderTasks();

    // Call PATCH /api/tasks/<id>
    const updated = await API.updateTask(taskId, { done: newDoneStatus });

    // Sync with returned server state
    state.tasks[taskIndex] = updated;
    updateMetrics();

    showToast(
      newDoneStatus ? "Task marked as done!" : "Task marked as active",
      "info"
    );
  } catch (error) {
    console.error("Error updating task status:", error);
    showToast(error.message || "Failed to update task", "danger");
    // Reload tasks on error to guarantee consistency with database
    loadTasks();
  }
}

/**
 * Requirement 4: Delete a task
 */
async function handleDeleteTask(taskId) {
  const taskElement = document.getElementById(`task-item-${taskId}`);

  // Play smooth deletion exit animation
  if (taskElement) {
    taskElement.classList.add("deleting");
  }

  try {
    // Call DELETE /api/tasks/<id>
    await API.deleteTask(taskId);

    // Remove from local state after small delay for animation
    setTimeout(() => {
      state.tasks = state.tasks.filter((t) => t.id !== taskId);
      renderTasks();
      showToast("Task deleted", "danger");
    }, 200);
  } catch (error) {
    console.error("Error deleting task:", error);
    showToast(error.message || "Failed to delete task", "danger");
    if (taskElement) {
      taskElement.classList.remove("deleting");
    }
  }
}

/**
 * Stretch Goal: Filter task list by All / Active / Done
 */
function handleFilterChange(filterValue) {
  state.currentFilter = filterValue;

  // Update active pill UI styling
  elements.filterPills.forEach((pill) => {
    const isSelected = pill.getAttribute("data-filter") === filterValue;
    pill.classList.toggle("active", isSelected);
    pill.setAttribute("aria-selected", isSelected ? "true" : "false");
  });

  renderTasks();
}

// ---------------------------------------------------------------------------
// Setup Event Listeners
// ---------------------------------------------------------------------------
function setupEventListeners() {
  // Add task form submission
  elements.addTaskForm.addEventListener("submit", handleAddTask);

  // Clear form error as user types
  elements.taskTitleInput.addEventListener("input", () => {
    if (!elements.formError.classList.contains("hidden")) {
      elements.formError.classList.add("hidden");
    }
  });

  // Filter tabs click handling
  elements.filterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      const filter = pill.getAttribute("data-filter");
      handleFilterChange(filter);
    });
  });

  // Delegated event listener for task items (checkboxes and delete buttons)
  elements.tasksList.addEventListener("click", (e) => {
    // Check if delete button was clicked
    const deleteBtn = e.target.closest('[data-action="delete-task"]');
    if (deleteBtn) {
      const taskId = parseInt(deleteBtn.getAttribute("data-id"), 10);
      handleDeleteTask(taskId);
      return;
    }

    // Check if checkbox was toggled
    const checkbox = e.target.closest('[data-action="toggle-done"]');
    if (checkbox) {
      const taskId = parseInt(checkbox.getAttribute("data-id"), 10);
      const isChecked = checkbox.checked;
      handleToggleDone(taskId, isChecked);
    }
  });
}

// ---------------------------------------------------------------------------
// Application Bootstrap
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadTasks();
});
