"""
=============================================================================
LAYER: Database Persistence Layer (db.py)
DESCRIPTION:
  This file manages all interactions with the SQLite database.
  It uses Python's built-in `sqlite3` module with 100% hand-crafted SQL
  queries (no ORM). It is responsible for database initialization, schema
  creation, seed data insertion, and all CRUD (Create, Read, Update, Delete)
  operations on the `tasks` table.
=============================================================================
"""

import os
import sqlite3
from datetime import datetime

# Resolve database file path relative to this file's directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.db")


def get_db_connection():
    """
    Establish and return a new SQLite database connection.
    Configures `row_factory` to `sqlite3.Row` so query results can be
    accessed like dictionaries with column names.
    """
    conn = sqlite3.connect(DB_PATH)
    # Enable dict-like column access for fetched rows
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database table and seed initial sample data if empty.
    Creates the `tasks` table with fields:
      - id: unique auto-incrementing integer identifier
      - title: task description string (cannot be null)
      - done: integer status flag (0 = active, 1 = completed)
      - created_at: ISO-formatted timestamp of task creation
      - due_date: optional ISO date string for task deadline (stretch goal)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the tasks table if it does not already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            due_date TEXT
        )
    """)

    # Check if the database has any existing tasks
    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cursor.fetchone()["count"]

    # Seed initial sample data if the table is freshly created and empty
    if count == 0:
        sample_tasks = [
            (
                "Explore the Neumorphic To-Do App design",
                1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d"),
            ),
            (
                "Test adding a new task with due date",
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d"),
            ),
            (
                "Filter tasks by Active and Done status",
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                None,
            ),
            (
                "Review Flask REST API endpoints in app.py",
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                None,
            ),
        ]

        # Insert sample rows using parameterized SQL to prevent SQL injection
        cursor.executemany(
            """
            INSERT INTO tasks (title, done, created_at, due_date)
            VALUES (?, ?, ?, ?)
            """,
            sample_tasks,
        )

        conn.commit()

    conn.close()


def task_to_dict(row):
    """
    Helper function to convert a sqlite3.Row object into a standard Python dict.
    Converts SQLite integer boolean (0 or 1) to a Python boolean for clean JSON serialization.
    """
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
        "due_date": row["due_date"],
    }


def get_all_tasks():
    """
    Retrieve all tasks from the database ordered by completion status (active first)
    and then descending by ID (newest first).
    Returns a list of task dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, done, created_at, due_date
        FROM tasks
        ORDER BY done ASC, id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [task_to_dict(row) for row in rows]


def get_task_by_id(task_id):
    """
    Fetch a single task record by its unique ID.
    Returns the task dictionary if found, or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done, created_at, due_date FROM tasks WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    conn.close()

    return task_to_dict(row)


def create_task(title, due_date=None):
    """
    Insert a new task into the database.
    - title: text description (validated by caller)
    - due_date: optional string in YYYY-MM-DD format
    Returns the newly inserted task dictionary.
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, done, created_at, due_date)
        VALUES (?, 0, ?, ?)
        """,
        (title.strip(), created_at, due_date.strip() if due_date else None),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return get_task_by_id(new_id)


def update_task(task_id, done=None, title=None, due_date=None):
    """
    Update specific attributes of an existing task.
    Supports updating 'done' status, 'title', and/or 'due_date'.
    Returns the updated task dictionary if found, or None if task does not exist.
    """
    # Check if task exists first
    task = get_task_by_id(task_id)
    if not task:
        return None

    # Dynamically build the SQL UPDATE clause based on provided arguments
    update_clauses = []
    params = []

    if done is not None:
        # Convert boolean to integer (1 for True, 0 for False)
        update_clauses.append("done = ?")
        params.append(1 if done else 0)

    if title is not None:
        update_clauses.append("title = ?")
        params.append(title.strip())

    if due_date is not None:
        update_clauses.append("due_date = ?")
        params.append(due_date.strip() if due_date else None)

    # If no fields were provided to update, return the current task
    if not update_clauses:
        return task

    # Append task_id for the WHERE clause
    params.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(update_clauses)} WHERE id = ?"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(params))
    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def delete_task(task_id):
    """
    Delete a task by its ID.
    Returns True if a record was deleted, or False if no matching record was found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted
