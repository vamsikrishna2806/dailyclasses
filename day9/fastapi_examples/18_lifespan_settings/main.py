from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict   # pip install pydantic-settings

class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str = "sqlite:///app.db"
    secret_key: str                       # REQUIRED: must be in env or .env
    debug: bool = False
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache                                # read the file only once
def get_settings() -> Settings:
    return Settings()

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 starting: loading model...")
    ml_models["sentiment"] = lambda text: "positive" if "good" in text else "negative"
    yield                                 # ---- app is running here ----
    print("🛑 shutting down: cleaning up")
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
def predict(text: str):
    return {"label": ml_models["sentiment"](text)}

@app.get("/info")
def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {"app": settings.app_name, "debug": settings.debug}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
