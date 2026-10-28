from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome_email(email: str, name: str):
    # slow work: SMTP, writing logs, resizing an image...
    with open("emails.log", "a") as f:
        f.write(f"Welcome {name} -> {email}\n")

@app.post("/signup")
def signup(email: str, name: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_welcome_email, email, name)
    return {"message": "Signed up! Check your inbox soon."}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
