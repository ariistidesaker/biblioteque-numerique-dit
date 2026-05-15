from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


# CRÉATION D'UN EMPRUNT
class EmpruntCreate(BaseModel):
    livre_id: int
    utilisateur_id: UUID
    date_retour_prevue: datetime


# RETOUR D'UN LIVRE
class RetourRequest(BaseModel):
    date_retour_effective: Optional[datetime] = None  # Si None, on prend datetime.utcnow()


# RÉPONSE EMPRUNT
class EmpruntResponse(BaseModel):
    id: int
    livre_id: int
    utilisateur_id: UUID
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effective: Optional[datetime]
    en_retard: bool

    class Config:
        from_attributes = True
