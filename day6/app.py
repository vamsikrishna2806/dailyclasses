from flask import Flask, render_template, request, jsonify
import database

# Initialize the Flask web application
app = Flask(__name__)

# Automatically create the database file and table if they do not exist
database.init_db()


@app.route("/")
def home():
    """
    Renders and serves the single-page HTML frontend.
    """
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    GET /api/tasks
    Fetches all tasks from the database (newest first) and returns them as JSON.
    """
    tasks = database.get_all_tasks()
    return jsonify(tasks), 200


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """
    POST /api/tasks
    Expects a JSON body: { "title": "Study Python" }
    Validates input:
      - Title cannot be empty or just whitespace.
      - Title must be under 200 characters.
    Returns the newly created task on success, or an error message with status 400.
    """
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    # Input validation: check for string type, strip whitespace
    if not isinstance(title, str):
        return jsonify({"error": "Task title must be text."}), 400

    clean_title = title.strip()

    # Rule: title must not be empty
    if not clean_title:
        return jsonify({"error": "Task title cannot be empty."}), 400

    # Rule: title must be under 200 characters
    if len(clean_title) > 200:
        return jsonify({"error": "Task title must be under 200 characters."}), 400

    # Save to the database using parameterized query
    new_task = database.add_task(clean_title)
    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def toggle_task(task_id):
    """
    PATCH /api/tasks/<id>
    Toggles a task between done (1) and not done (0).
    Returns the updated task, or 404 if the task ID was not found.
    """
    updated_task = database.toggle_task(task_id)
    if updated_task is None:
        return jsonify({"error": f"Task with ID {task_id} not found."}), 404

    return jsonify(updated_task), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    """
    DELETE /api/tasks/<id>
    Deletes a task by ID.
    Returns a success message, or 404 if the task ID was not found.
    """
    deleted = database.delete_task(task_id)
    if not deleted:
        return jsonify({"error": f"Task with ID {task_id} not found."}), 404

    return jsonify({"message": "Task deleted successfully."}), 200


if __name__ == "__main__":
    # Run the server locally on port 5000
    app.run(debug=True, port=5000)
