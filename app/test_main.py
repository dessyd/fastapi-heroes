import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.classes import Hero
from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_hero(client: TestClient):
    response = client.post("/heroes/", json={"name": "Deadpond", "secret_name": "Dive Wilson"})
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "Deadpond"
    assert data["secret_name"] == "Dive Wilson"
    assert data["age"] is None
    assert data["id"] is not None


def test_create_hero_incomplete(client: TestClient):
    # No secret_name
    response = client.post("/heroes/", json={"name": "Deadpond"})
    assert response.status_code == 422


def test_create_hero_invalid(client: TestClient):
    # secret_name has an invalid type
    response = client.post(
        "/heroes/",
        json={
            "name": "Deadpond",
            "secret_name": {"message": "Do you wanna know my secret identity?"},
        },
    )
    assert response.status_code == 422


def test_read_heroes(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    session.add(hero_1)
    session.add(hero_2)
    session.commit()

    response = client.get("/heroes/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["name"] == hero_1.name
    assert data[0]["secret_name"] == hero_1.secret_name
    assert data[0]["age"] == hero_1.age
    assert data[0]["id"] == hero_1.id
    assert data[1]["name"] == hero_2.name
    assert data[1]["secret_name"] == hero_2.secret_name
    assert data[1]["age"] == hero_2.age
    assert data[1]["id"] == hero_2.id


def test_read_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero_1)
    session.commit()

    response = client.get(f"/heroes/{hero_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == hero_1.name
    assert data["secret_name"] == hero_1.secret_name
    assert data["age"] == hero_1.age
    assert data["id"] == hero_1.id


def test_update_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero_1)
    session.commit()

    response = client.patch(f"/heroes/{hero_1.id}", json={"name": "Deadpuddle"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Deadpuddle"
    assert data["secret_name"] == "Dive Wilson"
    assert data["age"] is None
    assert data["id"] == hero_1.id


def test_delete_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero_1)
    session.commit()

    response = client.delete(f"/heroes/{hero_1.id}")

    hero_in_db = session.get(Hero, hero_1.id)

    assert response.status_code == 204

    assert hero_in_db is None


# ============================================================================
# TEAM TESTS
# ============================================================================


def test_create_team(client: TestClient):
    response = client.post(
        "/teams/",
        json={"name": "Avengers", "headquarters": "New York"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "Avengers"
    assert data["headquarters"] == "New York"
    assert data["id"] is not None


def test_create_team_incomplete(client: TestClient):
    response = client.post("/teams/", json={"name": "Avengers"})
    assert response.status_code == 422


def test_read_teams(session: Session, client: TestClient):
    from app.classes import Team

    team_1 = Team(name="Avengers", headquarters="New York")
    team_2 = Team(name="X-Men", headquarters="Westchester")
    session.add(team_1)
    session.add(team_2)
    session.commit()

    response = client.get("/teams/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == team_1.name
    assert data[1]["name"] == team_2.name


def test_read_team(session: Session, client: TestClient):
    from app.classes import Team

    team_1 = Team(name="Avengers", headquarters="New York")
    session.add(team_1)
    session.commit()

    response = client.get(f"/teams/{team_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == team_1.name
    assert data["headquarters"] == team_1.headquarters
    assert data["id"] == team_1.id


def test_read_team_with_heroes(session: Session, client: TestClient):
    from app.classes import Team

    team_1 = Team(name="Avengers", headquarters="New York")
    hero_1 = Hero(name="Iron Man", secret_name="Tony Stark", team=team_1)
    session.add(team_1)
    session.add(hero_1)
    session.commit()

    response = client.get(f"/teams/{team_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == team_1.name
    assert len(data["heroes"]) == 1
    assert data["heroes"][0]["name"] == "Iron Man"


def test_update_team(session: Session, client: TestClient):
    from app.classes import Team

    team_1 = Team(name="Avengers", headquarters="New York")
    session.add(team_1)
    session.commit()

    response = client.patch(
        f"/teams/{team_1.id}",
        json={"name": "Avengers United"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Avengers United"
    assert data["headquarters"] == "New York"
    assert data["id"] == team_1.id


def test_delete_team(session: Session, client: TestClient):
    from app.classes import Team

    team_1 = Team(name="Avengers", headquarters="New York")
    session.add(team_1)
    session.commit()

    response = client.delete(f"/teams/{team_1.id}")

    team_in_db = session.get(Team, team_1.id)

    assert response.status_code == 204
    assert team_in_db is None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_get_hero_not_found(client: TestClient):
    response = client.get("/heroes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


def test_update_hero_not_found(client: TestClient):
    response = client.patch(
        "/heroes/999",
        json={"name": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


def test_delete_hero_not_found(client: TestClient):
    response = client.delete("/heroes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


def test_get_team_not_found(client: TestClient):
    response = client.get("/teams/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"


def test_update_team_not_found(client: TestClient):
    response = client.patch(
        "/teams/999",
        json={"name": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"


def test_delete_team_not_found(client: TestClient):
    response = client.delete("/teams/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"


# ============================================================================
# RELATIONSHIP TESTS
# ============================================================================


def test_create_hero_with_team(session: Session, client: TestClient):
    from app.classes import Team

    team = Team(name="Avengers", headquarters="New York")
    session.add(team)
    session.commit()

    response = client.post(
        "/heroes/",
        json={
            "name": "Iron Man",
            "secret_name": "Tony Stark",
            "team_id": team.id,
        },
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "Iron Man"


def test_read_hero_with_team_relationship(session: Session, client: TestClient):
    from app.classes import Team

    team = Team(name="Avengers", headquarters="New York")
    hero = Hero(name="Iron Man", secret_name="Tony Stark", team=team)
    session.add(team)
    session.add(hero)
    session.commit()

    response = client.get(f"/heroes/{hero.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Iron Man"
    assert data["team"] is not None
    assert data["team"]["name"] == "Avengers"


# ============================================================================
# PAGINATION TESTS
# ============================================================================


def test_read_heroes_with_offset(session: Session, client: TestClient):
    for i in range(5):
        hero = Hero(
            name=f"Hero{i}",
            secret_name=f"Secret{i}",
        )
        session.add(hero)
    session.commit()

    response = client.get("/heroes/?offset=2&limit=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == "Hero2"


def test_read_teams_with_limit(session: Session, client: TestClient):
    from app.classes import Team

    for i in range(5):
        team = Team(
            name=f"Team{i}",
            headquarters=f"Location{i}",
        )
        session.add(team)
    session.commit()

    response = client.get("/teams/?limit=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


# ============================================================================
# ROOT ENDPOINT TEST
# ============================================================================


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"
