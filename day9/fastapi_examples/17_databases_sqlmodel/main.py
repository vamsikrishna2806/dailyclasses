from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Hero(SQLModel, table=True):           # a TABLE and a Pydantic model
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = None

engine = create_engine("sqlite:///heroes.db", connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:        # one session per request
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)    # create tables at startup
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/heroes")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)                   # get the new id from the DB
    return hero

@app.get("/heroes")
def list_heroes(session: SessionDep, offset: int = 0, limit: int = 100) -> list[Hero]:
    return session.exec(select(Hero).offset(offset).limit(limit)).all()

@app.get("/heroes/{hero_id}")
def get_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(404, "Hero not found")
    return hero

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(404, "Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


# Run this file directly:  python main.py
# (same as: fastapi dev / uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
