from sqlalchemy import Column, Integer, String, Enum
import enum
from .database import Base

class TypeUtilisateur(str, enum.Enum):
    etudiant = "Etudiant"
    professeur = "Professeur"
    personnel = "Personnel"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mot_de_passe_hash = Column(String)
    type_utilisateur = Column(Enum(TypeUtilisateur), default=TypeUtilisateur.etudiant)
