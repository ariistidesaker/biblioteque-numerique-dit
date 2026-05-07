from pydantic import BaseModel
from typing import Optional


# SCHÉMA DE BASE
class LivreBase(BaseModel):
    titre: str
    auteur: str
    isbn: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    exemplaires_totaux: int = 1
    disponible: bool = True


# CRÉATION
class LivreCreate(LivreBase):
    pass


# MISE À JOUR (tous les champs optionnels)
class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    auteur: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    exemplaires_totaux: Optional[int] = None
    disponible: Optional[bool] = None


# RÉPONSE
class LivreResponse(LivreBase):
    id: int
    disponible: bool

    class Config:
        from_attributes = True
