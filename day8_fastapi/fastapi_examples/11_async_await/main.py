import asyncio
import time
import httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/async-wait")
async def good():
    await asyncio.sleep(2)              # non-blocking: others run meanwhile
    return {"done": True}

@app.get("/call-other-api")
async def call_other():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.github.com")
    return {"status": r.status_code}

@app.get("/sync-wait")
def also_fine():
    time.sleep(2)                       # blocking, but FastAPI runs plain `def`
    return {"done": True}               # in a thread pool, so it's still OK

@app.get("/BAD")
async def bad():
    time.sleep(2)                       # ❌ blocking call inside async def
    return {"oops": "froze the whole server for 2s"}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
