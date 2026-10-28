from fastapi import FastAPI
from app.routers import users, items

app = FastAPI(title="My API")
app.include_router(users.router)
app.include_router(items.router, prefix="/v1")   # extra prefix


# Run this file directly:  python -m app.main   (run from the myapi folder)
# (same as: fastapi dev / uvicorn app.main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
