from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models import Statut


class BienBase(BaseModel):
    titre: str = Field(min_length=1, max_length=200)
    ville: str = Field(min_length=1, max_length=100)
    prix: int = Field(gt=0)
    surface: float = Field(gt=0)
    statut: Statut = Statut.a_visiter
    url: str | None = None
    notes: str | None = None


class BienCreate(BienBase):
    pass


class BienUpdate(BaseModel):
    titre: str | None = Field(default=None, min_length=1, max_length=200)
    ville: str | None = Field(default=None, min_length=1, max_length=100)
    prix: int | None = Field(default=None, gt=0)
    surface: float | None = Field(default=None, gt=0)
    statut: Statut | None = None
    url: str | None = None
    notes: str | None = None


class BienRead(BienBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cree_le: datetime

    @computed_field
    @property
    def prix_m2(self) -> float:
        return round(self.prix / self.surface, 2)
