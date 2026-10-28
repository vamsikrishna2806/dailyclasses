from typing import Annotated
from fastapi import FastAPI, Header, Cookie, Form, File, UploadFile, Response

app = FastAPI()

# HEADERS: user_agent reads the "User-Agent" header (_ becomes -)
@app.get("/whoami")
def whoami(user_agent: Annotated[str | None, Header()] = None,
           x_token: Annotated[str | None, Header()] = None):
    return {"browser": user_agent, "token": x_token}

# COOKIES: read one...
@app.get("/cart")
def cart(session_id: Annotated[str | None, Cookie()] = None):
    return {"session": session_id}

# ...and set one
@app.post("/login-cookie")
def set_cookie(response: Response):
    response.set_cookie(key="session_id", value="abc123", httponly=True)
    return {"ok": True}

# HTML FORMS (needs python-multipart, included in fastapi[standard])
@app.post("/login")
def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}

# FILE UPLOADS
@app.post("/upload")
async def upload(file: UploadFile):
    data = await file.read()
    return {"filename": file.filename, "type": file.content_type, "size": len(data)}

@app.post("/upload-many")
async def upload_many(files: list[UploadFile], note: Annotated[str, Form()] = ""):
    return {"names": [f.filename for f in files], "note": note}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
