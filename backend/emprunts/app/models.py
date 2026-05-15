import uuid
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base


class Emprunt(Base):
    __tablename__ = "emprunts"

    id                    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    livre_id              = Column(Integer, nullable=False, index=True)
    utilisateur_id        = Column(UUID(as_uuid=True), nullable=False, index=True)
    date_emprunt          = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_retour_prevue    = Column(DateTime, nullable=False)
    date_retour_effective = Column(DateTime, nullable=True)
    en_retard             = Column(Boolean, default=False, nullable=False)
