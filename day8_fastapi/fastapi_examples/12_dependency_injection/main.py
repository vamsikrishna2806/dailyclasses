from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Header

app = FastAPI()

# 1) Simple dependency: shared query parameters
def pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def list_items(page: Annotated[dict, Depends(pagination)]):
    return page                                   # /items?skip=20&limit=5

# 2) Dependency with cleanup: `yield`
def get_db():
    db = {"connected": True}                      # e.g. SessionLocal()
    try:
        yield db                                  # given to the endpoint
    finally:
        db["connected"] = False                   # runs AFTER the response: close it

# 3) Dependencies that use other dependencies
def get_token(authorization: Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(401, "Missing token")
    return authorization.removeprefix("Bearer ")

def get_current_user(db: Annotated[dict, Depends(get_db)],
                     token: Annotated[str, Depends(get_token)]):
    return {"name": "asha", "token": token}

# Tip: make a short alias and reuse it everywhere
CurrentUser = Annotated[dict, Depends(get_current_user)]

@app.get("/profile")
def read_profile(user: CurrentUser):
    return user

# 4) Run a dependency for its side effect only (no return value needed)
def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "secret":
        raise HTTPException(403, "Bad key")

@app.get("/admin", dependencies=[Depends(verify_key)])
def admin():
    return {"welcome": "admin"}

# 5) For the WHOLE app: FastAPI(dependencies=[Depends(verify_key)])


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
