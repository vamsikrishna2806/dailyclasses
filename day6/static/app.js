// ======================================================
// STUDENT TASK TRACKER - FRONTEND JAVASCRIPT
// Uses vanilla JavaScript and the standard fetch() API
// to communicate with the Flask backend.
// ======================================================

// Grab references to key HTML DOM elements
const taskForm = document.getElementById("taskForm");
const taskTitleInput = document.getElementById("taskTitleInput");
const charCounter = document.getElementById("charCounter");
const errorBanner = document.getElementById("errorBanner");
const taskList = document.getElementById("taskList");
const emptyState = document.getElementById("emptyState");
const taskStats = document.getElementById("taskStats");

// Run loadTasks as soon as the HTML document is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    loadTasks();
});

// Update the character counter while the user types (max 200 characters)
taskTitleInput.addEventListener("input", () => {
    const length = taskTitleInput.value.length;
    charCounter.textContent = `${length}/200`;
    if (length > 0) {
        clearError();
    }
});

// Helper function to show error messages on the page
function showError(message) {
    errorBanner.textContent = message;
    errorBanner.style.display = "block";
}

// Helper function to hide the error message banner
function clearError() {
    errorBanner.textContent = "";
    errorBanner.style.display = "none";
}

// ======================================================
// FEATURE 2: See all tasks in a list, newest first
// ======================================================
async function loadTasks() {
    try {
        const response = await fetch("/api/tasks");
        if (!response.ok) {
            throw new Error("Failed to load tasks from server.");
        }

        const tasks = await response.json();
        renderTaskList(tasks);
    } catch (err) {
        showError("Could not connect to the server. Please check if Flask is running.");
    }
}

// Renders the list of tasks inside the <ul> element
function renderTaskList(tasks) {
    taskList.innerHTML = ""; // Clear current list

    // Toggle empty state message
    if (tasks.length === 0) {
        emptyState.style.display = "block";
        taskStats.textContent = "0 tasks";
        return;
    }

    emptyState.style.display = "none";

    // Count how many tasks are completed
    const completedCount = tasks.filter(t => t.done === 1).length;
    taskStats.textContent = `${completedCount} of ${tasks.length} done`;

    // Loop through tasks and build HTML for each task item
    tasks.forEach(task => {
        const li = document.createElement("li");
        li.className = `task-item ${task.done === 1 ? "is-done" : ""}`;
        li.setAttribute("data-id", task.id);

        // Task content: checkbox and title
        const taskContent = document.createElement("div");
        taskContent.className = "task-content";

        // Checkbox (Feature 3: Mark done or not done)
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.className = "task-checkbox";
        checkbox.checked = task.done === 1;
        checkbox.setAttribute("aria-label", `Mark "${task.title}" as complete`);
        checkbox.addEventListener("change", () => toggleTask(task.id));

        // Details container (title and timestamp)
        const details = document.createElement("div");
        details.className = "task-details";

        const titleSpan = document.createElement("span");
        titleSpan.className = "task-title";
        titleSpan.textContent = task.title; // Using textContent prevents XSS attacks

        const timeSpan = document.createElement("span");
        timeSpan.className = "task-time";
        timeSpan.textContent = `Added: ${task.created_at}`;

        details.appendChild(titleSpan);
        details.appendChild(timeSpan);

        taskContent.appendChild(checkbox);
        taskContent.appendChild(details);

        // Delete button (Feature 4: Delete a task)
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn-delete";
        deleteBtn.textContent = "Delete";
        deleteBtn.setAttribute("aria-label", `Delete task "${task.title}"`);
        deleteBtn.addEventListener("click", () => deleteTask(task.id));

        li.appendChild(taskContent);
        li.appendChild(deleteBtn);

        taskList.appendChild(li);
    });
}

// ======================================================
// FEATURE 1: Add a task
// ======================================================
taskForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent standard page reload

    const title = taskTitleInput.value.trim();

    // Frontend validation: check not empty
    if (!title) {
        showError("Task title cannot be empty. Please enter a task.");
        taskTitleInput.focus();
        return;
    }

    // Frontend validation: check length under 200 characters
    if (title.length > 200) {
        showError("Task title must be under 200 characters.");
        return;
    }

    clearError();

    try {
        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: title })
        });

        const result = await response.json();

        if (!response.ok) {
            // Show validation or server error message returned by backend
            showError(result.error || "Failed to add task.");
            return;
        }

        // Reset input field and character counter on success
        taskTitleInput.value = "";
        charCounter.textContent = "0/200";

        // Refresh task list to show the new task at the top
        loadTasks();
    } catch (err) {
        showError("Network error while trying to add task.");
    }
});

// ======================================================
// FEATURE 3: Mark a task as done or not done with checkbox
// ======================================================
async function toggleTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: "PATCH"
        });

        if (!response.ok) {
            const result = await response.json();
            showError(result.error || "Failed to update task.");
            return;
        }

        // Refresh list to update strikethrough styling and completed counter
        loadTasks();
    } catch (err) {
        showError("Network error while updating task.");
    }
}

// ======================================================
// FEATURE 4: Delete a task with a "Delete" button
// ======================================================
async function deleteTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            const result = await response.json();
            showError(result.error || "Failed to delete task.");
            return;
        }

        // Refresh list to remove the deleted task
        loadTasks();
    } catch (err) {
        showError("Network error while deleting task.");
    }
}
