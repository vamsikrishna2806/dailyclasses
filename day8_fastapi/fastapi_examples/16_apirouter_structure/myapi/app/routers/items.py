# Not shown in the HTML (only users.py is) - a small router so app/main.py can include it.
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")                  # -> GET /v1/items/
def list_items():
    return [{"name": "laptop"}]

@router.get("/{item_id}")         # -> GET /v1/items/1
def get_item(item_id: int):
    return {"item_id": item_id}
