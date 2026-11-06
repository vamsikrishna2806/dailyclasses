"""
Root Launcher for the Neumorphic To-Do List Application.
Runs the Flask application located inside the todo_app/ directory.
"""
import os
import sys

# Change working directory to todo_app so relative paths resolve cleanly
todo_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_app")
sys.path.insert(0, todo_app_dir)
os.chdir(todo_app_dir)

from app import app, init_db

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print(" Neumorphic To-Do List Server Running ")
    print(" Open in your browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
