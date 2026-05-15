from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base


class ModelTrainingHistory(Base):
    __tablename__ = "training_history"

    id                 = Column(Integer, primary_key=True, index=True)
    version            = Column(String, index=True)
    date_entrainement  = Column(DateTime, default=datetime.utcnow)
    status             = Column(String)   # "success" | "failed"
    metrics            = Column(Text, nullable=True)  # JSON sérialisé des métriques
