"""
Day 7 - Task API built with FASTAPI.

It does exactly the same job as ../flask_app/app.py so you can compare
the two files line by line.

Run:   fastapi dev main.py        (or: uvicorn main:app --reload)
Open:  http://127.0.0.1:8000/docs  <- free interactive docs!
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Task API", version="1.0")


# The rules live in the type hints. FastAPI + Pydantic check them for you.
class TaskIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    priority: int = Field(default=3, ge=1, le=5)


class Task(TaskIn):
    id: int
    done: bool = False


tasks: list[Task] = []   # our "database" (a plain Python list in memory)
next_id = 1


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task_in: TaskIn) -> Task:
    global next_id
    task = Task(id=next_id, **task_in.model_dump())
    tasks.append(task)
    next_id += 1
    return task


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="task not found")


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail="task not found")
