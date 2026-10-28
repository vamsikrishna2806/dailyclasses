curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -d "{\"title\": \"Learn FastAPI\"}"
curl http://127.0.0.1:8000/todos
curl -X PATCH http://127.0.0.1:8000/todos/1 -H "Content-Type: application/json" -d "{\"done\": true}"
curl -X DELETE http://127.0.0.1:8000/todos/1
