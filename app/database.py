import os
from collections.abc import Generator

from sqlmodel import Session, create_engine

# Get database URL from environment, default to SQLite for local development
database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Configure connection arguments based on database type
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, echo=True, connect_args=connect_args)
else:
    # PostgreSQL or other database
    connect_args = {"pool_pre_ping": True}
    engine = create_engine(database_url, echo=True, connect_args=connect_args, pool_size=10)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
