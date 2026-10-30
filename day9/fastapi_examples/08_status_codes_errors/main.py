from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()
items = {"apple": 1.5}

@app.get("/items/{name}")
def get_item(name: str):
    if name not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,     # same as 404, but readable
            detail=f"Item '{name}' not found",
            headers={"X-Error": "missing-item"},       # optional
        )
    return {"name": name, "price": items[name]}

@app.post("/items", status_code=status.HTTP_201_CREATED)   # change the success code
def create_item(name: str, price: float):
    items[name] = price
    return {"name": name}

# Your own exception + a global handler for it
class OutOfStock(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(OutOfStock)
async def out_of_stock_handler(request: Request, exc: OutOfStock):
    return JSONResponse(status_code=409, content={"error": f"{exc.name} is out of stock"})

@app.get("/buy/{name}")
def buy(name: str):
    raise OutOfStock(name)                              # -> 409 + friendly JSON


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
