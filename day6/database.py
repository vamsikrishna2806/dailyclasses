import sqlite3
from datetime import datetime

# Name of the SQLite database file stored locally
DATABASE_NAME = "tasks.db"


def get_db_connection():
    """
    Connect to the SQLite database file.
    Row factory allows accessing query results by column name like dictionaries (e.g., row['title']).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates the 'tasks' table automatically if it does not already exist.
    Columns:
      - id: unique number for each task, auto-increments
      - title: text description of the task (required)
      - done: integer flag (0 = not done, 1 = done, defaults to 0)
      - created_at: readable timestamp string showing when the task was added
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()


def get_all_tasks():
    """
    Fetch all tasks from the database, sorted newest first (highest id first).
    Returns a list of task dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query all tasks ordered newest first using parameterized SQL (best practice)
    cursor.execute("SELECT id, title, done, created_at FROM tasks ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # Convert each sqlite3.Row object into a standard Python dictionary
    tasks = []
    for row in rows:
        tasks.append({
            "id": row["id"],
            "title": row["title"],
            "done": row["done"],
            "created_at": row["created_at"]
        })
    return tasks


def add_task(title):
    """
    Insert a new task into the database using a parameterized query (?).
    Returns the newly created task dictionary.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Current timestamp formatted as YYYY-MM-DD HH:MM:SS
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Use the '?' placeholder to safely pass user input and prevent SQL injection
    cursor.execute(
        "INSERT INTO tasks (title, done, created_at) VALUES (?, 0, ?)",
        (title, created_at)
    )

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": new_id,
        "title": title,
        "done": 0,
        "created_at": created_at
    }


def toggle_task(task_id):
    """
    Toggle a task's 'done' status between 0 (not done) and 1 (done).
    Uses a parameterized query (?) with the task ID.
    Returns the updated task dictionary, or None if the task does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the task exists first
    cursor.execute("SELECT id, title, done, created_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    # Flip status: if 0 -> 1, if 1 -> 0
    new_status = 1 if row["done"] == 0 else 0

    cursor.execute(
        "UPDATE tasks SET done = ? WHERE id = ?",
        (new_status, task_id)
    )
    conn.commit()
    conn.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": new_status,
        "created_at": row["created_at"]
    }


def delete_task(task_id):
    """
    Delete a task from the database by its ID using a parameterized query (?).
    Returns True if a row was deleted, False if the ID was not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return deleted
