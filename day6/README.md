# 🎓 Student Task Tracker

A simple, beginner-friendly web application for students to track their study tasks and daily goals. Built with **Python Flask** on the backend, standard **SQLite** for local database storage, and clean **HTML, CSS, and JavaScript** on the frontend.

---

## ✨ Features

1. **Add a task**: Enter study goals in the text box and click **Add Task**.
2. **See all tasks**: View all tasks neatly in a list, sorted with the newest task first.
3. **Mark as done / not done**: Check the checkbox to mark a task as completed (applies a clean strikethrough effect) or uncheck it to mark it active again.
4. **Delete a task**: Click the **Delete** button to remove a task permanently from the database.

---

## 🛠️ Setup Steps

Run the following commands in your terminal or command prompt:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
# source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask application
python app.py
```

After starting the server, open your web browser and visit:
👉 **http://localhost:5000**

---

## 📂 Project Structure & Plain English Explanations

Here is an overview of each file and what it does in plain English:

1. **`app.py`**: The Python Flask web server. It handles incoming web requests, defines the REST API endpoints (`GET /api/tasks`, `POST /api/tasks`, `PATCH /api/tasks/<id>`, `DELETE /api/tasks/<id>`), validates inputs (e.g. non-empty title under 200 characters), and renders the home page.
2. **`database.py`**: The SQLite database helper module. It creates `tasks.db` and the `tasks` table automatically on startup using Python's built-in `sqlite3` library. It uses safe parameterized SQL queries (`?`) to perform `get_all`, `add`, `toggle`, and `delete` operations without risk of SQL injection.
3. **`templates/index.html`**: The web page structure. It contains the header, input form, character counter, error message banner, and the task list container.
4. **`static/style.css`**: The styling rules. It provides a clean, responsive layout with an attractive color scheme and mobile-friendly tap targets that look great on smartphones, tablets, and desktops.
5. **`static/app.js`**: The frontend logic. It listens for user actions (submitting a task, clicking checkboxes, clicking delete) and communicates with the Flask API routes using `fetch()` without reloading the page.
6. **`requirements.txt`**: Lists Python packages required to run the project (`flask`).
7. **`README.md`**: Complete project documentation, setup guide, and database examples.

---

## 🧪 3 Example Tasks & SQLite Database Inspection

### Example Tasks to Add:
1. `Read Chapter 3 of Biology textbook`
2. `Complete Calculus Problem Set #4`
3. `Review History notes for Friday quiz`

### Inspecting `tasks.db` with SQLite Command Line:

You can inspect the saved database at any time using the `sqlite3` command line:

```bash
sqlite3 tasks.db
```

Then run this SQL query:

```sql
SELECT id, title, done, created_at FROM tasks ORDER BY id ASC;
```

### Expected Output:

```text
id | title                                | done | created_at
---+--------------------------------------+------+--------------------
1  | Read Chapter 3 of Biology textbook   | 0    | 2026-10-23 06:45:10
2  | Complete Calculus Problem Set #4     | 0    | 2026-10-23 06:46:25
3  | Review History notes for Friday quiz | 0    | 2026-10-23 06:47:05
```

> **Note**: `done = 0` means the task is active (not done). When you click the checkbox for task #2, its `done` value updates to `1`.
