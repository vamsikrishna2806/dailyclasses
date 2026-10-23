# Day 7 · Flask vs FastAPI

Open **`flask_vs_fastapi_guide.html`** in a browser. It is an interactive lesson with animations:

| Lesson | What you see |
|---|---|
| 1. Async race | Animated "waiter story": 1 sync Flask worker vs 1 async FastAPI worker |
| 2. Request journey | A request travelling through each framework, step by step |
| 3. Validation | Send good and bad JSON to both apps and compare the real responses |
| 4. Auto docs | Code types itself while the `/docs` page builds itself |
| 5. Type hints | How `task_id: int` checks, converts and documents |
| 6. Depends | Dependency injection as plug-in helpers |
| 7. Same app, 2 ways | Full Task API in Flask and in FastAPI, side by side |
| 8. 360° table | 25 features compared, with filters |
| 9–13 | What FastAPI changed, myths, "which one?" helper, quiz, cheat sheet |

## Run both apps

```bash
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**Flask** (terminal 1):

```bash
cd flask_app
python app.py
```

Open http://127.0.0.1:5000/tasks

**FastAPI** (terminal 2):

```bash
cd fastapi_app
fastapi dev main.py
```

Open http://127.0.0.1:8000/docs (free interactive docs) and http://127.0.0.1:8000/redoc

## Try this

Send the same bad data to both and compare:

```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Gym\", \"priority\": \"high\"}"
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Gym\", \"priority\": \"high\"}"
```

- Flask answers `400` with the message you wrote by hand.
- FastAPI answers `422` with the exact field, the reason and the bad value, and you wrote no checks.

Then visit `/tasks/abc` on both: Flask gives a plain 404 page, FastAPI explains that `task_id` must be an integer.
