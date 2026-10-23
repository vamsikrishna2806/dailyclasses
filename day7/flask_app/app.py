"""
Day 7 - Task API built with FLASK.

It does exactly the same job as ../fastapi_app/main.py so you can compare
the two files line by line.

Run:   python app.py
Open:  http://127.0.0.1:5000/tasks
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = []      # our "database" (a plain Python list in memory)
next_id = 1


@app.get("/tasks")
def list_tasks():
    return jsonify(tasks)


@app.post("/tasks")
def create_task():
    global next_id
    data = request.get_json(silent=True) or {}

    # Flask does NOT check the input for you.
    # Every rule below is written by hand.
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400
    if len(title.strip()) > 200:
        return jsonify({"error": "title must be 200 characters or less"}), 400

    priority = data.get("priority", 3)
    # bool is a subclass of int in Python, so True would sneak through without this
    if isinstance(priority, bool) or not isinstance(priority, int):
        return jsonify({"error": "priority must be a whole number"}), 400
    if not 1 <= priority <= 5:
        return jsonify({"error": "priority must be from 1 to 5"}), 400

    task = {"id": next_id, "title": title.strip(), "priority": priority, "done": False}
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return jsonify(task)
    return jsonify({"error": "task not found"}), 404


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return "", 204
    return jsonify({"error": "task not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
