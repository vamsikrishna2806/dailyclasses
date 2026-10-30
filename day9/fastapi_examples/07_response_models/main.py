from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

class UserIn(BaseModel):          # what the client SENDS
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):         # what the client GETS
    username: str
    email: EmailStr

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    # save to DB here...
    return user                   # password is stripped automatically!

# Modern style: the return type hint does the same job
@app.get("/users/{username}")
def get_user(username: str) -> UserOut:
    return UserOut(username=username, email=f"{username}@example.com")

# Useful options
@app.get("/items/{id}", response_model=UserOut, response_model_exclude_unset=True)
def item(id: int):
    ...                           # only send fields that were actually set


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
