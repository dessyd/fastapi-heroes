from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app import database

from .routers import heroes, teams


def create_db_and_tables():
    SQLModel.metadata.create_all(database.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Add cleanup logic here if needed


app = FastAPI(lifespan=lifespan)
app.include_router(heroes.router)
app.include_router(teams.router)


@app.get("/")
async def root():
    return {"version": "1.0.0"}
