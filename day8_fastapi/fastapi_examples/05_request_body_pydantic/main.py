from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

class User(BaseModel):
    name: str = Field(min_length=2)       # text, at least 2 characters
    age: int = Field(gt=0)                # whole number, greater than 0
    email: EmailStr                       # must look like an email
    is_active: bool = True                # optional, default True

@app.post("/users")
def create_user(user: User):              # a model type = read from the BODY
    print(user.name, user.age)            # real attributes, with autocomplete!
    return {"saved": user.model_dump()}   # model_dump() -> plain dict


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
