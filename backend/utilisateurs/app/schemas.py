from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from .models import TypeUtilisateur, StatusUtilisateur


# SCHÉMAS DES SOUS-PROFILS

class EtudiantProfile(BaseModel):
    """Données spécifiques à un étudiant lors de la création."""
    numero_etudiant: Optional[str] = None
    filiere: Optional[str] = None
    niveau: Optional[str] = None   # L1, L2, L3, M1, M2

class ProfesseurProfile(BaseModel):
    """Données spécifiques à un professeur lors de la création."""
    specialite: Optional[str] = None
    departement: Optional[str] = None

class PersonnelProfile(BaseModel):
    """Données spécifiques au personnel lors de la création."""
    poste: Optional[str] = None
    departement: Optional[str] = None


# SCHÉMAS DE CRÉATION

class UtilisateurCreate(BaseModel):
    email: str
    numero_telephone: Optional[str] = None
    mot_de_passe: str
    nom_prenom: str
    type_utilisateur: TypeUtilisateur
    # Profil optionnel selon le type
    profil_etudiant:   Optional[EtudiantProfile]   = None
    profil_professeur: Optional[ProfesseurProfile] = None
    profil_personnel:  Optional[PersonnelProfile]  = None


# SCHÉMAS DE RÉPONSE

class EtudiantResponse(BaseModel):
    id_etudiant: UUID
    numero_etudiant: Optional[str]
    filiere: Optional[str]
    niveau: Optional[str]
    class Config:
        from_attributes = True

class ProfesseurResponse(BaseModel):
    id_professeur: UUID
    specialite: Optional[str]
    departement: Optional[str]
    class Config:
        from_attributes = True

class PersonnelResponse(BaseModel):
    id_personnel: UUID
    poste: Optional[str]
    departement: Optional[str]
    class Config:
        from_attributes = True

class UtilisateurResponse(BaseModel):
    id_utilisateur: UUID
    email: str
    numero_telephone: Optional[str]
    nom_prenom: str
    type_utilisateur: TypeUtilisateur
    status: StatusUtilisateur
    date_creation: datetime
    date_modification: Optional[datetime]
    # Sous-profils (null selon le type)
    etudiant:   Optional[EtudiantResponse]   = None
    professeur: Optional[ProfesseurResponse] = None
    personnel:  Optional[PersonnelResponse]  = None

    class Config:
        from_attributes = True


# SCHÉMA DE MISE À JOUR

class UtilisateurUpdate(BaseModel):
    nom_prenom: Optional[str] = None
    numero_telephone: Optional[str] = None
    status: Optional[StatusUtilisateur] = None
    profil_etudiant:   Optional[EtudiantProfile]   = None
    profil_professeur: Optional[ProfesseurProfile] = None
    profil_personnel:  Optional[PersonnelProfile]  = None
