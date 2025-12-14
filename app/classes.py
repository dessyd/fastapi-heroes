from sqlmodel import Field, Relationship, SQLModel


class TeamBase(SQLModel):
    """Base schema for Team API operations."""

    name: str = Field(index=True)
    headquarters: str


class Team(TeamBase, table=True):
    """Database model for Team table."""

    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    """Schema for creating a Team."""


class TeamRead(TeamBase):
    """Schema for reading a Team from API."""

    id: int


class TeamUpdate(SQLModel):
    """Schema for updating a Team."""

    id: int | None = None
    name: str | None = None
    headquarters: str | None = None


class HeroBase(SQLModel):
    """Base schema for Hero API operations (no DB-specific fields)."""

    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    """Database model for Hero table."""

    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")


class HeroCreate(HeroBase):
    """Schema for creating a Hero."""


class HeroRead(HeroBase):
    """Schema for reading a Hero from API."""

    id: int


class HeroUpdate(SQLModel):
    """Schema for updating a Hero."""

    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None


class HeroReadWithTeam(HeroRead):
    team: TeamRead | None = None


class TeamReadWithHeroes(TeamRead):
    heroes: list[HeroRead] = []
