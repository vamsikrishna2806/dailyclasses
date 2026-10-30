from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

SECRET_KEY = "change-me"          # real apps: long random value from an env variable
ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")   # adds the Authorize button in /docs

# never store plain passwords, only hashes
fake_users = {"asha": {"username": "asha", "hashed_password": password_hash.hash("secret")}}

app = FastAPI()

def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_users.get(form.username)
    if not user or not password_hash.verify(form.password, user["hashed_password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password")
    return {"access_token": create_token(user["username"]), "token_type": "bearer"}

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
    user = fake_users.get(payload.get("sub"))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user

@app.get("/users/me")
def read_me(user: Annotated[dict, Depends(get_current_user)]):
    return {"username": user["username"]}


# Run this file directly:  python auth_app.py
# (same as: fastapi dev / uvicorn auth_app:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("auth_app:app", host="127.0.0.1", port=8000, reload=True)
