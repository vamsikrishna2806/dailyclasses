from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
clients: list[WebSocket] = []

@app.websocket("/ws/{name}")
async def chat(websocket: WebSocket, name: str):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            for c in clients:              # broadcast to everyone
                await c.send_text(f"{name}: {text}")
    except WebSocketDisconnect:
        clients.remove(websocket)


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
