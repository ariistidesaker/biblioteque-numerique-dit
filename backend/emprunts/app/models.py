from sqlalchemy import Column, Integer, DateTime, Boolean
from datetime import datetime
from .database import Base

class Emprunt(Base):
    __tablename__ = "emprunts"

    id = Column(Integer, primary_key=True, index=True)
    livre_id = Column(Integer, index=True)
    utilisateur_id = Column(Integer, index=True)
    date_emprunt = Column(DateTime, default=datetime.utcnow)
    date_retour_prevue = Column(DateTime)
    date_retour_effective = Column(DateTime, nullable=True)
    en_retard = Column(Boolean, default=False)
