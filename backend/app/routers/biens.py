from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bien, Statut
from app.schemas import BienCreate, BienRead, BienUpdate

router = APIRouter(prefix="/biens", tags=["biens"])

DB = Annotated[Session, Depends(get_db)]


def get_bien_or_404(db: Session, bien_id: int) -> Bien:
    bien = db.get(Bien, bien_id)
    if bien is None:
        raise HTTPException(status_code=404, detail="Bien introuvable")
    return bien


@router.get("", response_model=list[BienRead])
def lister_biens(db: DB, statut: Statut | None = None):
    query = select(Bien).order_by(Bien.id.desc())
    if statut:
        query = query.where(Bien.statut == statut)
    return db.scalars(query).all()


@router.get("/{bien_id}", response_model=BienRead)
def lire_bien(bien_id: int, db: DB):
    return get_bien_or_404(db, bien_id)


@router.post("", response_model=BienRead, status_code=status.HTTP_201_CREATED)
def creer_bien(data: BienCreate, db: DB):
    bien = Bien(**data.model_dump())
    db.add(bien)
    db.commit()
    db.refresh(bien)
    return bien


@router.patch("/{bien_id}", response_model=BienRead)
def modifier_bien(bien_id: int, data: BienUpdate, db: DB):
    bien = get_bien_or_404(db, bien_id)
    for champ, valeur in data.model_dump(exclude_unset=True).items():
        setattr(bien, champ, valeur)
    db.commit()
    db.refresh(bien)
    return bien


@router.delete("/{bien_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_bien(bien_id: int, db: DB):
    bien = get_bien_or_404(db, bien_id)
    db.delete(bien)
    db.commit()
