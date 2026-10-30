from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/items")
def read_items(user_id: int, q: str | None = None, limit: int = 10):
    #           ^ path param   ^ optional query     ^ query with default
    return {"user_id": user_id, "q": q, "limit": limit}

@app.get("/search")
def search(term: str, in_stock: bool = False):   # term has no default = REQUIRED
    return {"term": term, "in_stock": in_stock}
    # in_stock accepts: true/false, 1/0, yes/no, on/off


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
