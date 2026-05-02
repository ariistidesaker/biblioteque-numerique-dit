from pydantic import BaseModel
from .models import TypeUtilisateur

class UtilisateurBase(BaseModel):
    nom: str
    email: str
    type_utilisateur: TypeUtilisateur = TypeUtilisateur.etudiant

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurResponse(UtilisateurBase):
    id: int

    class Config:
        from_attributes = True
