"""
=============================================================================
LAYER: Test Verification Layer (test_app.py)
Automated unit & API endpoint tests for the To-Do List application.
=============================================================================
"""

import unittest
import os
import json

# Ensure test uses a clean temporary database
os.environ["TESTING"] = "1"
from app import app
from db import init_db, DB_PATH

class TodoAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure test client
        self.client = app.test_client()
        app.config["TESTING"] = True
        # Clean up database if exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def tearDown(self):
        # Clean up test database
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def test_01_index_page(self):
        """Test GET / returns 200 and loads HTML template."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TaskFlow", response.data)
        self.assertIn(b"tasks-counter", response.data)

    def test_02_get_seeded_tasks(self):
        """Test GET /api/tasks returns initial seeded tasks."""
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        tasks = response.get_json()
        self.assertIsInstance(tasks, list)
        self.assertGreaterEqual(len(tasks), 4)
        # Check first task structure
        first = tasks[0]
        self.assertIn("id", first)
        self.assertIn("title", first)
        self.assertIn("done", first)
        self.assertIn("created_at", first)

    def test_03_create_task_success(self):
        """Test POST /api/tasks with valid title returns 201."""
        payload = {"title": "Test new task", "due_date": "2026-10-30"}
        response = self.client.post(
            "/api/tasks",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        created = response.get_json()
        self.assertEqual(created["title"], "Test new task")
        self.assertEqual(created["due_date"], "2026-10-30")
        self.assertFalse(created["done"])

    def test_04_create_task_validation_error(self):
        """Test POST /api/tasks with empty or missing title returns 400."""
        # Empty string
        response = self.client.post(
            "/api/tasks",
            data=json.dumps({"title": "   "}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

        # Missing title key
        response2 = self.client.post(
            "/api/tasks",
            data=json.dumps({"due_date": "2026-10-30"}),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 400)

    def test_05_patch_task_toggle_done(self):
        """Test PATCH /api/tasks/<id> updates done status."""
        # Toggle task 2 to done: True
        response = self.client.patch(
            "/api/tasks/2",
            data=json.dumps({"done": True}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertTrue(updated["done"])

        # Toggle back to False
        response2 = self.client.patch(
            "/api/tasks/2",
            data=json.dumps({"done": False}),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 200)
        updated2 = response2.get_json()
        self.assertFalse(updated2["done"])

    def test_06_patch_nonexistent_task(self):
        """Test PATCH /api/tasks/<id> for non-existent id returns 404."""
        response = self.client.patch(
            "/api/tasks/9999",
            data=json.dumps({"done": True}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_07_delete_task(self):
        """Test DELETE /api/tasks/<id> deletes a task."""
        # Delete task 1
        response = self.client.delete("/api/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 1)

        # Deleting again should return 404
        response2 = self.client.delete("/api/tasks/1")
        self.assertEqual(response2.status_code, 404)

if __name__ == "__main__":
    unittest.main()
