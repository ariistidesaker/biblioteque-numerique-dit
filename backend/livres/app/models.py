from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, index=True)
    auteur = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    exemplaires_totaux = Column(Integer, default=1)
    categorie = Column(String, default="Autre")
    disponible = Column(Boolean, default=True)
