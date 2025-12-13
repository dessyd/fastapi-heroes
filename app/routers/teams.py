from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from .. import classes
from ..database import get_session

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=classes.TeamRead,
)
def create_team(
    *,
    session: Session = Depends(get_session),
    team: classes.TeamCreate,
):
    db_team = classes.Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.get("/", response_model=list[classes.TeamRead])
def read_teams(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    teams = session.exec(select(classes.Team).offset(offset).limit(limit)).all()
    return teams


@router.get("/{team_id}", response_model=classes.TeamReadWithHeroes)
def read_team(*, team_id: int, session: Session = Depends(get_session)):
    team = session.get(classes.Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


@router.patch("/{team_id}", response_model=classes.TeamRead)
def update_team(
    *,
    session: Session = Depends(get_session),
    team_id: int,
    team: classes.TeamUpdate,
):
    db_team = session.get(classes.Team, team_id)
    if not db_team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    team_data = team.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team = session.get(classes.Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    session.delete(team)
    session.commit()
    return {"ok": True}
