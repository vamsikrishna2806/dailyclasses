from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")                  # -> GET /users/
def list_users():
    return [{"username": "asha"}]

@router.get("/{username}")        # -> GET /users/asha
def get_user(username: str):
    return {"username": username}
