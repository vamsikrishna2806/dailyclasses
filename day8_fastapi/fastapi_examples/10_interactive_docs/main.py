from fastapi import FastAPI

app = FastAPI(
    title="Todo API",
    description="Manage your todos. **Markdown** works here!",
    version="1.0.0",
    docs_url="/docs",          # set to None to hide Swagger UI
    redoc_url="/redoc",
)

@app.get(
    "/todos",
    tags=["todos"],                         # groups endpoints in the UI
    summary="List all todos",
    description="Returns every todo, newest last.",
    response_description="A list of todos",
)
def list_todos():
    """You can also write the description as a docstring."""
    return []

@app.get("/old-endpoint", deprecated=True, tags=["legacy"])
def old():
    return {}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
