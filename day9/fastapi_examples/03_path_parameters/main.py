from enum import Enum
from fastapi import FastAPI

app = FastAPI()

# 1. Basic: the type hint converts + validates
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# 2. ORDER MATTERS: put fixed paths BEFORE variable ones
@app.get("/me")                       # fine, different path
def who_am_i():
    return {"user": "current user"}

@app.get("/files/me")                 # declared first, so it wins
def my_files():
    return {"owner": "me"}

@app.get("/files/{owner}")            # otherwise "me" would land here
def files_of(owner: str):
    return {"owner": owner}

# 3. Allowed values only: use an Enum (shows as a dropdown in /docs)
class Model(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"

@app.get("/models/{name}")
def get_model(name: Model):
    return {"model": name, "is_resnet": name is Model.resnet}

# 4. A path that contains slashes
@app.get("/download/{file_path:path}")
def download(file_path: str):
    return {"file": file_path}        # /download/docs/a/b.txt -> "docs/a/b.txt"


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
