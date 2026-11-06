# 📝 Neumorphic To-Do List Web App

A clean, minimalist Single-Page Application (SPA) To-Do List built with a modern **Neumorphic (Soft UI)** design, pure vanilla HTML/CSS/JavaScript on the frontend, a lightweight **Flask REST API** backend, and raw hand-crafted SQL persistence using Python's standard library **SQLite3** (no ORM).

---

## 🌟 Features

- **Dynamic Task Management (SPA)**: View all tasks loaded dynamically without page refreshes.
- **Add Tasks**: Add new tasks with description and optional due date.
- **Toggle Done**: Mark tasks as done/active with smooth strike-through typography and custom neumorphic checkboxes.
- **Delete Tasks**: Remove tasks instantly with animated transitions.
- **Progress Counter**: Real-time progress metric (`"3 of 5 tasks done"`) with percentage indicator and smooth inset progress bar.
- **Stretch Goals**:
  - **Status Filter**: Toggle between **All**, **Active**, and **Done** with dynamic item counts.
  - **Due Date & Overdue Indicators**: Assign deadlines; overdue tasks are highlighted with alert badges.
- **Automated Seeding**: Seeds 4 sample tasks on first launch so the app is ready to use immediately.

---

## 🏗️ 3-Layer Architecture

The project maintains strict separation of concerns across three distinct layers:

```
todo_app/
│
├── static/
│   ├── style.css         # [Presentation Layer] Neumorphic Soft UI design & animations
│   └── script.js         # [Presentation Logic Layer] Vanilla JS SPA, REST fetch calls
│
├── templates/
│   └── index.html        # [Presentation Layer] Semantic HTML template served by Flask
│
├── app.py                # [Backend API Layer] Flask REST endpoints, routing, validation
├── db.py                 # [Persistence Layer] Raw SQLite3 connections, queries, seeding
├── requirements.txt      # [Dependencies] Pinned open-source library versions
└── README.md             # [Documentation] Setup guide and API reference
```

Every source file contains a layer declaration header explaining its responsibilities.

---

## 📋 Prerequisites

- **Python 3.8+** (Python 3.11+ recommended)
- **pip** (Python package installer)
- A modern web browser (Chrome, Edge, Firefox, Safari)

---

## 🚀 Installation & Setup

1. **Navigate to the application folder**:
   ```bash
   cd todo_app
   ```

2. **(Optional) Create and activate a virtual environment**:
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the pinned dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```
   *(Or run `python run.py` from the root workspace directory)*

2. **Open in your browser**:
   Navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 💾 Database Schema

The database is powered by standard SQLite (`todo.db`), automatically created and seeded on first run using hand-written SQL:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    due_date TEXT
);
```

---

## 🔌 REST API Reference

All API endpoints return JSON responses with standard HTTP status codes.

| Method | Endpoint | Description | Request Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/tasks` | Retrieve all tasks | *None* | `200 OK` |
| `POST` | `/api/tasks` | Create a new task | `{"title": "...", "due_date": "YYYY-MM-DD"}` | `201 Created`, `400 Bad Request` |
| `PATCH` | `/api/tasks/<id>` | Update status or fields | `{"done": true}` or `{"title": "..."}` | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/tasks/<id>` | Delete a task | *None* | `200 OK`, `404 Not Found` |

### Sample JSON Requests

#### 1. Add Task (`POST /api/tasks`)
```json
{
  "title": "Buy groceries",
  "due_date": "2026-10-25"
}
```

#### 2. Toggle Status (`PATCH /api/tasks/1`)
```json
{
  "done": true
}
```

#### 3. Response format
```json
{
  "id": 1,
  "title": "Buy groceries",
  "done": true,
  "created_at": "2026-10-24 08:15:00",
  "due_date": "2026-10-25"
}
```

---

## 🎨 Neumorphic Design Details

- **Soft Dual Shadows**: Surfaces elevated with light highlights (`#ffffff`) and soft ambient shadows (`#c5d0e0`).
- **Sunken/Inset Inputs**: Input boxes and toggled checkboxes feature realistic recessed shadows (`box-shadow: inset ...`).
- **Interactive Feedback**: Pressed buttons transition smoothly from raised to sunken states with micro-animations.
- **Accessible & Responsive**: Fully responsive layout adapting from mobile screens to desktop viewports.
