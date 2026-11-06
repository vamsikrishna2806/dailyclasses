"""
=============================================================================
LAYER: Backend API & Web Server Layer (app.py)
DESCRIPTION:
  This file implements the Flask REST API backend and serves the frontend SPA.
  It handles HTTP routing, request parsing, input validation, and proper HTTP
  response status codes (200 OK, 201 Created, 400 Bad Request, 404 Not Found).
  It connects to the Database Layer (db.py) to perform all data operations.
=============================================================================
"""

from flask import Flask, jsonify, render_template, request

# Import hand-crafted database operations from our database layer
from db import create_task, delete_task, get_all_tasks, get_task_by_id, init_db, update_task

# Initialize Flask application
app = Flask(__name__)


# ---------------------------------------------------------------------------
# Frontend Route
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """
    Serve the main single-page application (SPA) HTML shell.
    All dynamic task management happens client-side via the REST API.
    """
    return render_template("index.html")


# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    GET /api/tasks
    Retrieve all tasks in the database.
    Returns:
      - 200 OK: JSON list of all task objects.
    """
    tasks = get_all_tasks()
    return jsonify(tasks), 200


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """
    POST /api/tasks
    Create a new task record.
    Expected JSON Body:
      - title: string (required, non-empty)
      - due_date: string (optional, format YYYY-MM-DD)
    Returns:
      - 201 Created: The newly created task object.
      - 400 Bad Request: If title is missing, not a string, or empty.
    """
    # Parse request JSON payload
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload provided."}), 400

    title = data.get("title")
    due_date = data.get("due_date")

    # Validate that the title is provided and not just whitespace
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Task title is required and cannot be empty."}), 400

    # Optional due_date validation: must be string or None
    if due_date is not None and not isinstance(due_date, str):
        return jsonify({"error": "Due date must be a valid date string."}), 400

    # Insert into the database
    new_task = create_task(title=title, due_date=due_date)
    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def patch_task(task_id):
    """
    PATCH /api/tasks/<id>
    Update an existing task (e.g. toggle completion status, update title/due_date).
    Expected JSON Body:
      - done: boolean (optional)
      - title: string (optional)
      - due_date: string or null (optional)
    Returns:
      - 200 OK: The updated task object.
      - 400 Bad Request: If no valid update fields are provided.
      - 404 Not Found: If task with the given ID does not exist.
    """
    # Verify task existence first
    existing_task = get_task_by_id(task_id)
    if not existing_task:
        return jsonify({"error": f"Task with id {task_id} not found."}), 404

    # Parse request JSON payload
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload provided."}), 400

    # Extract optional fields to update
    done = data.get("done")
    title = data.get("title")
    due_date = data.get("due_date")

    # Ensure at least one update field was provided
    if done is None and title is None and "due_date" not in data:
        return jsonify({"error": "At least one field ('done', 'title', 'due_date') must be provided."}), 400

    # Validate done if passed
    if done is not None and not isinstance(done, (bool, int)):
        return jsonify({"error": "Field 'done' must be a boolean or integer (0 or 1)."}), 400

    # Validate title if passed
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Title cannot be empty."}), 400

    # Update record in SQLite
    updated_task = update_task(task_id, done=done, title=title, due_date=due_date)
    return jsonify(updated_task), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    """
    DELETE /api/tasks/<id>
    Remove a task by ID.
    Returns:
      - 200 OK: Confirmation message and deleted task ID.
      - 404 Not Found: If task with given ID does not exist.
    """
    # Verify task existence first
    existing_task = get_task_by_id(task_id)
    if not existing_task:
        return jsonify({"error": f"Task with id {task_id} not found."}), 404

    # Perform deletion
    deleted = delete_task(task_id)
    if not deleted:
        return jsonify({"error": f"Failed to delete task with id {task_id}."}), 500

    return jsonify({"message": "Task deleted successfully.", "id": task_id}), 200


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure database table and sample records exist before server starts
    init_db()

    # Run Flask server locally on port 5000 in debug mode
    print("=" * 60)
    print(" Neumorphic To-Do List Server Running ")
    print(" Open in your browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
