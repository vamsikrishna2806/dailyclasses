from fastapi import FastAPI

app = FastAPI()
books = {1: "Harry Potter"}

@app.get("/books/{book_id}")          # READ
def read_book(book_id: int):
    return {"id": book_id, "title": books.get(book_id)}

@app.post("/books")                   # CREATE
def create_book(title: str):
    new_id = max(books) + 1
    books[new_id] = title
    return {"id": new_id, "title": title}

@app.put("/books/{book_id}")          # REPLACE
def replace_book(book_id: int, title: str):
    books[book_id] = title
    return {"id": book_id, "title": title}

@app.delete("/books/{book_id}")       # DELETE
def delete_book(book_id: int):
    books.pop(book_id, None)
    return {"deleted": book_id}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
