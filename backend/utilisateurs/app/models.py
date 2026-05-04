import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


# ENUMS

class TypeUtilisateur(str, enum.Enum):
    etudiant   = "ETUDIANT"
    professeur = "PROFESSEUR"
    personnel  = "PERSONNEL"
    admin      = "ADMIN"


class StatusUtilisateur(str, enum.Enum):
    actif      = "ACTIF"
    inactif    = "INACTIF"
    en_attente = "EN_ATTENTE"
    supprime   = "SUPPRIME"


# TABLE CENTRALE — Authentification

class Utilisateur(Base):
    """
    Table centrale de gestion de l'authentification et de l'identité.
    Chaque utilisateur est ensuite spécialisé via une sous-table
    (etudiant, professeur, personnel ou admin).
    """
    __tablename__ = "utilisateurs"

    id_utilisateur    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email             = Column(String, unique=True, nullable=False, index=True)
    numero_telephone  = Column(String, unique=True, nullable=True)
    mot_de_passe_hash = Column(Text, nullable=False)
    nom_prenom        = Column(String, nullable=False, index=True)
    type_utilisateur  = Column(Enum(TypeUtilisateur), nullable=False)
    status            = Column(Enum(StatusUtilisateur), default=StatusUtilisateur.actif, nullable=False)
    date_creation     = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations 1-to-1 vers les sous-profils
    etudiant   = relationship("Etudiant",   back_populates="utilisateur", uselist=False)
    professeur = relationship("Professeur", back_populates="utilisateur", uselist=False)
    personnel  = relationship("Personnel",  back_populates="utilisateur", uselist=False)
    admin      = relationship("Admin",      back_populates="utilisateur", uselist=False)


# SOUS-TABLE — Étudiant

class Etudiant(Base):
    """
    Profil spécifique à un étudiant.
    Contient les informations académiques complémentaires.
    """
    __tablename__ = "etudiants"

    id_etudiant      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_utilisateur   = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_utilisateur"), nullable=False, unique=True)
    numero_etudiant  = Column(String, unique=True, nullable=True)
    filiere          = Column(String, nullable=True)   # ex: "Informatique", "Big Data"
    niveau           = Column(String, nullable=True)   # ex: "L1", "L2", "M1", "M2"

    utilisateur = relationship("Utilisateur", back_populates="etudiant")


# SOUS-TABLE — Professeur

class Professeur(Base):
    """
    Profil spécifique à un professeur.
    """
    __tablename__ = "professeurs"

    id_professeur  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_utilisateur = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_utilisateur"), nullable=False, unique=True)
    specialite     = Column(String, nullable=True)   # ex: "Machine Learning", "Réseaux"
    departement    = Column(String, nullable=True)   # ex: "Informatique"

    utilisateur = relationship("Utilisateur", back_populates="professeur")


# SOUS-TABLE — Personnel

class Personnel(Base):
    """
    Profil spécifique au personnel administratif ou de bibliothèque.
    """
    __tablename__ = "personnels"

    id_personnel   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_utilisateur = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_utilisateur"), nullable=False, unique=True)
    poste          = Column(String, nullable=True)      # ex: "Bibliothécaire", "Administrateur"
    departement    = Column(String, nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="personnel")

# SOUS-TABLE — Admin

class Admin(Base):
    """
    Profil administrateur système.
    Accès complet à la plateforme.
    """
    __tablename__ = "admins"

    id_admin       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_utilisateur = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_utilisateur"), nullable=False, unique=True)

    utilisateur = relationship("Utilisateur", back_populates="admin")
