from typing import Annotated
from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1, le=1000, title="The item ID")],
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    tags: Annotated[list[str], Query()] = [],     # ?tags=a&tags=b -> ["a", "b"]
):
    return {"item_id": item_id, "q": q, "page": page, "tags": tags}

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Laptop"])
    price: float = Field(gt=0, description="Price in USD")
    code: str = Field(pattern=r"^[A-Z]{3}-\d{3}$")   # like "ABC-123"
    tags: list[str] = []

@app.post("/products")
def add_product(product: Product, importance: Annotated[int, Body(ge=1, le=5)]):
    return {"product": product, "importance": importance}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
