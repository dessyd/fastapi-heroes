from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from .. import classes
from ..database import get_session

router = APIRouter(
    prefix="/heroes",
    tags=["Heroes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=classes.HeroRead)
def create_hero(*, session: Session = Depends(get_session), hero: classes.HeroCreate):
    db_hero = classes.Hero.from_orm(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("/", response_model=List[classes.HeroRead])
def read_heroes(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    heroes = session.exec(select(classes.Hero).offset(offset).limit(limit)).all()
    return heroes


@router.get("/{hero_id}", response_model=classes.HeroReadWithTeam)
def read_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(classes.Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=classes.HeroRead)
def update_hero(*, session: Session = Depends(get_session), hero_id: int, hero: classes.HeroUpdate):
    db_hero = session.get(classes.Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    hero_data = hero.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(classes.Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
