import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Statut(str, enum.Enum):
    a_visiter = "a_visiter"
    visite = "visite"
    offre_faite = "offre_faite"
    abandonne = "abandonne"


class Bien(Base):
    __tablename__ = "biens"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200))
    ville: Mapped[str] = mapped_column(String(100))
    prix: Mapped[int]
    surface: Mapped[float]
    statut: Mapped[Statut] = mapped_column(Enum(Statut), default=Statut.a_visiter)
    url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
