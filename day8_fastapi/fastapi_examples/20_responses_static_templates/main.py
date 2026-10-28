import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import (HTMLResponse, FileResponse, RedirectResponse,
                               StreamingResponse, PlainTextResponse)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # /static/logo.png
templates = Jinja2Templates(directory="templates")

@app.get("/hello", response_class=HTMLResponse)
def hello():
    return "<h1>Hello from FastAPI</h1>"

@app.get("/report")
def report():
    return FileResponse("report.pdf", filename="report.pdf")   # download

@app.get("/old")
def old():
    return RedirectResponse(url="/hello")

@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"

@app.get("/stream")
async def stream():
    async def words():
        for w in ["Fast", "API ", "streams ", "like ", "ChatGPT"]:
            yield w + " "
            await asyncio.sleep(0.3)
    return StreamingResponse(words(), media_type="text/plain")

@app.get("/page/{name}", response_class=HTMLResponse)
def page(request: Request, name: str):
    return templates.TemplateResponse(request, "page.html", {"name": name})


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
