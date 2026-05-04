from pydantic import BaseModel
from typing import Optional


# SCHÉMA DE BASE
class LivreBase(BaseModel):
    titre: str
    auteur: str
    isbn: str
    description: Optional[str] = None


# CRÉATION
class LivreCreate(LivreBase):
    pass


# MISE À JOUR (tous les champs optionnels)
class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    auteur: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None


# RÉPONSE
class LivreResponse(LivreBase):
    id: int

    class Config:
        from_attributes = True
