from fastapi import FastAPI
from sqlmodel import SQLModel

from app import database

from .routers import heroes, teams


def create_db_and_tables():
    SQLModel.metadata.create_all(database.engine)


app = FastAPI()
app.include_router(heroes.router)
app.include_router(teams.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"version": "1.0.0"}
