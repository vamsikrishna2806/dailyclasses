from fastapi.testclient import TestClient
from main import app   # HTML has: from main import app, get_db (this Todo app has no get_db)

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}

def test_create_todo():
    r = client.post("/todos", json={"title": "Write tests"})
    assert r.status_code == 201
    assert r.json()["title"] == "Write tests"

def test_validation_error():
    r = client.post("/todos", json={})          # title missing
    assert r.status_code == 422

def test_not_found():
    assert client.get("/todos/9999").status_code == 404

# Swap a real dependency for a fake one during tests
# (pattern from the HTML; uncomment when your app has a get_db dependency)
# def fake_db():
#     yield {"fake": True}
#
# app.dependency_overrides[get_db] = fake_db
