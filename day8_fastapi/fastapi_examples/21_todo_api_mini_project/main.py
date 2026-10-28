from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="Todo API", version="1.0.0")

# ---------- schemas ----------
class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TodoUpdate(BaseModel):          # every field optional, for PATCH
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None

class Todo(TodoCreate):
    id: int

# ---------- "database" ----------
db: dict[int, Todo] = {}
counter = {"next": 1}

def get_todo_or_404(todo_id: int) -> Todo:          # reusable dependency
    if todo_id not in db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return db[todo_id]

TodoDep = Annotated[Todo, Depends(get_todo_or_404)]

# ---------- routes ----------
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/todos", tags=["todos"])
def list_todos(done: bool | None = None,
               limit: Annotated[int, Query(ge=1, le=100)] = 20) -> list[Todo]:
    todos = list(db.values())
    if done is not None:
        todos = [t for t in todos if t.done == done]
    return todos[:limit]

@app.post("/todos", status_code=status.HTTP_201_CREATED, tags=["todos"])
def create_todo(data: TodoCreate) -> Todo:
    todo = Todo(id=counter["next"], **data.model_dump())
    db[todo.id] = todo
    counter["next"] += 1
    return todo

@app.get("/todos/{todo_id}", tags=["todos"])
def read_todo(todo: TodoDep) -> Todo:
    return todo

@app.put("/todos/{todo_id}", tags=["todos"])
def replace_todo(todo: TodoDep, data: TodoCreate) -> Todo:
    new = Todo(id=todo.id, **data.model_dump())
    db[todo.id] = new
    return new

@app.patch("/todos/{todo_id}", tags=["todos"])
def update_todo(todo: TodoDep, data: TodoUpdate) -> Todo:
    changes = data.model_dump(exclude_unset=True)    # only fields the client sent
    updated = todo.model_copy(update=changes)
    db[todo.id] = updated
    return updated

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["todos"])
def delete_todo(todo: TodoDep):
    del db[todo.id]


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
